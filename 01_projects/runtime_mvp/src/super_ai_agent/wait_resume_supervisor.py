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
    dict(
        title="OpenFang exact repo identification and Rust install approval",
        wait_type="user_approval",
        repo_relative_context="14_context/openfang_rust_readiness_plan.md",
        resume_command="(manual — identify exact OpenFang repo, confirm license, then request operator approval for rustup install and isolated clone)",
        approval_required=True,
        risk_level="medium",
        notes="Rust not installed. Exact repo URL unconfirmed. No clone until repo identified, license checked, and operator approves rustup install.",
    ),
    dict(
        title="Screenpipe local capture retention setup — 3-day retention, operator-start only",
        wait_type="user_approval",
        repo_relative_context="14_context/screenpipe_local_capture_plan.md",
        resume_command="(manual — review screenpipe_local_capture_plan.md, confirm retention policy, operator-start capture only)",
        approval_required=True,
        risk_level="medium",
        notes="Retention policy + cleanup script created in N+3.3. Capture disabled by default. No capture until operator starts.",
    ),
    dict(
        title="Obsidian vault token-saving workflow — use compact notes in prompts",
        wait_type="tool_available",
        repo_relative_context="14_context/obsidian_vault/00_Index.md",
        resume_command="(start referencing vault notes in prompts instead of re-pasting context)",
        approval_required=False,
        risk_level="low",
        notes="Vault created at 14_context/obsidian_vault/ in N+3.3. Use vault notes to reduce token usage.",
    ),
    dict(
        title="CUA exact source confirmed — trycua/cua canonical repo evaluated",
        wait_type="external_result",
        repo_relative_context="14_context/cua_trycua_exact_source_evaluation.md",
        resume_command="(evaluation complete — see cua_trycua_exact_source_evaluation.md; Windows incompatible with canonical Lume layer; identify Docker-based alternative)",
        approval_required=False,
        risk_level="low",
        notes="Canonical source github.com/trycua/cua identified in N+3.4. macOS/Apple Silicon only. Windows alternative needed before any install.",
    ),
    dict(
        title="CUA sandbox profile operator approval — review 23_configs/cua_sandbox_profile.example.json",
        wait_type="user_approval",
        repo_relative_context="23_configs/cua_sandbox_profile.example.json",
        resume_command="(manual — operator reviews sandbox profile, confirms enabled=false, approves first screenshot-only test)",
        approval_required=True,
        risk_level="high",
        notes="Profile created in N+3.4. enabled=false. Screenshots only. Click/type disabled. No live accounts. Retention 3 days.",
    ),
    dict(
        title="First screenshot-only CUA sandbox smoke test",
        wait_type="user_approval",
        repo_relative_context="14_context/cua_sandbox_profile_plan.md",
        resume_command="(manual — operator confirms CUA driver installed in sandbox, approves first observe-only action against local test page)",
        approval_required=True,
        risk_level="high",
        notes="Smoke test: screenshot only, local test page, no click, no type, no live account. Audit log entry required.",
    ),
    dict(
        title="CUA descriptor-only adapter reviewed — no execution, no install, sandbox-only (N+3.5)",
        wait_type="external_result",
        repo_relative_context="14_context/cua_adapter_descriptor_design_n3_5.md",
        resume_command="(descriptor in action_intent.py: adapter_id=cua-driver-reference, status=descriptor_only, can_execute=false)",
        approval_required=False,
        risk_level="low",
        notes="Descriptor confirmed in action_intent.py in N+3.4/N+3.5. No execution path. No imports from CUA. Sandbox profile at 23_configs/cua_sandbox_profile.example.json.",
    ),
    dict(
        title="Docker Desktop install approval — required before CUA Docker/Ubuntu path can proceed (N+3.5)",
        wait_type="user_approval",
        repo_relative_context="14_context/cua_trycua_isolated_clone_audit_n3_5.md",
        resume_command="(manual — operator approves Docker Desktop install; then evaluate libs/qemu-docker/linux path for Ubuntu container agent)",
        approval_required=True,
        risk_level="medium",
        notes="All local CUA paths blocked: Lume=macOS-only, Windows Sandbox=Pro/Enterprise, Docker=not installed, WSL=not installed. Docker Desktop is the lowest-risk unlocker on Windows 11 Home.",
    ),
    dict(
        title="Docker Desktop install approval for CUA sandbox (N+3.6)",
        wait_type="user_approval",
        repo_relative_context="14_context/docker_desktop_cua_install_gate_n3_6.md",
        resume_command="(manual — user must type: APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX)",
        approval_required=True,
        risk_level="high",
        notes="Gate doc created N+3.6. Risks: admin install, WSL2 backend, background services, disk/network usage, container permissions. No install until exact approval phrase provided.",
    ),
    dict(
        title="CUA Docker/Ubuntu screenshot-only smoke after Docker install (N+3.6)",
        wait_type="user_approval",
        repo_relative_context="14_context/cua_docker_ubuntu_sandbox_path_n3_6.md",
        resume_command="(manual — only after Docker is installed and sandbox profile approved; Kasm/Ubuntu lightweight container; localhost only; no host mounts; no privileged; no credentials)",
        approval_required=True,
        risk_level="high",
        notes="Smoke path documented N+3.6. Screenshot/observe only. No click, no type, no live account. Audit log required. DO NOT RUN until Docker installed and operator approves.",
    ),
    dict(
        title="Screenpipe dashboard route + Obsidian vault sync fallback (N+3.6)",
        wait_type="tool_available",
        repo_relative_context="14_context/n3_6_execution_decision.md",
        resume_command="(manual — operator types: DO SCREENPIPE DASHBOARD + OBSIDIAN SYNC FIRST)",
        approval_required=False,
        risk_level="low",
        notes="Alternative to Docker install if operator prefers no new system installs. Dashboard route = read-only status panel, no capture started. Obsidian = compact markdown vault updates. Decision doc at n3_6_execution_decision.md.",
    ),
    dict(
        title="Screenpipe read-only status route + Obsidian vault sync done (N+3.7 PATH B)",
        wait_type="tool_available",
        repo_relative_context="14_context/screenpipe_dashboard_status_route_n3_7.md",
        resume_command="GET /api/ghoti/screenpipe/status — no capture started; use vault notes from 14_context/obsidian_vault/ in prompts",
        approval_required=False,
        risk_level="low",
        notes="PATH B completed N+3.7. Dashboard status route added to server.js (no capture, no delete, policy inspection only). Vault notes updated: 00_Index, 01_Current_State, 04_Tools, 05_Safety_Gates. Docker/CUA gate still pending — type APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX to unlock.",
    ),
    dict(
        title="Docker Desktop verified — CUA screenshot-only smoke is next approval gate (N+3.8)",
        wait_type="user_approval",
        repo_relative_context="14_context/docker_desktop_install_verification_n3_8.md",
        resume_command="(manual — open Docker Desktop from Start menu; verify docker info shows daemon running; then request CUA smoke approval)",
        approval_required=True,
        risk_level="medium",
        notes="Docker Desktop 4.70.0 installed via winget in N+3.8. CLI at C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker.exe. Daemon not yet running — operator must launch Docker Desktop manually. WSL2 not yet installed — Docker Desktop will install on first launch. After daemon is verified, CUA screenshot-only smoke is next gate (separate approval required).",
    ),
    dict(
        title="CUA screenshot-only smoke — separate approval required after Docker daemon verified (N+3.8)",
        wait_type="user_approval",
        repo_relative_context="14_context/cua_next_screenshot_smoke_after_docker_n3_8.md",
        resume_command="(manual — verify docker info running, then request CUA smoke approval; see cua_next_screenshot_smoke_after_docker_n3_8.md for exact workflow)",
        approval_required=True,
        risk_level="high",
        notes="Smoke plan at cua_next_screenshot_smoke_after_docker_n3_8.md. ActionIntent required. Payload hash required. localhost or example.com only. No click, no type, no host mounts, no privileged, no live accounts. Audit event required. Output under 05_logs/cua_smoke_runs/<run_id>/. DO NOT RUN until Docker daemon is verified and operator provides explicit separate approval.",
    ),
    dict(
        title="Docker Desktop manual launch / WSL2 setup required before CUA smoke (N+3.9)",
        wait_type="user_approval",
        repo_relative_context="14_context/docker_daemon_post_install_verification_n3_9.md",
        resume_command="(manual — open Docker Desktop from Start menu; accept WSL2 install prompts; wait for 'Docker is running' green status; reboot if prompted; then verify: docker info shows Server section + wsl --status shows WSL2 installed; then request CUA smoke approval separately)",
        approval_required=True,
        risk_level="medium",
        notes="Verified N+3.9: Docker CLI 29.4.0 present; Docker Compose v5.1.2 present; Docker Desktop.exe present. Daemon NOT running — npipe not found. WSL2 NOT installed. Verdict: docker_installed_daemon_not_running + wsl_setup_required. CUA smoke blocked. See docker_daemon_post_install_verification_n3_9.md for exact steps.",
    ),
    dict(
        title="CUA screenshot smoke exact plan ready — approval and daemon required (N+3.9)",
        wait_type="user_approval",
        repo_relative_context="14_context/cua_screenshot_smoke_exact_plan_n3_9.md",
        resume_command="(manual — after Docker daemon verified and WSL2 installed: pin trycua/cua-ubuntu:latest to exact sha256 digest; obtain image approval; create ActionIntent; compute payload hash; obtain smoke approval; then follow exact plan in cua_screenshot_smoke_exact_plan_n3_9.md)",
        approval_required=True,
        risk_level="high",
        notes="Smoke plan updated N+3.9. Image: trycua/cua-ubuntu:latest (kasmweb/core-ubuntu-jammy:1.17.0 base). No privileged mode. No host mounts. Localhost port only. Screenshot-only. Payload hash required before approval. Audit event required. DO NOT RUN until daemon verified + image digest approved + separate smoke approval obtained.",
    ),
    dict(
        title="Docker Desktop GUI running but engine start failed — WSL2 GUI setup required (N+3.10)",
        wait_type="user_approval",
        repo_relative_context="14_context/docker_desktop_post_launch_verification_n3_10.md",
        resume_command="(manual — Docker Desktop window is open on screen; sign in or skip Docker Hub login; accept WSL2 install prompt; wait for 'Docker Engine running' green status; reboot if prompted; then verify: docker info shows Server section + wsl --status shows WSL2 installed; report result to start N+3.11)",
        approval_required=True,
        risk_level="medium",
        notes="N+3.10 finding: Docker Desktop launched (4 PIDs), context=desktop-linux, license accepted, but engine HTTP 503 for 2+ min — WSL2 not installed. GUI open on screen. Operator must interact with Docker Desktop window. Reboot likely required after WSL2 install. See docker_desktop_post_launch_verification_n3_10.md for exact steps.",
    ),
    dict(
        title='Docker/WSL ready verified for CUA path (N+3.11)',
        wait_type='external_result',
        repo_relative_context='14_context/docker_wsl_ready_verification_n3_11.md',
        resume_command='(verified -- docker info shows Server section; context=desktop-linux; 16 CPUs, 15.27 GiB; verdict: docker_wsl_ready)',
        approval_required=False,
        risk_level='low',
        notes='N+3.11: Docker daemon reachable, WSL2 docker-desktop running, context desktop-linux, server 29.4.0, 16 CPUs, 15.27 GiB. CUA image digest pinned.',
    ),
    dict(
        title='CUA image digest approval required before screenshot smoke (N+3.11)',
        wait_type='user_approval',
        repo_relative_context='14_context/cua_image_digest_gate_n3_11.md',
        resume_command='(manual -- operator must type: APPROVE CUA IMAGE DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a FOR SCREENSHOT-ONLY SMOKE)',
        approval_required=True,
        risk_level='high',
        notes='N+3.11: digest pinned via docker manifest inspect. amd64 digest: sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a. Tag latest is mutable - must use digest reference. See cua_image_digest_gate_n3_11.md.',
    ),
    dict(
        title='Gemma/Ollama local brain smoke pending - model pull approval required (N+3.11)',
        wait_type='user_approval',
        repo_relative_context='14_context/gemma_ollama_truth_check_n3_11.md',
        resume_command='(manual -- operator must type: APPROVE OLLAMA PULL GEMMA3:4B FOR LOCAL BRAIN SMOKE)',
        approval_required=True,
        risk_level='medium',
        notes='N+3.11: Ollama 0.9.2 installed. No models installed. Gemma not available locally. Approval required for ollama pull gemma3:4b (~2.5 GB).',
    ),
    dict(
        title='CUA ActionIntent + payload hash ready — both digest and smoke approvals required (N+3.12)',
        wait_type='user_approval',
        repo_relative_context='14_context/cua_action_intent_payload_gate_n3_12.md',
        resume_command=(
            '(manual -- provide BOTH: '
            '(1) APPROVE CUA IMAGE DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a FOR SCREENSHOT-ONLY SMOKE, '
            'then (2) APPROVE CUA SCREENSHOT-ONLY SMOKE WITH DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a AND PAYLOAD 69149d31f052bfce0d15e383797b3fbbeee80dc351f3a2e100f1746fb51418e4)'
        ),
        approval_required=True,
        risk_level='high',
        notes=(
            'N+3.12: ActionIntent created (intent-n3-12-cua-smoke-20260428-1300). '
            'Payload hash: 69149d31f052bfce0d15e383797b3fbbeee80dc351f3a2e100f1746fb51418e4. '
            'Image digest verified unchanged: sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a. '
            'Docker/WSL GO. Both approval phrases required before docker pull/run.'
        ),
    ),
    dict(
        title='Gemma local brain pull or smoke completion gate (N+3.12)',
        wait_type='user_approval',
        repo_relative_context='14_context/gemma_local_brain_path_n3_12.md',
        resume_command=(
            '(manual -- type: APPROVE OLLAMA PULL GEMMA3:4B FOR LOCAL BRAIN SMOKE; '
            'then run: ollama pull gemma3:4b && ollama run gemma3:4b "Return exactly: GHOTI_LOCAL_BRAIN_OK")'
        ),
        approval_required=True,
        risk_level='medium',
        notes=(
            'N+3.12: Ollama 0.9.2 confirmed installed, no models installed. '
            'Gemma not locally available. brain_inference_ready=NO. '
            'Approval phrase required before pull (~2.5 GB).'
        ),
    ),
    dict(
        title='Persistent dashboard/app startup planning — startup script and health check (N+3.12)',
        wait_type='tool_available',
        repo_relative_context='14_context/persistent_dashboard_app_plan_n3_12.md',
        resume_command=(
            '(manual -- review 14_context/persistent_dashboard_app_plan_n3_12.md; '
            'decide: (A) PowerShell launcher shortcut or (B) Startup folder entry; '
            'implement 03_scripts/run_dashboard.ps1 when ready)'
        ),
        approval_required=False,
        risk_level='low',
        notes=(
            'N+3.12: Dashboard must be manually relaunched. Plan doc created. '
            'Recommended first step: PowerShell launcher + shortcut (no admin, reversible). '
            'Do NOT add Windows service without separate approval.'
        ),
    ),
    dict(
        title='CUA screenshot-only smoke completed safely (N+3.13)',
        wait_type='external_result',
        repo_relative_context='05_logs/cua_smoke_runs/n3_13_20260428_1400/screenshot_result.md',
        resume_command=(
            '(completed -- container started, KasmVNC HTTP 401 confirmed, container stopped; '
            'see 05_logs/cua_smoke_runs/n3_13_20260428_1400/screenshot_result.md)'
        ),
        approval_required=False,
        risk_level='low',
        notes=(
            'N+3.13: CUA smoke PASS. Image sha256:2bb539bd pulled (18.5 GB). '
            'Container ghoti-cua-smoke-n3-13 started. KasmVNC HTTP 401 confirmed at localhost:6901. '
            'No click, no type, no login, no host mounts, no privileged. '
            'Container stopped and removed. CUA NOT runtime-wired.'
        ),
    ),
    dict(
        title='Gemma3:4b local brain smoke — pull and inference smoke (N+3.13)',
        wait_type='external_result',
        repo_relative_context='14_context/gemma_local_brain_smoke_n3_13.md',
        resume_command=(
            '(see 14_context/gemma_local_brain_smoke_n3_13.md for result; '
            'if brain_inference_ready=YES: run brain-status from CLI to confirm)'
        ),
        approval_required=False,
        risk_level='low',
        notes=(
            'N+3.13: Gemma3:4b pulled via ollama pull gemma3:4b (~3.3 GB main blob). '
            'Smoke inference attempted: ollama run gemma3:4b "Return exactly: GHOTI_LOCAL_BRAIN_OK". '
            'See result doc for brain_inference_ready truth.'
        ),
    ),
    dict(
        title='Dashboard PowerShell launcher created (N+3.13)',
        wait_type='tool_available',
        repo_relative_context='03_scripts/run_dashboard.ps1',
        resume_command=(
            'powershell.exe -ExecutionPolicy Bypass -File .\\03_scripts\\run_dashboard.ps1 -OpenBrowser'
        ),
        approval_required=False,
        risk_level='low',
        notes=(
            'N+3.13: 03_scripts/run_dashboard.ps1 created. '
            'Starts Node dashboard at http://localhost:3210. No service installed. No Startup folder. '
            'Operator-triggered only. Next step: test via shortcut if desired.'
        ),
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
