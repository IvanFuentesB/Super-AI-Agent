"""Manual Decision Queue New Item -- stdlib only, local only.

Reads a reviewed decision candidate from a local weekly review artifact
and writes a single draft queue entry to the manual decision queue JSONL.

Never posts, emails, sells, scrapes, calls external APIs, or touches live accounts.
All outputs are local draft records requiring human approval before any action.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_REVIEWS_ROOT = _REPO_ROOT / "05_logs" / "money_reviews"
_DEFAULT_QUEUE_PATH = (
    _REPO_ROOT / "14_context" / "money_workflows" / "manual_decision_queue.jsonl"
)

_ALLOWED_DECISION_TYPES = frozenset({
    "DOUBLE_DOWN",
    "ITERATE",
    "PAUSE",
    "KILL",
    "BUILD_NEXT",
    "CREATE_CONTENT_BATCH",
    "CREATE_LEAD_MAGNET",
    "REVIEW_LAUNCH_CHECKLIST",
    "COLLECT_MORE_DATA",
})

_ALLOWED_STATUSES = frozenset({
    "draft",
    "candidate",
    "accepted_for_manual_work",
    "in_progress",
    "completed",
    "paused",
    "killed",
    "superseded",
})

_ALLOWED_RISK_LEVELS = frozenset({"low", "medium", "high"})

# Phrases that signal a live/external/public action was requested.
_FORBIDDEN_PHRASES = (
    "post to ",
    "post on ",
    "auto-post",
    "autopost",
    "auto post",
    "send email",
    "cold email",
    "email outreach",
    "dm people",
    "send dm",
    "scrape ",
    "activate payment",
    "process payment",
    "log into account",
    "login to",
    "buy followers",
    "buy views",
    "buy comments",
    "bypass platform",
    "upload to ",
    "publish to ",
    "launch on ",
    "launch at ",
)

_SAFETY_FLAGS: dict = {
    "external_api_used": False,
    "scraping_enabled": False,
    "live_account_actions_enabled": False,
    "posting_enabled": False,
    "selling_enabled": False,
    "outreach_enabled": False,
    "payment_actions_enabled": False,
    "model_output_executed": False,
    "manual_review_required": True,
}


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _short_hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:6]


def _make_queue_item_id() -> str:
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    return f"qdec_{ts}_{_short_hash(ts)}"


def _find_latest_review_run(reviews_root: Path) -> Path | None:
    if not reviews_root.exists():
        return None
    runs = sorted(d for d in reviews_root.iterdir() if d.is_dir())
    return runs[-1] if runs else None


def _read_candidates_jsonl(
    path: Path,
) -> tuple[list[dict], list[str]]:
    candidates: list[dict] = []
    warnings: list[str] = []
    if not path.exists():
        warnings.append(f"MISSING candidates file: {path}")
        return candidates, warnings
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        warnings.append(f"ERROR reading {path}: {exc}")
        return candidates, warnings
    for i, raw in enumerate(text.splitlines(), 1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict):
                candidates.append(obj)
            else:
                warnings.append(f"SKIP non-object on line {i}")
        except json.JSONDecodeError as exc:
            warnings.append(f"SKIP malformed JSONL line {i}: {exc}")
    return candidates, warnings


def _check_forbidden_action(text: str) -> str | None:
    lower = text.lower()
    for phrase in _FORBIDDEN_PHRASES:
        if phrase in lower:
            return phrase
    return None


def _build_queue_entry(
    candidate: dict,
    source_file: str,
    run_id: str,
) -> tuple[dict, list[str]]:
    errors: list[str] = []

    decision_type = (candidate.get("category") or candidate.get("decision_type") or "").strip()
    if not decision_type:
        errors.append("MISSING decision_type / category in candidate")
    elif decision_type not in _ALLOWED_DECISION_TYPES:
        errors.append(
            f"INVALID decision_type '{decision_type}' — "
            f"allowed: {sorted(_ALLOWED_DECISION_TYPES)}"
        )

    recommendation = (
        candidate.get("recommendation") or candidate.get("category") or ""
    ).strip()
    reason = (candidate.get("rationale") or candidate.get("reason") or "").strip()
    if not recommendation:
        errors.append("MISSING recommendation in candidate")
    if not reason:
        errors.append("MISSING rationale / reason in candidate")

    next_action = (
        candidate.get("next_local_step") or candidate.get("next_manual_action") or ""
    ).strip()
    if not next_action:
        errors.append("MISSING next_local_step / next_manual_action in candidate")
    else:
        hit = _check_forbidden_action(next_action)
        if hit:
            errors.append(
                f"next_manual_action contains forbidden phrase '{hit}' — "
                "no posting, selling, outreach, payment, scraping, upload, launch, or login"
            )

    risk_level = (candidate.get("risk_level") or "low").strip().lower()
    if risk_level not in _ALLOWED_RISK_LEVELS:
        errors.append(
            f"INVALID risk_level '{risk_level}' — allowed: {sorted(_ALLOWED_RISK_LEVELS)}"
        )

    if errors:
        return {}, errors

    raw_files = candidate.get("files") or []
    safe_files: list[str] = []
    for f in raw_files:
        f_str = str(f)
        if f_str.startswith(("http://", "https://", "//", "\\\\", "ftp://")):
            errors.append(
                f"FILE path '{f_str}' looks non-local — only repo-relative paths allowed"
            )
        else:
            safe_files.append(f_str)
    if errors:
        return {}, errors

    entry: dict = {
        "queue_item_id": _make_queue_item_id(),
        "created_at": _utc_now(),
        "source_type": "weekly_review_candidate",
        "source_review_run_id": run_id,
        "source_decision_id": candidate.get("decision_id", ""),
        "source_file": source_file,
        "title": (candidate.get("title") or "").strip(),
        "category": decision_type,
        "decision_type": decision_type,
        "recommendation": recommendation,
        "rationale": reason,
        "reason": reason,
        "risk_level": risk_level,
        "next_local_step": next_action,
        "next_manual_action": next_action,
        "blocked_reason": (candidate.get("blocked_reason") or "").strip(),
        "human_review_note": "Pending human review -- not approved for any live action.",
        "linked_experiment_id": (
            candidate.get("source") or candidate.get("experiment_id") or None
        ),
        "linked_product_id": None,
        "deadline_optional": None,
        "approval_required": True,
        "status": "draft",
        "public_or_money_facing": False,
        "public_action_allowed": False,
        "live_account_action_allowed": False,
        "external_action_allowed": False,
        "model_output_executed": False,
        "artifact_only": True,
        "no_live_action_taken": True,
        "safety_flags": dict(_SAFETY_FLAGS),
        "metrics_snapshot": {
            "impressions": 0,
            "clicks": 0,
            "opt_ins": 0,
            "sales": 0,
            "revenue_usd": 0,
        },
        "files": safe_files,
    }
    return entry, []


def _validate_queue_jsonl(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return errors
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"ERROR reading queue file: {exc}")
        return errors
    for i, raw in enumerate(text.splitlines(), 1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
            if not isinstance(obj, dict):
                errors.append(f"Queue line {i}: non-object JSON")
        except json.JSONDecodeError as exc:
            errors.append(f"Queue line {i}: malformed JSONL: {exc}")
    return errors


def _run(args: argparse.Namespace) -> int:
    reviews_root = Path(args.reviews_root)
    queue_path = Path(args.queue_path)
    dry_run: bool = args.dry_run
    do_append: bool = args.append

    if not dry_run and not do_append:
        print("[INFO] Neither --dry-run nor --append specified. Defaulting to --dry-run.")
        dry_run = True

    run_dir = _find_latest_review_run(reviews_root)
    if run_dir is None:
        print(
            f"[ERROR] No review run directories found under: {reviews_root}",
            file=sys.stderr,
        )
        print(
            "[INFO]  Run weekly_money_review.py first, or pass --reviews-root to a temp path."
        )
        return 1

    run_id = run_dir.name
    decisions_jsonl = run_dir / "decisions_recommended.jsonl"
    try:
        source_file = str(decisions_jsonl.relative_to(_REPO_ROOT)).replace("\\", "/")
    except ValueError:
        source_file = str(decisions_jsonl).replace("\\", "/")

    candidates, warnings = _read_candidates_jsonl(decisions_jsonl)
    for w in warnings:
        print(f"[WARN] {w}")

    if not candidates:
        print(
            f"[ERROR] No candidates found in: {decisions_jsonl}",
            file=sys.stderr,
        )
        return 1

    # Select candidate
    if args.candidate_id:
        matched = [c for c in candidates if c.get("decision_id") == args.candidate_id]
        if not matched:
            ids = [c.get("decision_id") for c in candidates]
            print(
                f"[ERROR] --candidate-id '{args.candidate_id}' not found in {decisions_jsonl}",
                file=sys.stderr,
            )
            print(f"[INFO]  Available IDs: {ids}")
            return 1
        candidate = matched[0]
    elif args.index is not None:
        idx = args.index - 1
        if idx < 0 or idx >= len(candidates):
            print(
                f"[ERROR] --index {args.index} out of range (valid: 1..{len(candidates)})",
                file=sys.stderr,
            )
            return 1
        candidate = candidates[idx]
    else:
        candidate = candidates[0]

    entry, errors = _build_queue_entry(candidate, source_file, run_id)

    if errors:
        print("[ERROR] Candidate validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    entry_json = json.dumps(entry, ensure_ascii=False)

    if dry_run:
        print(f"[DRY-RUN] reviews_root:   {reviews_root}")
        print(f"[DRY-RUN] run_id:         {run_id}")
        print(f"[DRY-RUN] source_file:    {source_file}")
        print(f"[DRY-RUN] candidates:     {len(candidates)}")
        cand_id = candidate.get("decision_id", "?")
        cand_title = candidate.get("title", "?")
        print(f"[DRY-RUN] selected:       {cand_id} -- {cand_title}")
        print(f"[DRY-RUN] queue_path:     {queue_path}")
        print(f"[DRY-RUN] status:         draft  approval_required=true  no_live_action=true")
        print("[DRY-RUN] Generated entry:")
        print(json.dumps(entry, indent=2, ensure_ascii=False))
        print("[DRY-RUN] No files written.")
        return 0

    # Pre-append queue validation
    pre_errors = _validate_queue_jsonl(queue_path)
    if pre_errors:
        print("[ERROR] Existing queue file has JSONL errors (pre-append):", file=sys.stderr)
        for e in pre_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    queue_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with queue_path.open("a", encoding="utf-8") as fh:
            fh.write(entry_json + "\n")
    except OSError as exc:
        print(f"[ERROR] Failed to append to queue: {exc}", file=sys.stderr)
        return 1

    # Post-append validation
    post_errors = _validate_queue_jsonl(queue_path)
    if post_errors:
        print("[ERROR] Queue file has JSONL errors after append:", file=sys.stderr)
        for e in post_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"[APPEND] Written to:          {queue_path}")
    print(f"[APPEND] queue_item_id:       {entry['queue_item_id']}")
    print(f"[APPEND] source_decision_id:  {entry['source_decision_id']}")
    print(f"[APPEND] title:               {entry['title']}")
    print(f"[APPEND] decision_type:       {entry['decision_type']}")
    print(f"[APPEND] status:              {entry['status']}  approval_required=true")
    print(f"[APPEND] no_live_action_taken: true")
    return 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Manual Decision Queue New Item -- local only, stdlib only.\n"
            "\n"
            "Reads a weekly review decision candidate and writes a draft queue entry.\n"
            "Never posts, sells, emails, scrapes, calls external APIs, or touches live accounts.\n"
            "All outputs require human approval before any action.\n"
            "\n"
            "Examples:\n"
            "  python 03_scripts/manual_decision_queue_new_item.py --latest --dry-run\n"
            "  python 03_scripts/manual_decision_queue_new_item.py --latest --index 1 --dry-run\n"
            "  python 03_scripts/manual_decision_queue_new_item.py --latest --index 1 --append\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    p.add_argument(
        "--latest",
        action="store_true",
        help="Use the latest review run (default behavior; always selects newest run).",
    )

    sel = p.add_mutually_exclusive_group()
    sel.add_argument(
        "--candidate-id",
        metavar="ID",
        help="Select candidate by decision_id field.",
    )
    sel.add_argument(
        "--index",
        type=int,
        metavar="N",
        help="Select candidate by 1-based index within the run.",
    )

    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated queue entry without writing any files (default if neither specified).",
    )
    mode.add_argument(
        "--append",
        action="store_true",
        help="Append the generated entry to the queue JSONL file.",
    )

    p.add_argument(
        "--reviews-root",
        default=str(_DEFAULT_REVIEWS_ROOT),
        metavar="PATH",
        help=(
            "Root directory for weekly review artifacts. "
            f"Default: {_DEFAULT_REVIEWS_ROOT}"
        ),
    )
    p.add_argument(
        "--queue-path",
        default=str(_DEFAULT_QUEUE_PATH),
        metavar="PATH",
        help=(
            "Path to manual decision queue JSONL. "
            f"Default: {_DEFAULT_QUEUE_PATH}"
        ),
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    return _run(args)


if __name__ == "__main__":
    sys.exit(main())
