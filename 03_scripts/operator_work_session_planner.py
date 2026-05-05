"""Operator Work Session Planner -- stdlib only, local only.

Reads the manual decision queue JSONL and produces a structured local work
session plan under 05_logs/operator_work_sessions/<run_id>/.

Never posts, emails, sells, scrapes, calls external APIs, or touches live accounts.
No model calls. No approval of queue items. Local draft artifacts only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_QUEUE_PATH = (
    _REPO_ROOT / "14_context" / "money_workflows" / "manual_decision_queue.jsonl"
)
_DEFAULT_SESSIONS_ROOT = _REPO_ROOT / "05_logs" / "operator_work_sessions"
_DEFAULT_MAX_TASKS = 3

_SAFE_LOCAL_STATUSES = frozenset({"draft", "candidate", "accepted_for_manual_work", "in_progress"})
_BLOCKED_STATUSES = frozenset({"paused", "killed", "superseded"})

_SAFE_LOCAL_CATEGORIES = frozenset({
    "ITERATE",
    "BUILD_NEXT",
    "CREATE_CONTENT_BATCH",
    "CREATE_LEAD_MAGNET",
    "REVIEW_LAUNCH_CHECKLIST",
    "COLLECT_MORE_DATA",
    "PAUSE",
})

_RISKY_CATEGORIES = frozenset({
    "DOUBLE_DOWN",
})

_REJECT_CATEGORIES = frozenset({
    "KILL",
})

_FORBIDDEN_PHRASES = (
    "post to ",
    "post on ",
    "auto-post",
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


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_id() -> str:
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    h = hashlib.sha256(ts.encode()).hexdigest()[:6]
    return f"session_{ts}_{h}"


def _has_forbidden_phrase(text: str) -> str | None:
    lower = text.lower()
    for phrase in _FORBIDDEN_PHRASES:
        if phrase in lower:
            return phrase
    return None


def _classify_item(item: dict) -> str:
    """Return one of: safe_local_work | needs_human_approval | blocked | reject_or_unsafe."""
    status = (item.get("status") or "").strip()
    if status in _BLOCKED_STATUSES:
        return "blocked"

    category = (item.get("category") or item.get("decision_type") or "").strip()
    if category in _REJECT_CATEGORIES:
        return "reject_or_unsafe"

    next_step = (item.get("next_local_step") or item.get("next_manual_action") or "").strip()
    if _has_forbidden_phrase(next_step):
        return "reject_or_unsafe"

    risk = (item.get("risk_level") or "low").strip().lower()
    if risk == "high" or category in _RISKY_CATEGORIES:
        return "needs_human_approval"

    if item.get("approval_required") is not False:
        return "needs_human_approval"

    if category in _SAFE_LOCAL_CATEGORIES and risk in ("low", "medium"):
        return "safe_local_work"

    return "needs_human_approval"


def _read_queue(queue_path: Path) -> tuple[list[dict], list[str]]:
    items: list[dict] = []
    warnings: list[str] = []
    if not queue_path.exists():
        warnings.append(f"Queue file not found: {queue_path}")
        return items, warnings
    try:
        text = queue_path.read_text(encoding="utf-8")
    except OSError as exc:
        warnings.append(f"Could not read queue file: {exc}")
        return items, warnings
    for i, raw in enumerate(text.splitlines(), 1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict):
                items.append(obj)
            else:
                warnings.append(f"Line {i}: non-object JSON, skipped")
        except json.JSONDecodeError as exc:
            warnings.append(f"Line {i}: malformed JSONL — {exc}")
    return items, warnings


def _build_task_plan(item: dict, classification: str) -> dict:
    title = (item.get("title") or item.get("queue_item_id") or "Untitled").strip()
    category = (item.get("category") or item.get("decision_type") or "").strip()
    risk = (item.get("risk_level") or "low").strip()
    next_step = (item.get("next_local_step") or item.get("next_manual_action") or "").strip()
    blocked_reason = (item.get("blocked_reason") or "").strip()
    recommendation = (item.get("recommendation") or "").strip()
    files = item.get("files") or []

    artifact_targets = [f for f in files if isinstance(f, str)] if files else []

    approval_questions: list[str] = []
    if classification == "needs_human_approval":
        approval_questions = [
            f"Is '{title}' safe to work on locally given risk_level={risk}?",
            "Does this item require any live account, external API, or public-facing action?",
            "Are the artifact targets listed below appropriate for local-only work?",
        ]

    risk_notes: list[str] = []
    if risk == "high":
        risk_notes.append("High risk: review manually before any local file changes.")
    if category in _RISKY_CATEGORIES:
        risk_notes.append(f"Category {category} requires extra human judgment.")
    if blocked_reason:
        risk_notes.append(f"Blocked reason: {blocked_reason}")

    validation_steps = [
        "Confirm item status is not 'killed' or 'superseded' before starting.",
        "Confirm all artifact targets are repo-relative paths (no external URLs).",
        "Confirm no posting, selling, emailing, scraping, or login is required.",
    ]

    return {
        "queue_item_id": item.get("queue_item_id", ""),
        "title": title,
        "category": category,
        "classification": classification,
        "risk_level": risk,
        "recommendation": recommendation,
        "next_local_step": next_step,
        "artifact_targets": artifact_targets,
        "validation_steps": validation_steps,
        "approval_questions": approval_questions,
        "risk_notes": risk_notes,
        "local_draft": True,
        "not_approval": True,
        "not_execution": True,
    }


def _build_plan(
    items: list[dict],
    warnings: list[str],
    max_tasks: int,
    queue_path: Path,
    run_id: str,
    dry_run: bool,
) -> dict:
    classified: list[tuple[str, dict]] = []
    for item in items:
        cls = _classify_item(item)
        classified.append((cls, item))

    safe_items = [i for c, i in classified if c == "safe_local_work"]
    approval_items = [i for c, i in classified if c == "needs_human_approval"]
    blocked_items = [i for c, i in classified if c == "blocked"]
    reject_items = [i for c, i in classified if c == "reject_or_unsafe"]

    # Prefer safe_local_work first, then needs_human_approval
    work_candidates = safe_items + approval_items
    top_items = work_candidates[:max_tasks]

    tasks = [_build_task_plan(item, _classify_item(item)) for item in top_items]

    session_root = _DEFAULT_SESSIONS_ROOT / run_id
    artifacts = {
        "work_session_plan.md": str(session_root / "work_session_plan.md"),
        "work_session_plan.json": str(session_root / "work_session_plan.json"),
        "source_index.json": str(session_root / "source_index.json"),
        "request.json": str(session_root / "request.json"),
    }

    return {
        "run_id": run_id,
        "generated_at": _utc_now(),
        "dry_run": dry_run,
        "queue_path": str(queue_path),
        "total_items": len(items),
        "classification_counts": {
            "safe_local_work": len(safe_items),
            "needs_human_approval": len(approval_items),
            "blocked": len(blocked_items),
            "reject_or_unsafe": len(reject_items),
        },
        "max_tasks": max_tasks,
        "top_tasks": tasks,
        "output_artifacts": artifacts,
        "session_root": str(session_root),
        "warnings": warnings,
        "local_draft": True,
        "not_approval": True,
        "not_execution": True,
        "safety_note": (
            "This plan is a local draft only. No queue items have been approved or executed. "
            "No live actions, external APIs, posting, selling, or account access."
        ),
    }


def _render_md(plan: dict) -> str:
    lines: list[str] = []
    lines.append("# Operator Work Session Plan")
    lines.append("")
    lines.append(f"**Run ID:** {plan['run_id']}")
    lines.append(f"**Generated:** {plan['generated_at']}")
    lines.append(f"**Queue:** {plan['queue_path']}")
    lines.append(f"**Total items in queue:** {plan['total_items']}")
    lines.append("")
    lines.append("> LOCAL DRAFT — not approval, not execution. No live actions.")
    lines.append("")

    cc = plan["classification_counts"]
    lines.append("## Classification Summary")
    lines.append("")
    lines.append(f"- safe_local_work: {cc.get('safe_local_work', 0)}")
    lines.append(f"- needs_human_approval: {cc.get('needs_human_approval', 0)}")
    lines.append(f"- blocked: {cc.get('blocked', 0)}")
    lines.append(f"- reject_or_unsafe: {cc.get('reject_or_unsafe', 0)}")
    lines.append("")

    tasks = plan.get("top_tasks") or []
    lines.append(f"## Top {len(tasks)} Local Tasks")
    lines.append("")
    if not tasks:
        lines.append("No eligible tasks found.")
    for idx, task in enumerate(tasks, 1):
        lines.append(f"### Task {idx}: {task['title']}")
        lines.append("")
        lines.append(f"- **Category:** {task['category']}")
        lines.append(f"- **Classification:** {task['classification']}")
        lines.append(f"- **Risk level:** {task['risk_level']}")
        lines.append(f"- **Recommendation:** {task['recommendation']}")
        lines.append(f"- **Next local step:** {task['next_local_step']}")
        lines.append("")
        if task.get("artifact_targets"):
            lines.append("**Artifact targets:**")
            for f in task["artifact_targets"]:
                lines.append(f"- `{f}`")
            lines.append("")
        lines.append("**Validation steps:**")
        for step in task.get("validation_steps") or []:
            lines.append(f"- {step}")
        lines.append("")
        if task.get("approval_questions"):
            lines.append("**Human approval questions:**")
            for q in task["approval_questions"]:
                lines.append(f"- {q}")
            lines.append("")
        if task.get("risk_notes"):
            lines.append("**Risk notes:**")
            for n in task["risk_notes"]:
                lines.append(f"- {n}")
            lines.append("")

    if plan.get("warnings"):
        lines.append("## Warnings")
        lines.append("")
        for w in plan["warnings"]:
            lines.append(f"- {w}")
        lines.append("")

    lines.append("## Output Artifacts")
    lines.append("")
    for name, artifact_path in (plan.get("output_artifacts") or {}).items():
        lines.append(f"- `{name}`: `{artifact_path}`")
    lines.append("")
    lines.append("---")
    lines.append(plan.get("safety_note", ""))
    lines.append("")
    return "\n".join(lines)


def _write_artifacts(plan: dict, session_root: Path) -> None:
    session_root.mkdir(parents=True, exist_ok=True)

    md_content = _render_md(plan)
    (session_root / "work_session_plan.md").write_text(md_content, encoding="utf-8")

    (session_root / "work_session_plan.json").write_text(
        json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    source_index = {
        "run_id": plan["run_id"],
        "generated_at": plan["generated_at"],
        "queue_path": plan["queue_path"],
        "total_items": plan["total_items"],
        "classification_counts": plan["classification_counts"],
    }
    (session_root / "source_index.json").write_text(
        json.dumps(source_index, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    request_doc = {
        "run_id": plan["run_id"],
        "generated_at": plan["generated_at"],
        "queue_path": plan["queue_path"],
        "max_tasks": plan["max_tasks"],
        "dry_run": plan["dry_run"],
        "local_draft": True,
        "not_approval": True,
        "not_execution": True,
    }
    (session_root / "request.json").write_text(
        json.dumps(request_doc, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _run(args: argparse.Namespace) -> int:
    queue_path = Path(args.queue_path)
    max_tasks: int = args.max_tasks
    dry_run: bool = args.dry_run

    items, warnings = _read_queue(queue_path)

    if not items and not warnings:
        warnings.append("Queue is empty.")

    run_id = _run_id()
    session_root = _DEFAULT_SESSIONS_ROOT / run_id

    plan = _build_plan(items, warnings, max_tasks, queue_path, run_id, dry_run)

    if dry_run:
        print("[DRY-RUN] Operator Work Session Planner")
        print(f"[DRY-RUN] queue_path:    {queue_path}")
        print(f"[DRY-RUN] total_items:   {len(items)}")
        print(f"[DRY-RUN] run_id:        {run_id}")
        print(f"[DRY-RUN] session_root:  {session_root}")
        print(f"[DRY-RUN] classification_counts: {plan['classification_counts']}")
        print(f"[DRY-RUN] top_tasks:     {len(plan['top_tasks'])}")
        if warnings:
            for w in warnings:
                print(f"[DRY-RUN][WARN] {w}")
        print("[DRY-RUN] Plan (JSON preview):")
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        print("[DRY-RUN] No files written.")
        return 0

    _write_artifacts(plan, session_root)
    print(f"[PLAN] session_root:          {session_root}")
    print(f"[PLAN] work_session_plan.md:  {session_root / 'work_session_plan.md'}")
    print(f"[PLAN] work_session_plan.json: {session_root / 'work_session_plan.json'}")
    print(f"[PLAN] source_index.json:     {session_root / 'source_index.json'}")
    print(f"[PLAN] request.json:          {session_root / 'request.json'}")
    print(f"[PLAN] total_items:           {len(items)}")
    print(f"[PLAN] top_tasks:             {len(plan['top_tasks'])}")
    print(f"[PLAN] warnings:              {len(warnings)}")
    print("[PLAN] local draft only — not approval, not execution.")
    return 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Operator Work Session Planner -- local only, stdlib only.\n"
            "\n"
            "Reads the manual decision queue and produces a local work session plan.\n"
            "Never approves, executes, posts, sells, emails, scrapes, or touches live accounts.\n"
            "All outputs are local draft artifacts under 05_logs/operator_work_sessions/<run_id>/.\n"
            "\n"
            "Examples:\n"
            "  python 03_scripts/operator_work_session_planner.py --help\n"
            "  python 03_scripts/operator_work_session_planner.py --dry-run\n"
            "  python 03_scripts/operator_work_session_planner.py --queue-path 14_context/money_workflows/manual_decision_queue.jsonl --dry-run\n"
            "  python 03_scripts/operator_work_session_planner.py --queue-path 14_context/money_workflows/manual_decision_queue.jsonl --max-tasks 3\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--queue-path",
        default=str(_DEFAULT_QUEUE_PATH),
        metavar="PATH",
        help=f"Path to manual decision queue JSONL. Default: {_DEFAULT_QUEUE_PATH}",
    )
    p.add_argument(
        "--max-tasks",
        type=int,
        default=_DEFAULT_MAX_TASKS,
        metavar="N",
        help=f"Maximum number of tasks to include in the plan. Default: {_DEFAULT_MAX_TASKS}",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the plan without writing any files.",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    return _run(args)


if __name__ == "__main__":
    sys.exit(main())
