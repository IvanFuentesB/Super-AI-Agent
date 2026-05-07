"""Local brain router — preview only.

Loads policy from 23_configs/local_brain_router_policy.example.json.
Runs one safe local task via ollama. Writes artifacts to
05_logs/local_brain_runs/<run_id>/. Does not call any external API.
Does not execute model output. Does not edit the repo from model output.
"""

from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
_POLICY_PATH = _REPO_ROOT / "23_configs" / "local_brain_router_policy.example.json"
_LOG_ROOT = _REPO_ROOT / "05_logs" / "local_brain_runs"

_PREVIEW_TASK_TYPE = "draft_checklist"
_PREVIEW_PROMPT = (
    "Create a 5 item checklist for validating a local-only AI agent task before execution."
)
_TIMEOUT_SECONDS = 120

_DEFAULT_MAX_CHARS = 12000
_ALLOWED_EXTENSIONS = {".md", ".txt", ".json", ".py", ".js", ".ps1"}
_VIDEO_MONEY_ALLOWED_EXT = frozenset({".md", ".txt"})
_MONEY_RUNS_ROOT = _REPO_ROOT / "05_logs" / "money_runs"
_CANDIDATE_ANCHOR_KEYS = frozenset({"workflow_type", "product_idea", "name"})

_COMPRESS_PROMPT_TEMPLATE = """\
You are a context-compression assistant. Read the excerpt below and produce a compact summary.

Return ONLY the following sections (no preamble, no commentary):

## SUMMARY
- (up to 10 bullet points — most important facts only)

## ACTIVE BLOCKERS
- (any blocked or stalled items; "none" if clear)

## NEXT ACTIONS
- (concrete next steps listed in priority order)

## DECISIONS / MEMORY WORTH PRESERVING
- (key decisions, constraints, or invariants a future session needs to know)

## FILES CITED
- (list exact repo-relative file paths mentioned in the text; one per line)

---

EXCERPT:
{excerpt}
"""


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ps_write(path: Path, text: str) -> None:
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    ps_path = str(path).replace("'", "''")
    ps_dir = str(path.parent).replace("'", "''")
    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-Command",
            (
                f"New-Item -ItemType Directory -Force -Path '{ps_dir}' | Out-Null; "
                f"[System.IO.File]::WriteAllBytes('{ps_path}', "
                f"[Convert]::FromBase64String('{encoded}'))"
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _write_artifact(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError:
        _ps_write(path, content)


def _load_policy() -> dict:
    if not _POLICY_PATH.exists():
        return {}
    try:
        return json.loads(_POLICY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[local_brain_router] WARNING: could not load policy: {exc}", file=sys.stderr)
        return {}


def _ensure_run_dir(run_dir: Path) -> None:
    try:
        run_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        ps_dir = str(run_dir).replace("'", "''")
        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                f"New-Item -ItemType Directory -Force -Path '{ps_dir}' | Out-Null",
            ],
            check=True,
            capture_output=True,
            text=True,
        )


def _strip_ansi(raw: bytes) -> bytes:
    return re.compile(rb"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])").sub(b"", raw)


def _run_ollama(provider: str, model: str, prompt: str) -> tuple[int, str, str]:
    cmd = [provider, "run", model, prompt]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=_TIMEOUT_SECONDS)
        exit_code = result.returncode
        stdout = _strip_ansi(result.stdout or b"").decode("utf-8", errors="replace").strip()
        stderr = _strip_ansi(result.stderr or b"").decode("utf-8", errors="replace").strip()
        return exit_code, stdout, stderr
    except FileNotFoundError:
        return 127, "", f"ERROR: '{provider}' not found on PATH."
    except subprocess.TimeoutExpired:
        return 1, "", f"ERROR: inference timed out after {_TIMEOUT_SECONDS}s."


def _safe_display(text: str) -> str:
    enc = sys.stdout.encoding or "utf-8"
    return text.encode(enc, errors="replace").decode(enc, errors="replace")


def run_preview(policy: dict) -> int:
    model = policy.get("default_local_model", "gemma3:4b")
    provider = policy.get("local_provider", "ollama")
    run_id = f"preview_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    run_dir = _LOG_ROOT / run_id
    _ensure_run_dir(run_dir)

    print(f"[local_brain_router] PREVIEW MODE — enabled=false, routing_mode=preview_only")
    print(f"[local_brain_router] provider={provider} model={model}")
    print(f"[local_brain_router] task_type={_PREVIEW_TASK_TYPE}")
    print(f"[local_brain_router] run_dir={run_dir.relative_to(_REPO_ROOT)}")
    print()

    request_data = {
        "run_id": run_id,
        "mode": "preview_only",
        "enabled": False,
        "provider": provider,
        "model": model,
        "task_type": _PREVIEW_TASK_TYPE,
        "prompt": _PREVIEW_PROMPT,
        "api_usage": "none",
        "timestamp_utc": _utc_now(),
    }
    _write_artifact(run_dir / "request.json", json.dumps(request_data, indent=2) + "\n")

    print(f"[local_brain_router] running: {provider} run {model} <prompt>")
    exit_code, stdout, stderr = _run_ollama(provider, model, _PREVIEW_PROMPT)

    if "not found on PATH" in stderr or "timed out" in stderr:
        print(f"[local_brain_router] ERROR: {stderr}", file=sys.stderr)
        _write_artifact(run_dir / "response.txt", f"{stderr}\n")
        _write_artifact(
            run_dir / "summary.md",
            f"# Local Brain Router Preview — {run_id}\n\nStatus: FAIL\nReason: {stderr}\n"
            f"API usage: none\nModel: {model}\n",
        )
        return 1

    response_text = stdout if stdout else f"(no stdout)\nstderr: {stderr}"
    _write_artifact(run_dir / "response.txt", response_text + "\n")

    status = "PASS" if exit_code == 0 else "FAIL"
    summary = (
        f"# Local Brain Router Preview — {run_id}\n\n"
        f"Date: {_utc_now()}\n"
        f"Status: {status}\n"
        f"Mode: preview_only (enabled=false)\n"
        f"Provider: {provider}\n"
        f"Model: {model}\n"
        f"Task type: {_PREVIEW_TASK_TYPE}\n"
        f"Exit code: {exit_code}\n"
        f"API usage: none\n"
        f"External calls: none\n"
        f"Model output executed: NO\n"
        f"Repo edits from model output: NO\n\n"
        f"## Prompt\n\n{_PREVIEW_PROMPT}\n\n"
        f"## Response\n\n{response_text}\n"
    )
    _write_artifact(run_dir / "summary.md", summary)

    print(f"[local_brain_router] exit_code={exit_code} status={status}")
    print()
    print("--- response ---")
    print(_safe_display(response_text))
    print("--- end ---")
    print()
    print(f"[local_brain_router] artifacts written to: {run_dir.relative_to(_REPO_ROOT)}")
    return exit_code


def _resolve_input_path(input_arg: str) -> tuple[Path | None, str]:
    """Resolve and validate input path. Returns (path, error_message)."""
    candidate = Path(input_arg)
    if not candidate.is_absolute():
        candidate = (_REPO_ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()

    # Must be inside repo root
    try:
        candidate.relative_to(_REPO_ROOT)
    except ValueError:
        return None, f"REJECTED: path is outside repo root: {input_arg}"

    if not candidate.exists():
        return None, f"REJECTED: file does not exist: {candidate}"

    if not candidate.is_file():
        return None, f"REJECTED: path is not a file: {candidate}"

    if candidate.suffix.lower() not in _ALLOWED_EXTENSIONS:
        return None, (
            f"REJECTED: file extension '{candidate.suffix}' not in allowed list "
            f"{sorted(_ALLOWED_EXTENSIONS)}"
        )

    return candidate, ""


def _read_excerpt(path: Path, max_chars: int) -> tuple[str, bool]:
    """Read file text, clip to max_chars. Returns (text, clipped)."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    # Reject binary-looking content (high ratio of non-printable non-whitespace)
    non_print = sum(1 for c in raw[:2000] if not c.isprintable() and c not in "\n\r\t")
    if len(raw) > 0 and non_print / min(len(raw), 2000) > 0.1:
        raise ValueError("File appears to contain binary or non-text content.")
    clipped = len(raw) > max_chars
    return raw[:max_chars], clipped


def run_compress_context(policy: dict, input_arg: str, max_chars: int) -> int:
    model = policy.get("default_local_model", "gemma3:4b")
    provider = policy.get("local_provider", "ollama")
    run_id = f"compress_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    run_dir = _LOG_ROOT / run_id
    _ensure_run_dir(run_dir)

    print(f"[local_brain_router] COMPRESS_CONTEXT — preview_only, no_external_api")
    print(f"[local_brain_router] provider={provider} model={model}")
    print(f"[local_brain_router] input={input_arg} max_chars={max_chars}")
    print(f"[local_brain_router] run_dir={run_dir.relative_to(_REPO_ROOT)}")
    print()

    input_path, err = _resolve_input_path(input_arg)
    if input_path is None:
        print(f"[local_brain_router] ERROR: {err}", file=sys.stderr)
        _write_artifact(
            run_dir / "run_summary.json",
            json.dumps({"run_id": run_id, "status": "FAIL", "reason": err,
                        "api_usage": "none", "timestamp_utc": _utc_now()}, indent=2) + "\n",
        )
        return 1

    try:
        excerpt, clipped = _read_excerpt(input_path, max_chars)
    except (OSError, ValueError) as exc:
        msg = str(exc)
        print(f"[local_brain_router] ERROR reading file: {msg}", file=sys.stderr)
        _write_artifact(
            run_dir / "run_summary.json",
            json.dumps({"run_id": run_id, "status": "FAIL", "reason": msg,
                        "api_usage": "none", "timestamp_utc": _utc_now()}, indent=2) + "\n",
        )
        return 1

    rel_input = str(input_path.relative_to(_REPO_ROOT))
    ext = input_path.suffix.lower()
    excerpt_filename = f"source_excerpt{ext if ext in {'.md', '.txt'} else '.txt'}"

    request_data = {
        "run_id": run_id,
        "mode": "preview_only",
        "enabled": False,
        "provider": provider,
        "model": model,
        "task_type": "compress_context",
        "input_file": rel_input,
        "input_chars_read": len(excerpt),
        "input_clipped": clipped,
        "max_chars": max_chars,
        "api_usage": "none",
        "external_calls": "none",
        "model_output_executed": False,
        "repo_edits_from_model": False,
        "timestamp_utc": _utc_now(),
    }
    _write_artifact(run_dir / "request.json", json.dumps(request_data, indent=2) + "\n")

    clip_note = f"\n\n[CLIPPED at {max_chars} chars — original file is larger]" if clipped else ""
    _write_artifact(run_dir / excerpt_filename, excerpt + clip_note)

    prompt = _COMPRESS_PROMPT_TEMPLATE.format(excerpt=excerpt + clip_note)

    print(f"[local_brain_router] input file : {rel_input}")
    print(f"[local_brain_router] chars read : {len(excerpt)}{' (clipped)' if clipped else ''}")
    print(f"[local_brain_router] running compression via {provider} run {model} ...")
    print()

    exit_code, stdout, stderr = _run_ollama(provider, model, prompt)

    if "not found on PATH" in stderr or "timed out" in stderr:
        print(f"[local_brain_router] ERROR: {stderr}", file=sys.stderr)
        _write_artifact(run_dir / "response.txt", f"{stderr}\n")
        _write_artifact(
            run_dir / "run_summary.json",
            json.dumps({"run_id": run_id, "status": "FAIL", "reason": stderr,
                        "api_usage": "none", "timestamp_utc": _utc_now()}, indent=2) + "\n",
        )
        return 1

    response_text = stdout if stdout else f"(no stdout)\nstderr: {stderr}"
    _write_artifact(run_dir / "response.txt", response_text + "\n")

    status = "PASS" if exit_code == 0 else "FAIL"
    run_summary = {
        "run_id": run_id,
        "status": status,
        "task_type": "compress_context",
        "input_file": rel_input,
        "input_chars_read": len(excerpt),
        "input_clipped": clipped,
        "max_chars": max_chars,
        "provider": provider,
        "model": model,
        "exit_code": exit_code,
        "api_usage": "none",
        "external_calls": "none",
        "model_output_executed": False,
        "repo_edits_from_model": False,
        "artifacts": [
            str((run_dir / "request.json").relative_to(_REPO_ROOT)),
            str((run_dir / excerpt_filename).relative_to(_REPO_ROOT)),
            str((run_dir / "response.txt").relative_to(_REPO_ROOT)),
            str((run_dir / "run_summary.json").relative_to(_REPO_ROOT)),
        ],
        "timestamp_utc": _utc_now(),
    }
    _write_artifact(run_dir / "run_summary.json", json.dumps(run_summary, indent=2) + "\n")

    print(f"[local_brain_router] exit_code={exit_code} status={status}")
    print()
    print("--- compression output ---")
    print(_safe_display(response_text))
    print("--- end ---")
    print()
    print(f"[local_brain_router] artifacts written to: {run_dir.relative_to(_REPO_ROOT)}")
    return exit_code


_VIDEO_TO_MONEY_PROMPT_TEMPLATE = """\
You are a business-extraction assistant. Read the notes below and produce a structured money-making idea analysis.

Return ONLY the following sections with exactly these headers (no preamble, no commentary outside sections):

## SOURCE SUMMARY
- (3-7 bullet points summarising the money/business idea from the source)

## PRODUCT IDEAS
(List 2-4 ideas. For each use this exact bullet format:)
- name: <product name>
- target_customer: <who buys this>
- pain_point: <what problem it solves>
- offer: <what is delivered>
- mvp_asset: <minimum asset to ship>
- price_test: <price range, e.g. $9-$27>
- time_to_ship: <e.g. 1 day, 1 week>
- risks: <key risks>
- distribution_channels: <comma-separated channels>

## CONTENT ANGLES
(List 2-4 angles. For each:)
- hook: <opening line or question>
- format: <short-form, long-form, thread, etc.>
- platform_fit: <TikTok, YouTube, Twitter/X, email, etc.>
- cta: <call to action>
- repurposing_options: <how to reuse this content across formats>

## EXPERIMENT CANDIDATES
(List 1-3 candidates. For each:)
- workflow_type: <digital_product|prompt_pack|video_to_business_system|email_lead_magnet>
- product_idea: <one sentence>
- target_customer: <who>
- pain_point: <pain>
- offer: <offer>
- next_action: <single most important next step>
- approval_required: true

## DISTRIBUTION PLAN
- channel_1: <name>
- strategy_1: <how to use it>
- channel_2: <name>
- strategy_2: <how to use it>
- channel_3: <name>
- strategy_3: <how to use it>
- email_list_angle: <how email list amplifies distribution>
- short_form_angle: <TikTok/Reels hook and angle>
- repurposing_angle: <how to repurpose content across channels>
- validation_metric: <how to measure if this is working>

## RISK REVIEW
- legal_tos_risk: <low|medium|high — description>
- claims_risk: <low|medium|high — description>
- fake_proof_risk: <low|medium|high — description>
- spam_fake_engagement_risk: <low|medium|high — description>
- live_account_risk: <low|medium|high — description>

---

NOTES:
{excerpt}
"""


def _parse_sections(response_text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []
    for line in response_text.splitlines():
        if line.startswith("## "):
            if current_key is not None:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = line[3:].strip()
            current_lines = []
        elif current_key is not None:
            current_lines.append(line)
    if current_key is not None:
        sections[current_key] = "\n".join(current_lines).strip()
    return sections


def _candidates_to_jsonl(candidates_text: str, run_id: str) -> str:
    entries: list[dict] = []
    current: dict[str, str] = {}
    parse_warnings: list[str] = []
    for raw_line in candidates_text.splitlines():
        line = raw_line.strip()
        if line.startswith("- ") and ": " in line[2:]:
            key, _, val = line[2:].partition(": ")
            norm_key = key.strip().lower().replace(" ", "_")
            # Split on repeated anchor key: new candidate started without a blank line
            if norm_key in _CANDIDATE_ANCHOR_KEYS and norm_key in current:
                parse_warnings.append(f"split on repeated anchor key '{norm_key}'")
                entries.append({"run_id": run_id, **current})
                current = {}
            current[norm_key] = val.strip()
        elif not line and current:
            entries.append({"run_id": run_id, **current})
            current = {}
    if current:
        entries.append({"run_id": run_id, **current})
    # Force approval_required to boolean True regardless of any model-emitted value
    for entry in entries:
        entry["approval_required"] = True
    if parse_warnings:
        for entry in entries:
            entry.setdefault("_parse_warnings", parse_warnings)
    if not entries:
        entries.append({
            "run_id": run_id,
            "raw_text": candidates_text[:2000],
            "approval_required": True,
            "note": "Could not parse structured candidates from response",
        })
    return "\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n"


def run_video_to_money(policy: dict, input_arg: str, max_chars: int) -> int:
    model = policy.get("default_local_model", "gemma3:4b")
    provider = policy.get("local_provider", "ollama")
    run_id = f"vm_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    run_dir = _MONEY_RUNS_ROOT / run_id
    _ensure_run_dir(run_dir)

    print("[local_brain_router] VIDEO_TO_MONEY — artifact_only, no_external_api, no_auto_post")
    print(f"[local_brain_router] provider={provider} model={model}")
    print(f"[local_brain_router] input={input_arg} max_chars={max_chars}")
    print(f"[local_brain_router] run_dir={run_dir.relative_to(_REPO_ROOT)}")
    print()

    input_path, err = _resolve_input_path(input_arg)
    if input_path is None:
        print(f"[local_brain_router] ERROR: {err}", file=sys.stderr)
        _write_artifact(
            run_dir / "run_summary.json",
            json.dumps({"run_id": run_id, "status": "FAIL", "reason": err,
                        "api_usage": "none", "timestamp_utc": _utc_now()}, indent=2) + "\n",
        )
        return 1

    if input_path.suffix.lower() not in _VIDEO_MONEY_ALLOWED_EXT:
        err = (
            f"REJECTED: video_to_money requires .md or .txt input, "
            f"got '{input_path.suffix}'"
        )
        print(f"[local_brain_router] ERROR: {err}", file=sys.stderr)
        _write_artifact(
            run_dir / "run_summary.json",
            json.dumps({"run_id": run_id, "status": "FAIL", "reason": err,
                        "api_usage": "none", "timestamp_utc": _utc_now()}, indent=2) + "\n",
        )
        return 1

    try:
        excerpt, clipped = _read_excerpt(input_path, max_chars)
    except (OSError, ValueError) as exc:
        msg = str(exc)
        print(f"[local_brain_router] ERROR reading file: {msg}", file=sys.stderr)
        _write_artifact(
            run_dir / "run_summary.json",
            json.dumps({"run_id": run_id, "status": "FAIL", "reason": msg,
                        "api_usage": "none", "timestamp_utc": _utc_now()}, indent=2) + "\n",
        )
        return 1

    rel_input = str(input_path.relative_to(_REPO_ROOT))
    clip_note = f"\n\n[CLIPPED at {max_chars} chars — original file is larger]" if clipped else ""
    excerpt_with_note = excerpt + clip_note

    request_data = {
        "run_id": run_id,
        "task_type": "video_to_money",
        "input_file": rel_input,
        "input_chars_read": len(excerpt),
        "input_clipped": clipped,
        "max_chars": max_chars,
        "provider": provider,
        "model": model,
        "api_usage": "none",
        "external_calls": "none",
        "model_output_executed": False,
        "auto_post": False,
        "auto_sell": False,
        "auto_email": False,
        "auto_commit_from_model": False,
        "timestamp_utc": _utc_now(),
    }
    _write_artifact(run_dir / "request.json", json.dumps(request_data, indent=2) + "\n")
    _write_artifact(run_dir / "source_excerpt.md", excerpt_with_note)

    prompt = _VIDEO_TO_MONEY_PROMPT_TEMPLATE.format(excerpt=excerpt_with_note)

    print(f"[local_brain_router] input file  : {rel_input}")
    print(f"[local_brain_router] chars read  : {len(excerpt)}{' (clipped)' if clipped else ''}")
    print(f"[local_brain_router] running video_to_money via {provider} run {model} ...")
    print()

    exit_code, stdout, stderr = _run_ollama(provider, model, prompt)

    if "not found on PATH" in stderr or "timed out" in stderr:
        print(f"[local_brain_router] ERROR: {stderr}", file=sys.stderr)
        _write_artifact(
            run_dir / "run_summary.json",
            json.dumps({"run_id": run_id, "status": "FAIL", "reason": stderr,
                        "api_usage": "none", "timestamp_utc": _utc_now()}, indent=2) + "\n",
        )
        return 1

    response_text = stdout if stdout else f"(no stdout)\nstderr: {stderr}"
    sections = _parse_sections(response_text)

    source_summary = sections.get("SOURCE SUMMARY", response_text)
    product_ideas = sections.get("PRODUCT IDEAS", "(not found in response)")
    content_angles = sections.get("CONTENT ANGLES", "(not found in response)")
    candidates_text = sections.get("EXPERIMENT CANDIDATES", "")
    distribution_plan = sections.get("DISTRIBUTION PLAN", "(not found in response)")
    risk_review = sections.get("RISK REVIEW", "(not found in response)")

    _write_artifact(
        run_dir / "source_summary.md",
        f"# Source Summary\n\nRun: {run_id}\nInput: {rel_input}\n\n{source_summary}\n",
    )
    _write_artifact(
        run_dir / "product_ideas.md",
        f"# Product Ideas\n\nRun: {run_id}\n\n{product_ideas}\n",
    )
    _write_artifact(
        run_dir / "content_angles.md",
        f"# Content Angles\n\nRun: {run_id}\n\n{content_angles}\n",
    )
    _write_artifact(
        run_dir / "experiment_candidates.jsonl",
        _candidates_to_jsonl(candidates_text, run_id),
    )
    _write_artifact(
        run_dir / "distribution_plan.md",
        f"# Distribution Plan\n\nRun: {run_id}\n\n{distribution_plan}\n",
    )
    _write_artifact(
        run_dir / "risk_review.md",
        f"# Risk Review\n\nRun: {run_id}\n\n{risk_review}\n",
    )

    artifact_names = [
        "request.json", "source_excerpt.md", "source_summary.md",
        "product_ideas.md", "content_angles.md", "experiment_candidates.jsonl",
        "distribution_plan.md", "risk_review.md", "run_summary.json",
    ]
    status = "PASS" if exit_code == 0 else "FAIL"
    run_summary = {
        "run_id": run_id,
        "status": status,
        "task_type": "video_to_money",
        "input_file": rel_input,
        "input_chars_read": len(excerpt),
        "input_clipped": clipped,
        "max_chars": max_chars,
        "provider": provider,
        "model": model,
        "exit_code": exit_code,
        "api_usage": "none",
        "external_calls": "none",
        "model_output_executed": False,
        "auto_post": False,
        "auto_sell": False,
        "auto_email": False,
        "auto_commit_from_model": False,
        "approval_required_for_any_use": True,
        "artifacts": [
            str((run_dir / name).relative_to(_REPO_ROOT)) for name in artifact_names
        ],
        "timestamp_utc": _utc_now(),
    }
    _write_artifact(run_dir / "run_summary.json", json.dumps(run_summary, indent=2) + "\n")

    print(f"[local_brain_router] exit_code={exit_code} status={status}")
    print()
    print("--- source summary ---")
    print(_safe_display(source_summary[:800]))
    if len(source_summary) > 800:
        print("... (truncated for display)")
    print("--- end ---")
    print()
    print(f"[local_brain_router] artifacts written to: {run_dir.relative_to(_REPO_ROOT)}")
    return exit_code


def _parse_args() -> dict:
    args = sys.argv[1:]
    result = {
        "preview": "--preview" in args,
        "task": None,
        "input": None,
        "max_chars": _DEFAULT_MAX_CHARS,
    }
    i = 0
    while i < len(args):
        if args[i] == "--task" and i + 1 < len(args):
            result["task"] = args[i + 1]
            i += 2
        elif args[i] == "--input" and i + 1 < len(args):
            result["input"] = args[i + 1]
            i += 2
        elif args[i] == "--max-chars" and i + 1 < len(args):
            try:
                result["max_chars"] = int(args[i + 1])
            except ValueError:
                print(f"[local_brain_router] WARNING: invalid --max-chars value, using default {_DEFAULT_MAX_CHARS}", file=sys.stderr)
            i += 2
        else:
            i += 1
    return result


def main() -> int:
    parsed = _parse_args()
    policy = _load_policy()

    if parsed["task"] == "compress_context":
        if not parsed["input"]:
            print("[local_brain_router] ERROR: --task compress_context requires --input <path>", file=sys.stderr)
            return 1
        return run_compress_context(policy, parsed["input"], parsed["max_chars"])

    if parsed["task"] == "video_to_money":
        if not parsed["input"]:
            print("[local_brain_router] ERROR: --task video_to_money requires --input <path>", file=sys.stderr)
            return 1
        return run_video_to_money(policy, parsed["input"], parsed["max_chars"])

    if parsed["preview"]:
        return run_preview(policy)

    print("[local_brain_router] No action specified.")
    print("  --preview                                run draft_checklist preview task")
    print("  --task compress_context --input <path>   compress a local markdown/text file")
    print("  --task video_to_money   --input <path>   extract money ideas from notes (.md/.txt only)")
    print("  --max-chars <number>                     clip input (default 12000)")
    print(f"  Policy: enabled={policy.get('enabled', False)}")
    print(f"  Routing mode: {policy.get('routing_mode', 'unknown')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
