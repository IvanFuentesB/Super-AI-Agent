#!/usr/bin/env python3
"""Gemma Compact Memory Worker — stdlib-only, local Ollama only, DRAFT output, no canonical writes."""
import argparse
import datetime
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
LOGS_DIR = REPO_ROOT / "05_logs" / "gemma_compact_runs"
COMPACT_MEMORY_DIR = REPO_ROOT / "14_context" / "compact_memory"

SECRET_PATTERNS = frozenset([
    ".env", "secret", "credential", "token", "key", "password"
])

DEFAULT_MAX_CHARS = 12000
PREFERRED_MODEL = "gemma3:4b"

COMPRESS_PROMPT_TEMPLATE = (
    "You are a compact memory summarizer. Read the following content and produce a concise summary "
    "that preserves key facts, decisions, and blockers. Output only the summary, no preamble.\n\n"
    "CONTENT:\n{content}\n\nSUMMARY:"
)


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _run(cmd, cwd=None, timeout=10, input_text=None):
    try:
        input_bytes = input_text.encode("utf-8") if input_text else None
        r = subprocess.run(
            cmd, capture_output=True,
            cwd=str(cwd or REPO_ROOT), timeout=timeout,
            input=input_bytes
        )
        stdout = (r.stdout or b"").decode("utf-8", errors="replace").strip()
        stderr = (r.stderr or b"").decode("utf-8", errors="replace").strip()
        return stdout, stderr, r.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1
    except Exception as e:
        return "", "ERROR: " + str(e), -1


def _is_secret_path(p: pathlib.Path) -> bool:
    name_lower = p.name.lower()
    for pat in SECRET_PATTERNS:
        if pat in name_lower:
            return True
    return False


def _validate_input_path(raw_path: str) -> pathlib.Path:
    p = (REPO_ROOT / raw_path).resolve()
    try:
        p.relative_to(REPO_ROOT)
    except ValueError:
        raise ValueError(f"Path escapes repo root: {raw_path}")
    if _is_secret_path(p):
        raise ValueError(f"Refused: path looks like a secret file: {p.name}")
    return p


def _check_ollama():
    ver, _, rc = _run(["ollama", "--version"])
    if rc != 0:
        return None, None
    models_out, _, mrc = _run(["ollama", "list"])
    if mrc != 0:
        return ver, []
    lines = [l for l in models_out.splitlines() if l.strip() and not l.startswith("NAME")]
    model_names = []
    for line in lines:
        parts = line.split()
        if parts:
            model_names.append(parts[0])
    return ver, model_names


def _pick_model(model_names):
    for m in model_names:
        if "gemma" in m.lower():
            return m
    return None


def cmd_status(args):
    print("=== Gemma Compact Memory Worker Status ===")
    print(f"Repo root     : {REPO_ROOT}")
    print(f"Compact memory: {COMPACT_MEMORY_DIR}")
    if COMPACT_MEMORY_DIR.exists():
        files = list(COMPACT_MEMORY_DIR.glob("*.md"))
        print(f"Memory files  : {len(files)}")
    else:
        print("Memory files  : directory MISSING")

    ver, models = _check_ollama()
    if ver is None:
        print("Ollama        : NOT FOUND")
        print("Gemma model   : UNAVAILABLE")
        print("Recommendation: Install Ollama from https://ollama.com; then: ollama pull gemma3:4b")
    else:
        print(f"Ollama        : FOUND — {ver}")
        print(f"Models        : {models if models else '(none)'}")
        picked = _pick_model(models or [])
        print(f"Gemma model   : {picked if picked else 'NOT FOUND — run: ollama pull gemma3:4b'}")
    print("=== End Status ===")


def cmd_compress(args):
    input_path_raw = args.input
    if not input_path_raw:
        print("ERROR: --input PATH required")
        sys.exit(1)

    try:
        input_path = _validate_input_path(input_path_raw)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    content = input_path.read_text(encoding="utf-8")
    max_chars = args.max_chars
    if len(content) > max_chars:
        content = content[:max_chars]
        print(f"NOTE: Input truncated to {max_chars} chars")

    ts = _utc_now()
    run_id = "gemma_compress_" + ts
    out_dir_base = pathlib.Path(args.output_dir) if args.output_dir else LOGS_DIR
    out_dir = out_dir_base / run_id

    rel_input = input_path.relative_to(REPO_ROOT)

    if args.dry_run and not args.apply:
        print(f"[DRY RUN] Input      : {rel_input} ({len(content)} chars)")
        print(f"[DRY RUN] Output dir : 05_logs/gemma_compact_runs/{run_id}/")
        print(f"[DRY RUN] Model      : {PREFERRED_MODEL} (if available)")
        print("[DRY RUN] Pass --apply to run compression.")
        return

    # Check Ollama
    ver, models = _check_ollama()
    if ver is None:
        print("ERROR: Ollama not found. Cannot compress. Recommend: Claude or Python route.")
        sys.exit(1)

    picked = _pick_model(models or [])
    if not picked:
        print("ERROR: No Gemma model found. Run: ollama pull gemma3:4b")
        sys.exit(1)

    prompt = COMPRESS_PROMPT_TEMPLATE.format(content=content)
    print(f"Running: ollama run {picked} (input: {rel_input})")
    summary_out, err_txt, rc = _run(
        ["ollama", "run", picked], input_text=prompt, timeout=120
    )

    if rc != 0:
        print(f"ERROR: ollama run failed (exit {rc}): {err_txt[:200]}")
        sys.exit(1)

    meta = {
        "run_id": run_id,
        "generated_at": ts,
        "model_used": picked,
        "input_path": str(rel_input),
        "input_chars": len(content),
        "output_chars": len(summary_out),
        "draft_only": True,
        "canonical": False,
        "human_review_required": True,
        "warning": "DRAFT_ONLY — NOT_CANONICAL — HUMAN_REVIEW_REQUIRED",
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "summary.md"
    meta_path = out_dir / "summary_meta.json"

    summary_content = (
        "<!-- DRAFT_ONLY | NOT_CANONICAL | HUMAN_REVIEW_REQUIRED -->\n"
        f"# Gemma Compression Draft — {ts}\n\n"
        f"**Source**: {rel_input}\n"
        f"**Model**: {picked}\n\n"
        "---\n\n"
        + summary_out + "\n"
    )
    summary_path.write_text(summary_content, encoding="utf-8")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Written (DRAFT): {summary_path.relative_to(REPO_ROOT)}")
    print(f"Written (meta) : {meta_path.relative_to(REPO_ROOT)}")
    print("IMPORTANT: This is DRAFT_ONLY. Do not promote to 14_context/compact_memory/ without human review.")
    print("NOTE: Generated logs are unstaged. Do not stage unless explicitly approved.")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Gemma Compact Memory Worker — local Ollama/Gemma draft compression only. "
            "DRAFT output. Never updates canonical memory. Human review required."
        )
    )
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--status", action="store_true", help="Check Ollama/Gemma availability")
    mode_group.add_argument("--compress", action="store_true", help="Compress an input file (--dry-run or --apply)")

    parser.add_argument("--input", metavar="PATH", help="Input file path (repo-relative or absolute)")
    parser.add_argument("--output-dir", metavar="PATH", help="Output directory (default: 05_logs/gemma_compact_runs/)")
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS, metavar="N",
                        help=f"Max input chars (default: {DEFAULT_MAX_CHARS})")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")

    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    elif args.compress:
        cmd_compress(args)


if __name__ == "__main__":
    main()
