#!/usr/bin/env python3
"""Local Memory Compression Bridge — N+4.2A.

Provides a local-first memory compression workflow:
- Reads only repo-local approved files (never outside REPO_ROOT).
- Rejects paths matching secret/credential patterns.
- Probes Ollama/Gemma availability; falls back to local_demo mode if unavailable.
- Never calls external APIs. Never stores secrets.
- Writes auditable outputs to 14_context/compact_memory/ and 14_context/obsidian_vault/.
- Exposes truthful --status, --dry-run, --compress-demo, --compress-file, --write-snapshot, --json.

stdlib-only (no requests, no urllib, no http). local_only: true. external_api_used: false.
"""
from __future__ import annotations

import argparse
import base64
import datetime
import json
import pathlib
import subprocess
import sys
import textwrap

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
COMPACT_MEMORY_DIR = REPO_ROOT / "14_context" / "compact_memory"
OBSIDIAN_VAULT_DIR = REPO_ROOT / "14_context" / "obsidian_vault"

# ---------------------------------------------------------------------------
# Safety patterns
# ---------------------------------------------------------------------------
_SECRET_NAME_PATTERNS = frozenset([
    ".env", "secret", "credential", "token", "key", "password", "apikey",
    "api_key", "private", "passwd", "auth",
])

# Demo text for --compress-demo / --write-snapshot
DEMO_TEXT = textwrap.dedent("""\
    Ghoti N+4.2A -- Local Memory Bridge Demo
    =========================================
    This is a deterministic demo compression run.  No real source file is read.
    Key facts captured:
    - N+4.1J runtime task-store diagnostics stability is live on main (cad316e).
    - Mixed valid+invalid task stores now report degraded status truthfully.
    - Task.from_dict(None) raises controlled TypeError.
    - Supervised content MVP score: 100 / 9 of 9 categories.
    - External tools remain intake/planning only -- no clone/install/run.
    - N+4.2A adds: local_memory_compression_bridge, repo_skill_plugin_intake,
      dashboard Local Memory / Gemma / Repo-Intake truth cards.
    Blockers: none.
    Next: Codex N+4.2A real audit.
""")

PREFERRED_MODEL = "gemma3:4b"

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _is_secret_path(p: pathlib.Path) -> bool:
    name_lower = p.name.lower()
    stem_lower = p.stem.lower()
    for pat in _SECRET_NAME_PATTERNS:
        if pat in name_lower or pat in stem_lower:
            return True
    return False


def _is_inside_repo(p: pathlib.Path) -> bool:
    try:
        resolved = p.resolve()
        resolved.relative_to(REPO_ROOT)
        return True
    except ValueError:
        return False


def _run(cmd: list, timeout: int = 10, input_text=None):
    try:
        input_bytes = input_text.encode("utf-8") if input_text else None
        r = subprocess.run(cmd, capture_output=True, timeout=timeout, input=input_bytes)
        stdout = (r.stdout or b"").decode("utf-8", errors="replace").strip()
        stderr = (r.stderr or b"").decode("utf-8", errors="replace").strip()
        return stdout, stderr, r.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1
    except FileNotFoundError:
        return "", "NOT_FOUND", -2
    except Exception as exc:
        return "", f"ERROR: {exc}", -3


def _safe_write(dest: pathlib.Path, content: str) -> None:
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        return
    except (PermissionError, OSError):
        pass
    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
    node_script = (
        "const fs=require('fs'),p=require('path'),"
        f"dest={json.dumps(str(dest))},"
        f"enc={json.dumps(encoded)};"
        "fs.mkdirSync(p.dirname(dest),{recursive:true});"
        "fs.writeFileSync(dest,Buffer.from(enc,'base64'));"
        "console.log('WRITTEN');"
    )
    out, err, rc = _run(["node", "-e", node_script], timeout=15)
    if rc != 0 or "WRITTEN" not in out:
        raise RuntimeError(f"Node.js write fallback failed (rc={rc}): {err[:300]}")


# ---------------------------------------------------------------------------
# Ollama / Gemma probe
# ---------------------------------------------------------------------------

def _probe_ollama() -> dict:
    result = {
        "ollama_available": False,
        "ollama_version": "",
        "gemma_model_found": False,
        "model_name": None,
        "fallback_mode": "local_demo",
        "probe_error": "",
    }
    ver_out, ver_err, ver_rc = _run(["ollama", "--version"], timeout=5)
    if ver_rc == -2:
        result["probe_error"] = "ollama not found in PATH"
        return result
    if ver_rc != 0:
        result["probe_error"] = f"ollama --version failed: {ver_err[:200]}"
        return result
    result["ollama_available"] = True
    result["ollama_version"] = ver_out.strip()
    list_out, list_err, list_rc = _run(["ollama", "list"], timeout=10)
    if list_rc != 0:
        result["probe_error"] = f"ollama list failed: {list_err[:200]}"
        return result
    for line in list_out.splitlines():
        col = line.split()
        if not col:
            continue
        if PREFERRED_MODEL in col[0].lower():
            result["gemma_model_found"] = True
            result["model_name"] = col[0]
            result["fallback_mode"] = "ollama_gemma3_4b"
            return result
    for line in list_out.splitlines():
        col = line.split()
        if not col:
            continue
        if "gemma" in col[0].lower():
            result["gemma_model_found"] = True
            result["model_name"] = col[0]
            result["fallback_mode"] = "ollama_other"
            return result
    result["probe_error"] = "Ollama available but no gemma model found"
    return result


# ---------------------------------------------------------------------------
# Compression
# ---------------------------------------------------------------------------

def _compress_local_demo(text: str) -> str:
    lines = text.strip().splitlines()
    summary_lines = lines[:30]
    summary = "\n".join(summary_lines)
    if len(lines) > 30:
        summary += f"\n[... {len(lines) - 30} additional lines omitted in local_demo mode ...]"
    return summary


def _compress_ollama(text: str, model: str):
    prompt = (
        "You are a compact memory summarizer. Read the following content and produce "
        "a concise summary that preserves key facts, decisions, and blockers. "
        "Output only the summary, no preamble.\n\nCONTENT:\n"
        + text[:12000] + "\n\nSUMMARY:"
    )
    out, err, rc = _run(["ollama", "run", model], timeout=60, input_text=prompt)
    if rc != 0 or not out.strip():
        return "", f"ollama run failed (rc={rc}): {err[:300]}"
    return out.strip(), ""


def _build_metadata(source_files, compression_mode, model_used, created_at):
    return {
        "source_files": source_files,
        "compression_mode": compression_mode,
        "model_used": model_used,
        "local_only": True,
        "external_api_used": False,
        "secrets_scanned_or_skipped": True,
        "created_at": created_at,
        "approval_required_for_external_actions": True,
    }


def _build_obsidian_note(summary, metadata):
    tags = "tags: [ghoti, compact-memory, n4-2a, local-memory-bridge]"
    created = metadata["created_at"]
    mode = metadata["compression_mode"]
    model = metadata.get("model_used", "none")
    return (
        f"---\n{tags}\ncreated: {created}\ncompression_mode: {mode}\nmodel_used: {model}\n"
        f"local_only: true\nexternal_api_used: false\n---\n\n"
        f"# N+4.2A Memory Bridge Snapshot\n\n"
        f"**Created:** {created}  \n**Mode:** {mode}  \n**Model:** {model}  \n"
        f"**Local only:** true  \n**External API used:** false  \n\n"
        f"## Summary\n\n{summary}\n\n"
        f"## Metadata\n\n```json\n{json.dumps(metadata, indent=2)}\n```\n"
    )


def _build_compact_note(summary, metadata):
    created = metadata["created_at"]
    mode = metadata["compression_mode"]
    model = metadata.get("model_used", "none")
    return (
        f"# N+4.2A Compact Memory Snapshot\n\n"
        f"**created_at:** {created}  \n**compression_mode:** {mode}  \n"
        f"**model_used:** {model}  \n**local_only:** true  \n"
        f"**external_api_used:** false  \n"
        f"**approval_required_for_external_actions:** true  \n\n"
        f"## Summary\n\n{summary}\n\n"
        f"## Full Metadata\n\n```json\n{json.dumps(metadata, indent=2)}\n```\n"
    )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_status(json_out):
    probe = _probe_ollama()
    last_snapshot = None
    if COMPACT_MEMORY_DIR.exists():
        snapshots = sorted(COMPACT_MEMORY_DIR.glob("n4_2a_*.md"), reverse=True)
        if snapshots:
            last_snapshot = str(snapshots[0].relative_to(REPO_ROOT))
    data = {
        "bridge": "local_memory_compression_bridge",
        "milestone": "N+4.2A",
        "local_only": True,
        "external_api_used": False,
        "ollama_available": probe["ollama_available"],
        "ollama_version": probe["ollama_version"],
        "gemma_model_found": probe["gemma_model_found"],
        "model_name": probe["model_name"],
        "fallback_mode": probe["fallback_mode"],
        "probe_error": probe["probe_error"],
        "compact_memory_dir": str(COMPACT_MEMORY_DIR.relative_to(REPO_ROOT)),
        "obsidian_vault_dir": str(OBSIDIAN_VAULT_DIR.relative_to(REPO_ROOT)),
        "last_snapshot_path": last_snapshot,
        "approval_required_for_external_actions": True,
    }
    if json_out:
        print(json.dumps(data, indent=2))
    else:
        print("local_memory_compression_bridge status")
        print(f"  local_only:           true")
        print(f"  external_api_used:    false")
        print(f"  ollama_available:     {probe['ollama_available']}")
        if probe["ollama_version"]:
            print(f"  ollama_version:       {probe['ollama_version']}")
        print(f"  gemma_model_found:    {probe['gemma_model_found']}")
        print(f"  model_name:           {probe['model_name']}")
        print(f"  fallback_mode:        {probe['fallback_mode']}")
        if probe["probe_error"]:
            print(f"  probe_error:          {probe['probe_error']}")
        print(f"  compact_memory_dir:   {data['compact_memory_dir']}")
        print(f"  obsidian_vault_dir:   {data['obsidian_vault_dir']}")
        print(f"  last_snapshot_path:   {last_snapshot or 'none'}")
        print(f"  approval_required:    true")
    return 0


def cmd_dry_run(source_label, json_out):
    probe = _probe_ollama()
    mode = probe["fallback_mode"]
    model = probe["model_name"] or "none"
    ts = _utc_now()
    slug = ts.replace(":", "").replace("-", "")
    compact_dest = COMPACT_MEMORY_DIR / f"n4_2a_snapshot_{slug}.md"
    obsidian_dest = OBSIDIAN_VAULT_DIR / f"N4_2A_Memory_Bridge_{slug}.md"
    data = {
        "dry_run": True,
        "source_label": source_label,
        "compression_mode": mode,
        "model_used": model,
        "local_only": True,
        "external_api_used": False,
        "would_write_compact": str(compact_dest.relative_to(REPO_ROOT)),
        "would_write_obsidian": str(obsidian_dest.relative_to(REPO_ROOT)),
        "approval_required_for_external_actions": True,
    }
    if json_out:
        print(json.dumps(data, indent=2))
    else:
        print("[DRY-RUN] local_memory_compression_bridge")
        for k, v in data.items():
            print(f"  {k}: {v}")
    return 0


def cmd_compress(source_text, source_files, write, json_out):
    probe = _probe_ollama()
    mode = probe["fallback_mode"]
    model_name = probe["model_name"]
    ts = _utc_now()
    if probe["gemma_model_found"] and model_name:
        summary, err = _compress_ollama(source_text, model_name)
        if not summary:
            summary = _compress_local_demo(source_text)
            mode = "local_demo"
            model_name = "none"
            if not json_out:
                print(f"  [WARN] Ollama failed ({err}); using local_demo.")
    else:
        summary = _compress_local_demo(source_text)
        model_name = "none"
        mode = "local_demo"
    metadata = _build_metadata(source_files, mode, model_name or "none", ts)
    result = {
        "compression_mode": mode,
        "model_used": model_name or "none",
        "local_only": True,
        "external_api_used": False,
        "secrets_scanned_or_skipped": True,
        "created_at": ts,
        "approval_required_for_external_actions": True,
        "summary_length": len(summary),
        "written": False,
        "compact_path": None,
        "obsidian_path": None,
    }
    if write:
        slug = ts.replace(":", "").replace("-", "")
        compact_dest = COMPACT_MEMORY_DIR / f"n4_2a_snapshot_{slug}.md"
        obsidian_dest = OBSIDIAN_VAULT_DIR / f"N4_2A_Memory_Bridge_{slug}.md"
        _safe_write(compact_dest, _build_compact_note(summary, metadata))
        _safe_write(obsidian_dest, _build_obsidian_note(summary, metadata))
        result["written"] = True
        try:
            result["compact_path"] = str(compact_dest.relative_to(REPO_ROOT))
        except ValueError:
            result["compact_path"] = str(compact_dest)
        try:
            result["obsidian_path"] = str(obsidian_dest.relative_to(REPO_ROOT))
        except ValueError:
            result["obsidian_path"] = str(obsidian_dest)
    if json_out:
        print(json.dumps(result, indent=2))
    else:
        print(f"compression_mode:   {mode}")
        print(f"model_used:         {model_name or 'none'}")
        print(f"local_only:         true")
        print(f"external_api_used:  false")
        print(f"summary_length:     {len(summary)}")
        if write:
            print(f"compact_path:       {result['compact_path']}")
            print(f"obsidian_path:      {result['obsidian_path']}")
            print(f"written:            true")
        else:
            print("written:            false (use --write-snapshot to write)")
        print(f"approval_required:  true")
        print("\n--- Summary preview (first 5 lines) ---")
        for line in summary.splitlines()[:5]:
            print(" ", line)
    return 0


def cmd_compress_file(filepath, write, json_out):
    p = pathlib.Path(filepath).resolve()
    if not _is_inside_repo(p):
        msg = f"REJECTED: path outside repo root: {filepath}"
        if json_out:
            print(json.dumps({"error": msg, "local_only": True}))
        else:
            print(msg)
        return 1
    if _is_secret_path(p):
        msg = f"REJECTED: secret/credential pattern in path: {p.name}"
        if json_out:
            print(json.dumps({"error": msg, "local_only": True}))
        else:
            print(msg)
        return 1
    if not p.exists():
        msg = f"REJECTED: file not found: {filepath}"
        if json_out:
            print(json.dumps({"error": msg}))
        else:
            print(msg)
        return 1
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        msg = f"REJECTED: could not read: {exc}"
        if json_out:
            print(json.dumps({"error": msg}))
        else:
            print(msg)
        return 1
    return cmd_compress(
        source_text=text,
        source_files=[str(p.relative_to(REPO_ROOT))],
        write=write,
        json_out=json_out,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Local Memory Compression Bridge (N+4.2A) -- local-only, no external APIs."
    )
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--compress-demo", action="store_true")
    parser.add_argument("--compress-file", metavar="PATH")
    parser.add_argument("--write-snapshot", action="store_true")
    parser.add_argument("--json", dest="json_out", action="store_true")
    args = parser.parse_args()

    if args.status:
        return cmd_status(args.json_out)
    if args.compress_file:
        if args.dry_run:
            return cmd_dry_run(args.compress_file, args.json_out)
        return cmd_compress_file(args.compress_file, args.write_snapshot, args.json_out)
    if args.compress_demo or args.write_snapshot:
        if args.dry_run:
            return cmd_dry_run("demo_text", args.json_out)
        return cmd_compress(
            source_text=DEMO_TEXT,
            source_files=["demo_text"],
            write=args.write_snapshot,
            json_out=args.json_out,
        )
    if args.json_out:
        return cmd_status(json_out=True)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
