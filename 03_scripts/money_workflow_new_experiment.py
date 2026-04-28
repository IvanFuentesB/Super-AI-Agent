"""Append a new Ghoti money experiment entry to experiment_tracker.jsonl.

Standard library only. No external API calls. No posting, selling, or scraping.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TRACKER_PATH = _REPO_ROOT / "14_context" / "money_workflows" / "experiment_tracker.jsonl"

_LIVE_ACTION_WORDS = frozenset({
    "post", "publish", "send", "email", "outreach", "sell", "buy",
    "purchase", "submit", "upload", "deploy", "launch", "live",
    "payment", "charge", "subscribe", "account",
})


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _short_id(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:6]


def _generate_experiment_id() -> str:
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    return f"exp_{ts}_{_short_id(ts)}"


def _has_live_action_words(text: str) -> bool:
    words = set(re.findall(r"\w+", text.lower()))
    return bool(words & _LIVE_ACTION_WORDS)


def _approval_required(risk_level: str, fields: dict) -> bool:
    if risk_level in ("medium", "high"):
        return True
    combined = " ".join(str(v) for v in fields.values())
    if _has_live_action_words(combined):
        return True
    return False


def _parse_args(argv: list[str]) -> dict:
    result: dict = {
        "workflow_type": None,
        "source": None,
        "product_idea": None,
        "target_customer": None,
        "pain_point": None,
        "offer": None,
        "next_action": None,
        "risk_level": "low",
        "channels": [],
        "dry_run": False,
    }
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--dry-run":
            result["dry_run"] = True
            i += 1
        elif arg in ("--workflow-type", "--source", "--product-idea",
                     "--target-customer", "--pain-point", "--offer",
                     "--next-action", "--risk-level"):
            if i + 1 >= len(argv):
                _die(f"ERROR: {arg} requires a value")
            key = arg.lstrip("-").replace("-", "_")
            result[key] = argv[i + 1]
            i += 2
        elif arg == "--channel":
            if i + 1 >= len(argv):
                _die("ERROR: --channel requires a value")
            for ch in argv[i + 1].split(","):
                ch = ch.strip()
                if ch:
                    result["channels"].append(ch)
            i += 2
        else:
            i += 1
    return result


def _die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)


def _validate(parsed: dict) -> None:
    required = [
        "workflow_type", "source", "product_idea",
        "target_customer", "pain_point", "offer", "next_action",
    ]
    for field in required:
        if not parsed.get(field):
            _die(f"ERROR: --{field.replace('_', '-')} is required")

    valid_risk = {"low", "medium", "high"}
    if parsed["risk_level"] not in valid_risk:
        _die(f"ERROR: --risk-level must be one of: {', '.join(sorted(valid_risk))}")


def _build_record(parsed: dict) -> dict:
    exp_id = _generate_experiment_id()
    fields_for_approval = {
        "workflow_type": parsed["workflow_type"],
        "product_idea": parsed["product_idea"],
        "offer": parsed["offer"],
        "next_action": parsed["next_action"],
    }
    approval = _approval_required(parsed["risk_level"], fields_for_approval)

    return {
        "experiment_id": exp_id,
        "created_at": _utc_now(),
        "workflow_type": parsed["workflow_type"],
        "source": parsed["source"],
        "product_idea": parsed["product_idea"],
        "target_customer": parsed["target_customer"],
        "pain_point": parsed["pain_point"],
        "offer": parsed["offer"],
        "price_test": None,
        "distribution_channels": parsed["channels"],
        "content_assets": [],
        "status": "idea",
        "next_action": parsed["next_action"],
        "metrics": {
            "impressions": 0,
            "clicks": 0,
            "opt_ins": 0,
            "replies": 0,
            "sales": 0,
            "revenue_usd": 0,
            "time_spent_hours": 0,
        },
        "risk_level": parsed["risk_level"],
        "approval_required": approval,
        "notes": "",
        "files": [],
    }


def main() -> int:
    argv = sys.argv[1:]

    if not argv or "--help" in argv or "-h" in argv:
        print(
            "Usage: python money_workflow_new_experiment.py\n"
            "  --workflow-type <str>     required\n"
            "  --source <str>            required\n"
            "  --product-idea <str>      required\n"
            "  --target-customer <str>   required\n"
            "  --pain-point <str>        required\n"
            "  --offer <str>             required\n"
            "  --next-action <str>       required\n"
            "  --risk-level <str>        optional; default=low; values: low|medium|high\n"
            "  --channel <str>           optional; repeatable; comma-separated ok\n"
            "  --dry-run                 print JSON without writing\n"
            "\n"
            "Does NOT post, sell, email, scrape, or call external APIs.\n"
            "approval_required is set automatically for medium/high risk or live-action words.\n"
        )
        return 0

    parsed = _parse_args(argv)
    _validate(parsed)

    record = _build_record(parsed)
    line = json.dumps(record, ensure_ascii=False)

    if parsed["dry_run"]:
        print("[dry-run] Would append the following record:")
        print(json.dumps(record, indent=2, ensure_ascii=False))
        print(f"\n[dry-run] Target file: {_TRACKER_PATH.relative_to(_REPO_ROOT)}")
        return 0

    try:
        _TRACKER_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _TRACKER_PATH.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError as exc:
        _die(f"ERROR: could not write to tracker: {exc}")

    print(f"Appended experiment: {record['experiment_id']}")
    print(f"File: {_TRACKER_PATH.relative_to(_REPO_ROOT)}")
    print(f"approval_required: {record['approval_required']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
