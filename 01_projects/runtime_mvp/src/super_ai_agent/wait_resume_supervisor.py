"""Local wait/resume supervisor for Ghoti operator sessions.

Tracks pending pushes, approval gates, tool-evaluation holds, and model
availability so the operator does not need to babysit each step manually.

No background daemon. No external calls. No autonomous execution.
Status label: local_wait_resume_only / no_external_adapter_wired
"""

from __future__ import annotations

# Allow direct invocation: python wait_resume_supervisor.py
import sys as _sys
from pathlib import Path as _Path
_SRC = _Path(__file__).resolve().parents[1]
if str(_SRC) not in _sys.path:
    _sys.path.insert(0, str(_SRC))

import base64
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

_REPO_ROOT = Path(__file__).resolve().parents[4]
_RUNTIME_DATA_DIR = _REPO_ROOT / "01_projects" / "runtime_mvp" / "runtime_data"
WAIT_RESUME_PATH = _RUNTIME_DATA_DIR / "wait_resume_items.json"

VALID_STATUSES = frozenset({"pending", "ready", "done", "blocked", "expired"})
VALID_WAIT_TYPES = frozenset(
    {
        "user_approval",
        "manual_push",
        "external_result",
        "time_delay",
        "tool_available",
        "model_available",
    }
)
VALID_RISK_LEVELS = frozenset({"low", "medium", "high", "blocked"})


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ps_write(path: Path, text: str) -> None:
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    ps_path = str(path).replace("'", "''")
    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-Command",
            (
                "[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName"
                f"('{ps_path}')) | Out-Null; "
                f"[System.IO.File]::WriteAllBytes('{ps_path}', "
                f"[Convert]::FromBase64String('{encoded}'))"
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _write_json(path: Path, data: list) -> None:
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(text, encoding="utf-8")
    except OSError:
        _ps_write(path, text)


def _read_json(path: Path) -> list:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


@dataclass
class WaitItem:
    wait_id: str
    title: str
    status: str
    wait_type: str
    created_at_utc: str
    updated_at_utc: str
    repo_relative_context: str
    resume_command: str
    approval_required: bool
    risk_level: str
    notes: str

    def to_dict(self) -> dict:
        return asdict(self)


def list_wait_items(status: str | None = None) -> list[dict]:
    items = _read_json(WAIT_RESUME_PATH)
    if status is not None:
        items = [i for i in items if i.get("status") == status]
    return items


def create_wait_item(
    *,
    title: str,
    wait_type: str,
    repo_relative_context: str = "",
    resume_command: str = "",
    approval_required: bool = True,
    risk_level: str = "medium",
    notes: str = "",
    status: str = "pending",
) -> dict:
    if wait_type not in VALID_WAIT_TYPES:
        raise ValueError(f"Invalid wait_type: {wait_type!r}")
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status!r}")
    if risk_level not in VALID_RISK_LEVELS:
        raise ValueError(f"Invalid risk_level: {risk_level!r}")
    now = _utc_now()
    item = WaitItem(
        wait_id=f"wait-{uuid4().hex[:12]}",
        title=title,
        status=status,
        wait_type=wait_type,
        created_at_utc=now,
        updated_at_utc=now,
        repo_relative_context=repo_relative_context,
        resume_command=resume_command,
        approval_required=approval_required,
        risk_level=risk_level,
        notes=notes,
    )
    items = _read_json(WAIT_RESUME_PATH)
    items.append(item.to_dict())
    _write_json(WAIT_RESUME_PATH, items)
    return item.to_dict()


def _update_item_status(wait_id: str, new_status: str, note: str = "") -> dict:
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {new_status!r}")
    items = _read_json(WAIT_RESUME_PATH)
    for item in items:
        if item.get("wait_id") == wait_id:
            item["status"] = new_status
            item["updated_at_utc"] = _utc_now()
            if note:
                existing = item.get("notes", "")
                item["notes"] = f"{existing} | {note}".strip(" |")
            _write_json(WAIT_RESUME_PATH, items)
            return item
    return {"status": "error", "reason": "wait_id_not_found", "wait_id": wait_id}


def mark_wait_ready(wait_id: str, note: str = "") -> dict:
    return _update_item_status(wait_id, "ready", note)


def mark_wait_done(wait_id: str, note: str = "") -> dict:
    return _update_item_status(wait_id, "done", note)


def summarize_wait_state() -> dict:
    items = list_wait_items()
    counts: dict[str, int] = {}
    for item in items:
        s = str(item.get("status", "unknown"))
        counts[s] = counts.get(s, 0) + 1
    latest_updated = ""
    for item in items:
        ts = str(item.get("updated_at_utc", ""))
        if ts > latest_updated:
            latest_updated = ts
    return {
        "ok": True,
        "total": len(items),
        "pending_count": counts.get("pending", 0),
        "ready_count": counts.get("ready", 0),
        "done_count": counts.get("done", 0),
        "blocked_count": counts.get("blocked", 0),
        "expired_count": counts.get("expired", 0),
        "latest_updated_at_utc": latest_updated or _utc_now(),
        "runtime_wiring_truth": "local_wait_resume_only",
        "autonomous_execution_enabled": False,
        "external_actions_enabled": False,
        "items": [
            {k: v for k, v in i.items() if k in (
                "wait_id", "title", "status", "wait_type",
                "risk_level", "approval_required", "resume_command",
                "updated_at_utc",
            )}
            for i in items
            if i.get("status") not in ("done", "expired")
        ],
    }


_DEFAULT_SEEDS = [
    dict(
        title="Push pending local commits to origin",
        wait_type="manual_push",
        repo_relative_context="feat/ghoti-visible-operator-stack",
        resume_command="git push origin feat/ghoti-visible-operator-stack",
        approval_required=True,
        risk_level="medium",
        notes="Push only after validation passes. Confirm clean git status first.",
    ),
    dict(
        title="Pull Gemma model — ollama pull gemma3:4b (~2.5 GB)",
        wait_type="user_approval",
        repo_relative_context="14_context/gemma_wait_resume_diagnostic.md",
        resume_command="ollama pull gemma3:4b",
        approval_required=True,
        risk_level="medium",
        notes="Requires explicit operator approval. Large download. No paid cloud.",
    ),
    dict(
        title="AutoBrowser adapter evaluation approval",
        wait_type="user_approval",
        repo_relative_context="14_context/autobrowser_isolated_clone_audit.md",
        resume_command="(manual review — see autobrowser_isolated_clone_audit.md)",
        approval_required=True,
        risk_level="high",
        notes="External adapter candidate. Must not be runtime-wired until approval.",
    ),
    dict(
        title="External adapter execution approval gate",
        wait_type="user_approval",
        repo_relative_context="01_projects/runtime_mvp/src/super_ai_agent/action_intent.py",
        resume_command="(manual — operator approves in dashboard approval inbox)",
        approval_required=True,
        risk_level="high",
        notes="No external adapter execution without explicit per-intent approval.",
    ),
    dict(
        title="Dashboard approval queue integration follow-up",
        wait_type="tool_available",
        repo_relative_context="01_projects/dashboard_mvp/server.js",
        resume_command="(future milestone — wire wait_resume_items.json to dashboard UI)",
        approval_required=False,
        risk_level="low",
        notes="Dashboard read route added in N+3.2; full UI integration is a future step.",
    ),
    dict(
        title="Obscura Playwright-CDP smoke test — no stealth, example.com only",
        wait_type="user_approval",
        repo_relative_context="14_context/obscura_runtime_verification.md",
        resume_command="(manual — run playwright CDP test with operator approval; see next_safe_steps)",
        approval_required=True,
        risk_level="medium",
        notes="Binary built and CDP confirmed. Playwright connection test is next optional step.",
    ),
    dict(
        title="LOC report refresh after major commits",
        wait_type="external_result",
        repo_relative_context="14_context/ghoti_code_line_count_report.md",
        resume_command="(re-run LOC count script after next major commit batch)",
        approval_required=False,
        risk_level="low",
        notes="Generated in N+3.2. Refresh after significant code additions.",
    ),
    dict(
        title="TryCUA/CUA Driver evaluation — sandbox only, no live desktop",
        wait_type="user_approval",
        repo_relative_context="14_context/computer_use_strategy_note.md",
        resume_command="(manual review and sandboxed trial required before any wiring)",
        approval_required=True,
        risk_level="high",
        notes="No live account or full desktop autonomy until gated. Sandbox-first.",
    ),
    dict(
        title="Tool intake evaluation — Proxima/LibreChat/OpenWebUI/AnythingLLM/Perplexica/LTX-2/ComfyUI",
        wait_type="user_approval",
        repo_relative_context="14_context/tool_intake_new_candidates_n3_2.md",
        resume_command="(manual review per candidate; see tool_intake_new_candidates_n3_2.md)",
        approval_required=True,
        risk_level="medium",
        notes="Local-first candidates. No paid/cloud connection without explicit approval.",
    ),
]


def seed_default_wait_items_if_empty() -> int:
    items = _read_json(WAIT_RESUME_PATH)
    if items:
        return 0
    now = _utc_now()
    new_items = []
    for seed in _DEFAULT_SEEDS:
        item = WaitItem(
            wait_id=f"wait-{uuid4().hex[:12]}",
            title=seed["title"],
            status="pending",
            wait_type=seed["wait_type"],
            created_at_utc=now,
            updated_at_utc=now,
            repo_relative_context=seed["repo_relative_context"],
            resume_command=seed["resume_command"],
            approval_required=seed["approval_required"],
            risk_level=seed["risk_level"],
            notes=seed["notes"],
        )
        new_items.append(item.to_dict())
    _write_json(WAIT_RESUME_PATH, new_items)
    return len(_DEFAULT_SEEDS)


if __name__ == "__main__":
    seeded = seed_default_wait_items_if_empty()
    if seeded:
        print(f"[wait_resume_supervisor] Seeded {seeded} default wait items.")

    summary = summarize_wait_state()
    print("\n=== Ghoti Wait/Resume Supervisor ===")
    print(f"Total items : {summary['total']}")
    print(f"Pending     : {summary['pending_count']}")
    print(f"Ready       : {summary['ready_count']}")
    print(f"Blocked     : {summary['blocked_count']}")
    print(f"Done        : {summary['done_count']}")
    print(f"Runtime     : {summary['runtime_wiring_truth']}")
    print(f"Autonomous  : {summary['autonomous_execution_enabled']}")
    print(f"Ext actions : {summary['external_actions_enabled']}")
    print()

    active_items = summary["items"]
    if active_items:
        print(f"--- Active wait items ({len(active_items)}) ---")
        for item in active_items:
            approval_tag = "[APPROVAL]" if item.get("approval_required") else "          "
            print(
                f"  [{item['status'].upper():8s}] {item['risk_level']:7s} {approval_tag} "
                f"{item['title']}"
            )
            cmd = item.get("resume_command", "")
            if cmd and not cmd.startswith("("):
                print(f"             resume: {cmd}")
    else:
        print("No active wait items.")
    print()
