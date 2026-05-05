"""Weekly Money Review Artifact Generator -- stdlib only, local only.

No posting, emailing, selling, scraping, live accounts, or model output execution.
All outputs are local drafts requiring human review before any action.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TRACKER_PATH = _REPO_ROOT / "14_context" / "money_workflows" / "experiment_tracker.jsonl"
_MONEY_RUNS_DIR = _REPO_ROOT / "05_logs" / "money_runs"
_MONEY_REVIEWS_DIR = _REPO_ROOT / "05_logs" / "money_reviews"

_SAFETY_FLAGS: dict = {
    "external_api_used": False,
    "scraping_enabled": False,
    "live_account_actions_enabled": False,
    "posting_enabled": False,
    "selling_enabled": False,
    "outreach_enabled": False,
    "payment_actions_enabled": False,
    "tracker_mutated": False,
    "queue_mutated": False,
    "model_output_executed": False,
    "manual_review_required": True,
}

_DECISION_TYPE_BY_STATUS: dict[str, str] = {
    "idea": "COLLECT_MORE_DATA",
    "selected": "BUILD_NEXT",
    "asset_draft": "CREATE_CONTENT_BATCH",
    "approval_needed": "REVIEW_LAUNCH_CHECKLIST",
    "published": "DOUBLE_DOWN",
    "measuring": "ITERATE",
    "done": "KILL",
    "blocked": "PAUSE",
    "killed": "KILL",
}

_FORBIDDEN_LIVE_WORDS = frozenset({
    "post automatically",
    "send email automatically",
    "dm people",
    "scrape platform",
    "upload listing",
    "activate payment",
    "log into account",
    "fake testimonial",
    "fake scarcity",
    "fake income proof",
    "buy followers",
    "buy views",
    "buy comments",
    "bypass platform",
})

_COMMON_CHANNELS = ["email_list", "tiktok", "whop", "gumroad", "youtube"]


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _short_id(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:6]


def _make_run_id() -> str:
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    return f"mrev_{ts}_{_short_id(ts)}"


def _read_jsonl_tolerant(
    path: Path, label: str, max_records: int = 1000
) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    warnings: list[str] = []
    if not path.exists():
        warnings.append(f"MISSING optional file: {path.relative_to(_REPO_ROOT)}")
        return records, warnings
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        warnings.append(f"ERROR reading {label}: {exc}")
        return records, warnings
    for i, raw in enumerate(lines, 1):
        raw = raw.strip()
        if not raw:
            continue
        if len(records) >= max_records:
            warnings.append(f"CAPPED {label} at {max_records} records (line {i}+)")
            break
        try:
            obj = json.loads(raw)
            if not isinstance(obj, dict):
                warnings.append(f"SKIP non-object line {i} in {label}")
                continue
            records.append(obj)
        except json.JSONDecodeError as exc:
            warnings.append(f"SKIP malformed JSONL line {i} in {label}: {exc}")
    return records, warnings


def _load_optional_json(path: Path, label: str) -> tuple[dict | None, list[str]]:
    warnings: list[str] = []
    if not path.exists():
        warnings.append(f"MISSING optional file: {path.relative_to(_REPO_ROOT)}")
        return None, warnings
    try:
        return json.loads(path.read_text(encoding="utf-8")), warnings
    except (OSError, json.JSONDecodeError) as exc:
        warnings.append(f"ERROR reading {label}: {exc}")
        return None, warnings


def _collect_run_summaries(money_runs_dir: Path) -> tuple[list[dict], list[str]]:
    summaries: list[dict] = []
    warnings: list[str] = []
    if not money_runs_dir.exists():
        warnings.append(f"MISSING money_runs dir: {money_runs_dir.relative_to(_REPO_ROOT)}")
        return summaries, warnings
    for run_dir in sorted(money_runs_dir.iterdir()):
        if not run_dir.is_dir():
            continue
        data, w = _load_optional_json(
            run_dir / "run_summary.json", f"run_summary in {run_dir.name}"
        )
        warnings.extend(w)
        if data is not None:
            data["_run_dir"] = run_dir.name
            summaries.append(data)
    return summaries, warnings


def _collect_experiment_candidates(money_runs_dir: Path) -> tuple[list[dict], list[str]]:
    candidates: list[dict] = []
    warnings: list[str] = []
    if not money_runs_dir.exists():
        return candidates, warnings
    for run_dir in sorted(money_runs_dir.iterdir()):
        if not run_dir.is_dir():
            continue
        cand_path = run_dir / "experiment_candidates.jsonl"
        recs, w = _read_jsonl_tolerant(cand_path, f"experiment_candidates in {run_dir.name}")
        warnings.extend(w)
        for rec in recs:
            rec.setdefault("_run_dir", run_dir.name)
            candidates.append(rec)
    return candidates, warnings


def _build_snapshot(experiments: list[dict]) -> dict:
    status_counts: Counter = Counter()
    workflow_counts: Counter = Counter()
    risk_counts: Counter = Counter()
    bucket_counts: Counter = Counter()
    channel_counts: Counter = Counter()
    approval_count = 0
    blocked_count = 0
    scored_count = 0
    total_sales = 0
    total_revenue = 0.0
    total_opt_ins = 0

    for exp in experiments:
        status = exp.get("status", "unknown")
        status_counts[status] += 1
        workflow_counts[exp.get("workflow_type", "unknown")] += 1
        risk_counts[exp.get("risk_level", "unknown")] += 1
        if exp.get("approval_required"):
            approval_count += 1
        if status == "blocked":
            blocked_count += 1
        if scoring := exp.get("scoring"):
            bucket_counts[scoring.get("priority_bucket", "?")] += 1
            scored_count += 1
        for ch in exp.get("distribution_channels") or []:
            channel_counts[ch] += 1
        m = exp.get("metrics") or {}
        total_sales += m.get("sales", 0)
        total_revenue += m.get("revenue_usd", 0.0)
        total_opt_ins += m.get("opt_ins", 0)

    sorted_exps = sorted(experiments, key=lambda e: e.get("created_at", ""), reverse=True)
    latest = [
        {
            "experiment_id": e.get("experiment_id"),
            "workflow_type": e.get("workflow_type"),
            "status": e.get("status"),
            "product_idea": e.get("product_idea"),
        }
        for e in sorted_exps[:5]
    ]

    return {
        "experiment_count": len(experiments),
        "experiments_by_status": dict(status_counts),
        "experiments_by_workflow_type": dict(workflow_counts),
        "experiments_by_risk": dict(risk_counts),
        "priority_bucket_counts": dict(bucket_counts),
        "scored_count": scored_count,
        "approval_required_count": approval_count,
        "blocked_count": blocked_count,
        "distribution_channel_counts": dict(channel_counts),
        "manual_sales_total": total_sales,
        "manual_revenue_total": total_revenue,
        "manual_opt_ins_total": total_opt_ins,
        "latest_records": latest,
    }


def _heuristic_review(
    experiments: list[dict],
    run_summaries: list[dict],
    snapshot: dict,
    week_start: str,
    week_end: str,
    run_id: str,
) -> dict:
    scored = sorted(
        [e for e in experiments if e.get("scoring")],
        key=lambda e: e["scoring"].get("total_score", 0),
        reverse=True,
    )
    unscored = [e for e in experiments if not e.get("scoring")]
    top_experiments = (scored[:3] + unscored[:2]) if scored else unscored[:5]

    all_channels: set[str] = set()
    for exp in experiments:
        all_channels.update(exp.get("distribution_channels") or [])
    missing_channels = [ch for ch in _COMMON_CHANNELS if ch not in all_channels]

    now = _utc_now()
    decisions: list[dict] = []
    for i, exp in enumerate(experiments[:20]):
        exp_id = exp.get("experiment_id", f"unknown_{i}")
        status = exp.get("status", "idea")
        risk = exp.get("risk_level", "low")
        scoring = exp.get("scoring")
        m = exp.get("metrics") or {}
        has_metrics = any(v and v > 0 for v in m.values())

        decision_type = _DECISION_TYPE_BY_STATUS.get(status, "COLLECT_MORE_DATA")
        if scoring:
            score = scoring.get("total_score", 0)
            if score >= 40:
                decision_type = "DOUBLE_DOWN"
            elif score >= 32:
                decision_type = "ITERATE"

        if has_metrics:
            confidence = "medium"
        elif scoring and scoring.get("total_score", 0) >= 32:
            confidence = "medium"
        else:
            confidence = "low"

        reason_parts: list[str] = []
        if scoring:
            bucket = scoring.get("priority_bucket", "?")
            score_val = scoring.get("total_score", 0)
            reason_parts.append(f"Priority {bucket} (score {score_val}/50).")
        if has_metrics:
            sales = m.get("sales", 0)
            rev = m.get("revenue_usd", 0)
            opt = m.get("opt_ins", 0)
            reason_parts.append(
                f"Manual metrics: sales={sales}, revenue=USD{rev:.2f}, opt_ins={opt}."
            )
        else:
            reason_parts.append(
                "No metrics recorded -- manual data collection needed before any claim."
            )
        if risk in ("medium", "high"):
            reason_parts.append(f"Risk {risk} -- human approval required before any live step.")

        decisions.append({
            "decision_id": f"cand_{run_id}_{i + 1:03d}",
            "created_at": now,
            "source": exp.get("_run_dir") or exp.get("run_id") or run_id,
            "experiment_id": exp_id,
            "title": exp.get("product_idea") or exp_id,
            "category": decision_type,
            "recommendation": decision_type,
            "confidence": confidence,
            "rationale": " ".join(reason_parts) or "Heuristic draft; no model input.",
            "risk_level": risk,
            "approval_required": True,
            "public_or_money_facing": False,
            "next_local_step": exp.get(
                "next_action", "Review experiment and define next local step."
            ),
            "blocked_reason": "",
            "status": "candidate",
            "files": exp.get("files") or [],
            "notes": "Heuristic draft only. Human review required before any action.",
        })

    return {
        "top_experiments": top_experiments,
        "decisions": decisions,
        "missing_channels": missing_channels,
        "week_start": week_start,
        "week_end": week_end,
        "run_summaries_found": len(run_summaries),
    }


def _write_request_json(
    out_dir: Path, run_id: str, week_start: str, week_end: str, argv: list[str]
) -> None:
    data = {
        "task": "weekly_money_review",
        "run_id": run_id,
        "created_at": _utc_now(),
        "week_start": week_start,
        "week_end": week_end,
        "argv": argv,
        "source_files_considered": [
            str(_TRACKER_PATH.relative_to(_REPO_ROOT)),
            str(_MONEY_RUNS_DIR.relative_to(_REPO_ROOT)),
        ],
        **_SAFETY_FLAGS,
    }
    (out_dir / "request.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _write_tracker_snapshot(out_dir: Path, snapshot: dict, warnings: list[str]) -> None:
    (out_dir / "tracker_snapshot.json").write_text(
        json.dumps({**snapshot, "parse_warnings": warnings}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _write_source_index_json(
    out_dir: Path,
    run_id: str,
    tracker_records: list[dict],
    run_summaries: list[dict],
    candidates: list[dict],
    warnings: list[str],
) -> None:
    data = {
        "run_id": run_id,
        "created_at": _utc_now(),
        "sources": {
            "experiment_tracker_jsonl": {
                "path": str(_TRACKER_PATH.relative_to(_REPO_ROOT)),
                "records_loaded": len(tracker_records),
                "exists": _TRACKER_PATH.exists(),
            },
            "money_runs_dir": {
                "path": str(_MONEY_RUNS_DIR.relative_to(_REPO_ROOT)),
                "run_dirs_found": len(run_summaries),
                "experiment_candidates_total": len(candidates),
                "exists": _MONEY_RUNS_DIR.exists(),
            },
        },
        "parse_warnings": warnings,
    }
    (out_dir / "source_index.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _write_weekly_review_json(
    out_dir: Path,
    run_id: str,
    week_start: str,
    week_end: str,
    snapshot: dict,
    review: dict,
    all_warnings: list[str],
    since_days: int,
) -> None:
    top_candidates = [
        {
            "experiment_id": e.get("experiment_id"),
            "product_idea": e.get("product_idea"),
            "workflow_type": e.get("workflow_type"),
            "status": e.get("status"),
            "risk_level": e.get("risk_level"),
        }
        for e in review["top_experiments"][:5]
    ]

    next_local_actions = []
    if review["missing_channels"]:
        next_local_actions.append(
            f"Consider adding distribution channels: {', '.join(review['missing_channels'])}"
        )
    if snapshot["experiment_count"] == 0:
        next_local_actions.append("Add first experiment to tracker or run video_to_money runner.")
    if snapshot["blocked_count"] > 0:
        next_local_actions.append(
            f"Review {snapshot['blocked_count']} blocked experiment(s) and resolve blockers."
        )
    if snapshot["approval_required_count"] > 0:
        next_local_actions.append(
            f"Human approval required for {snapshot['approval_required_count']} experiment(s) before any live step."
        )
    if not next_local_actions:
        next_local_actions.append("Review top candidates and decide next experiment step.")

    data = {
        "run_id": run_id,
        "created_at": _utc_now(),
        "week_start": week_start,
        "week_end": week_end,
        "since_days": since_days,
        "source_counts": {
            "tracker_experiments": snapshot["experiment_count"],
            "money_run_summaries": review["run_summaries_found"],
        },
        "total_experiments": snapshot["experiment_count"],
        "total_money_runs": review["run_summaries_found"],
        "top_candidates": top_candidates,
        "snapshot_summary": {
            "by_status": snapshot["experiments_by_status"],
            "by_workflow_type": snapshot["experiments_by_workflow_type"],
            "by_risk": snapshot["experiments_by_risk"],
            "missing_channels": review["missing_channels"],
            "manual_revenue_total": snapshot["manual_revenue_total"],
            "manual_sales_total": snapshot["manual_sales_total"],
            "manual_opt_ins_total": snapshot["manual_opt_ins_total"],
        },
        "warnings": all_warnings,
        "safety_flags": _SAFETY_FLAGS,
        "next_local_actions": next_local_actions,
        "approval_required_for_public_actions": True,
    }
    (out_dir / "weekly_review.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _write_weekly_review_md(
    out_dir: Path,
    run_id: str,
    week_start: str,
    week_end: str,
    snapshot: dict,
    review: dict,
    all_warnings: list[str],
) -> None:
    lines: list[str] = []
    lines.append(f"# Weekly Money Review — {week_start} to {week_end}")
    lines.append(f"\n**Run ID:** `{run_id}`  ")
    lines.append(f"**Generated:** {_utc_now()}  ")
    lines.append(
        "**Status:** DRAFT — Human review required before any action. "
        "All recommendations are candidates only.\n"
    )

    lines.append("## Summary\n")
    lines.append(f"- Total experiments tracked: **{snapshot['experiment_count']}**")
    lines.append(f"- Money run summaries found: **{review['run_summaries_found']}**")
    lines.append(f"- Experiments requiring approval: **{snapshot['approval_required_count']}**")
    lines.append(f"- Blocked experiments: **{snapshot['blocked_count']}**")
    if snapshot["manual_revenue_total"] > 0:
        lines.append(f"- Manual revenue recorded: **USD {snapshot['manual_revenue_total']:.2f}**")
    lines.append("")

    if snapshot["experiments_by_status"]:
        lines.append("### By Status\n")
        for status, count in sorted(snapshot["experiments_by_status"].items()):
            lines.append(f"- {status}: {count}")
        lines.append("")

    if snapshot["experiments_by_workflow_type"]:
        lines.append("### By Workflow Type\n")
        for wt, count in sorted(snapshot["experiments_by_workflow_type"].items()):
            lines.append(f"- {wt}: {count}")
        lines.append("")

    lines.append("## Top Experiments\n")
    if review["top_experiments"]:
        for exp in review["top_experiments"]:
            idea = exp.get("product_idea") or exp.get("experiment_id") or "Unknown"
            status = exp.get("status", "?")
            risk = exp.get("risk_level", "?")
            lines.append(f"- **{idea}** — status: `{status}`, risk: `{risk}`")
    else:
        lines.append("_No experiments found. Add data to tracker or run video_to_money runner._")
    lines.append("")

    if review["missing_channels"]:
        lines.append("## Distribution Gaps\n")
        lines.append(
            "The following common channels have no experiments yet: "
            + ", ".join(f"`{c}`" for c in review["missing_channels"])
        )
        lines.append("")

    lines.append("## Decision Candidates\n")
    lines.append(
        "_See `decisions_recommended.jsonl` for full candidate list. "
        "All require human approval before any live step._\n"
    )
    if review["decisions"]:
        for d in review["decisions"][:5]:
            title = d.get("title") or d.get("experiment_id") or "Unknown"
            cat = d.get("category", "?")
            risk = d.get("risk_level", "?")
            next_step = d.get("next_local_step", "")
            lines.append(f"- **{title}** — `{cat}` | risk: `{risk}`")
            if next_step:
                lines.append(f"  - Next: {next_step}")
    else:
        lines.append("_No decision candidates generated._")
    lines.append("")

    lines.append("## Next Local Actions\n")
    lines.append("_All actions require human review and approval before any live step._\n")
    next_actions: list[str] = []
    if review["missing_channels"]:
        next_actions.append(
            f"Consider adding distribution channels: {', '.join(review['missing_channels'])}"
        )
    if snapshot["experiment_count"] == 0:
        next_actions.append("Add first experiment to tracker or run video_to_money runner.")
    if snapshot["blocked_count"] > 0:
        next_actions.append(
            f"Review {snapshot['blocked_count']} blocked experiment(s) and resolve blockers."
        )
    if snapshot["approval_required_count"] > 0:
        next_actions.append(
            f"Human approval required for {snapshot['approval_required_count']} experiment(s)."
        )
    if not next_actions:
        next_actions.append("Review top candidates and decide next experiment step.")
    for action in next_actions:
        lines.append(f"1. {action}")
    lines.append("")

    lines.append("## Safety Flags\n")
    lines.append("| Flag | Value |")
    lines.append("|------|-------|")
    for k, v in _SAFETY_FLAGS.items():
        lines.append(f"| {k} | `{v}` |")
    lines.append("")

    if all_warnings:
        lines.append("## Parse Warnings\n")
        for w in all_warnings:
            lines.append(f"- {w}")
        lines.append("")

    lines.append(
        "---\n_This artifact is a local draft. "
        "No posting, selling, outreach, payment, or external actions have been taken. "
        "Human review required before any action._"
    )

    (out_dir / "weekly_review.md").write_text("\n".join(lines), encoding="utf-8")


def _write_decisions_recommended_jsonl(out_dir: Path, decisions: list[dict]) -> None:
    out_path = out_dir / "decisions_recommended.jsonl"
    lines: list[str] = []
    for d in decisions:
        entry = {
            "decision_id": d["decision_id"],
            "created_at": d["created_at"],
            "source": d.get("source", ""),
            "title": d.get("title", ""),
            "category": d.get("category", ""),
            "recommendation": d.get("recommendation", ""),
            "rationale": d.get("rationale", ""),
            "risk_level": d.get("risk_level", "low"),
            "approval_required": True,
            "public_or_money_facing": False,
            "next_local_step": d.get("next_local_step", ""),
            "blocked_reason": d.get("blocked_reason", ""),
            "status": "candidate",
            "notes": d.get("notes", ""),
        }
        lines.append(json.dumps(entry, ensure_ascii=False))
    out_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def _run_review(args: argparse.Namespace) -> int:
    since_days: int = args.since_days
    output_root: Path = Path(args.output_root) if args.output_root else _MONEY_REVIEWS_DIR
    dry_run: bool = args.dry_run

    now_utc = datetime.now(UTC)
    week_end = now_utc.date()
    week_start = week_end - timedelta(days=since_days)

    run_id = _make_run_id()
    all_warnings: list[str] = []

    # Collect tracker experiments
    tracker_records, w = _read_jsonl_tolerant(_TRACKER_PATH, "experiment_tracker.jsonl")
    all_warnings.extend(w)

    # Collect money run summaries
    run_summaries, w = _collect_run_summaries(_MONEY_RUNS_DIR)
    all_warnings.extend(w)

    # Collect experiment candidates from money runs
    run_candidates, w = _collect_experiment_candidates(_MONEY_RUNS_DIR)
    all_warnings.extend(w)

    # Merge all experiments: tracker records + run candidates (dedup by experiment_id)
    all_experiments: list[dict] = list(tracker_records)
    seen_ids: set[str] = {e.get("experiment_id", "") for e in all_experiments}
    for cand in run_candidates:
        cand_id = cand.get("experiment_id", "")
        if cand_id and cand_id in seen_ids:
            continue
        all_experiments.append(cand)
        if cand_id:
            seen_ids.add(cand_id)

    snapshot = _build_snapshot(all_experiments)
    review = _heuristic_review(
        all_experiments, run_summaries, snapshot, str(week_start), str(week_end), run_id
    )

    if dry_run:
        print(f"[DRY-RUN] run_id: {run_id}")
        print(f"[DRY-RUN] week_start: {week_start}  week_end: {week_end}")
        print(f"[DRY-RUN] tracker_records: {len(tracker_records)}")
        print(f"[DRY-RUN] run_summaries: {len(run_summaries)}")
        print(f"[DRY-RUN] run_candidates: {len(run_candidates)}")
        print(f"[DRY-RUN] total_experiments: {len(all_experiments)}")
        print(f"[DRY-RUN] decisions_generated: {len(review['decisions'])}")
        print(f"[DRY-RUN] warnings: {len(all_warnings)}")
        for w in all_warnings:
            print(f"[DRY-RUN] WARN: {w}")
        print("[DRY-RUN] No files written.")
        return 0

    out_dir = output_root / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_request_json(out_dir, run_id, str(week_start), str(week_end), sys.argv)
    _write_tracker_snapshot(out_dir, snapshot, all_warnings)
    _write_source_index_json(
        out_dir, run_id, tracker_records, run_summaries, run_candidates, all_warnings
    )
    _write_weekly_review_json(
        out_dir, run_id, str(week_start), str(week_end), snapshot, review, all_warnings, since_days
    )
    _write_weekly_review_md(
        out_dir, run_id, str(week_start), str(week_end), snapshot, review, all_warnings
    )
    _write_decisions_recommended_jsonl(out_dir, review["decisions"])

    print(f"Weekly review artifacts written to: {out_dir}")
    print(f"  run_id:              {run_id}")
    print(f"  week:                {week_start} to {week_end}")
    print(f"  total_experiments:   {len(all_experiments)}")
    print(f"  total_money_runs:    {len(run_summaries)}")
    print(f"  decisions_generated: {len(review['decisions'])}")
    print(f"  warnings:            {len(all_warnings)}")
    for w_msg in all_warnings:
        print(f"  WARN: {w_msg}")
    print("  approval_required_for_public_actions: true")
    return 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Weekly Money Review Artifact Generator — local only, stdlib only. "
            "No posting, selling, scraping, or live account actions."
        )
    )
    p.add_argument(
        "--since-days",
        type=int,
        default=7,
        metavar="N",
        help="Number of days to look back for the review window (default: 7).",
    )
    p.add_argument(
        "--output-root",
        default=str(_MONEY_REVIEWS_DIR),
        metavar="PATH",
        help=f"Root directory for review artifacts (default: {_MONEY_REVIEWS_DIR}).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without writing any files.",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    return _run_review(args)


if __name__ == "__main__":
    sys.exit(main())
