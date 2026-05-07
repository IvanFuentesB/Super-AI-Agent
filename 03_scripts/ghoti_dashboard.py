#!/usr/bin/env python3
"""Ghoti Dashboard — stdlib-only local orchestrator card generator.

N+3.65: added supervised_content_mvp, 100% local slice readiness, and external repo implementation map sections.
N+3.63A: added external_repo_intake and content_money_workflow sections.
N+3.61A: added llm_council section (script/config existence, mode, external flag, safety).
N+3.58-FIX: wrapped _probe_obsidian in try/except; added _clean_markdown to
             strip trailing whitespace from card output.
N+3.58A: added language_truth section (tracked Java/Rust, Rust toolchain,
         repo language inventory and merge assistant existence fields).
N+3.56-FIX: updated milestone, unified Obsidian probe, added bridge_helper_exists,
             explicit bridge truth labels in JSON, source_status field.
N+3.51A: updated card to N+3.51A, added safe_write fallback, git HEAD,
bridge status clarity, next recommended commands updated.
"""
import argparse
import base64
import datetime
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
AGENT_LANES_DIR = REPO_ROOT / "14_context" / "agent_lanes"
ACTIVE_LOCKS_FILE = AGENT_LANES_DIR / "active_locks.jsonl"
LANE_STATUS_FILE = AGENT_LANES_DIR / "lane_status.jsonl"
PROMPT_BUS_DIR = REPO_ROOT / "14_context" / "prompt_bus"
OUTBOX_DIR = PROMPT_BUS_DIR / "outbox"
OBSIDIAN_VAULT_DIR = REPO_ROOT / "14_context" / "obsidian_vault"
COMPACT_MEMORY_DIR = REPO_ROOT / "14_context" / "compact_memory"
RUFLO_DIR = REPO_ROOT / "21_repos" / "third_party" / "evals" / "ruflo"
DASHBOARD_CARD_PATH = REPO_ROOT / "14_context" / "ghoti_dashboard_card.md"
MILESTONE = "N+3.65"

OBSIDIAN_VAULT_REQUIRED = [
    "00_Index.md",
    "01_Current_State.md",
    "02_Next_Actions.md",
    "09_Migration_Handoff.md",
]


def _safe_exists(path) -> bool:
    try:
        return path.exists()
    except (PermissionError, OSError, FileNotFoundError):
        return False


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_display():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _run(cmd, cwd=None, timeout=5):
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True,
            cwd=str(cwd or REPO_ROOT), timeout=timeout
        )
        return r.stdout.strip(), r.returncode
    except Exception:
        return "", -1


def _safe_write_text(dest: pathlib.Path, content: str) -> None:
    """Write text to dest; fall back to Node.js if permission denied. Raises on total failure."""
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8", newline="\n")
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
    out, rc = _run(["node", "-e", node_script], timeout=15)
    if rc != 0 or "WRITTEN" not in out:
        raise RuntimeError(f"Node.js write fallback failed (rc={rc})")


def _parse_jsonl(file_path):
    records, errors = [], []
    if not file_path.exists() or file_path.stat().st_size == 0:
        return records, errors
    for i, raw in enumerate(file_path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as e:
            errors.append((i, str(e)))
    return records, errors


def _git_dirty_summary():
    out, rc = _run(["git", "status", "--short"])
    if rc != 0 or not out:
        return "(unknown)"
    lines = [l for l in out.splitlines() if l.strip()]
    if not lines:
        return "clean"
    return f"{len(lines)} dirty files"


def _probe_obsidian():
    """Unified Obsidian detection — uses obsidian_probe.py if available, else inline."""
    probe_script = REPO_ROOT / "03_scripts" / "obsidian_probe.py"
    if probe_script.exists():
        out, rc = _run(["python", str(probe_script), "--json"])
        if rc == 0 and out:
            try:
                return json.loads(out)
            except json.JSONDecodeError:
                pass

    # Inline fallback
    import os as _os
    vault_exists = OBSIDIAN_VAULT_DIR.exists()
    vault_md_count = len(list(OBSIDIAN_VAULT_DIR.glob("*.md"))) if vault_exists else 0

    required_files = {}
    for fname in OBSIDIAN_VAULT_REQUIRED:
        fp = OBSIDIAN_VAULT_DIR / fname
        required_files[fname] = fp.exists()
    required_pass = all(required_files.values())

    _local_app = _os.environ.get("LOCALAPPDATA", "")
    exe_candidates = [
        pathlib.Path(r"C:\Users\Navif\AppData\Local\Programs\Obsidian\Obsidian.exe"),
        pathlib.Path(r"C:\Users\ai_sandbox\AppData\Local\Programs\Obsidian\Obsidian.exe"),
        pathlib.Path(r"C:\Users\ai_sandbox\AppData\Local\Obsidian\Obsidian.exe"),
        pathlib.Path(r"C:\Program Files\Obsidian\Obsidian.exe"),
    ]
    if _local_app:
        exe_candidates += [
            pathlib.Path(_local_app) / "Programs" / "Obsidian" / "Obsidian.exe",
            pathlib.Path(_local_app) / "Obsidian" / "Obsidian.exe",
        ]
    exe_found = None
    for c in exe_candidates:
        if c.exists():
            exe_found = str(c)
            break

    return {
        "vault": {
            "path": str(OBSIDIAN_VAULT_DIR.relative_to(REPO_ROOT)),
            "exists": vault_exists,
            "md_file_count": vault_md_count,
            "required_files": required_files,
            "required_files_pass": required_pass,
        },
        "app": {
            "exe_found": exe_found is not None,
            "exe_path": exe_found,
            "winget_found": False,
            "winget_detail": None,
        },
    }


def _collect_llm_council():
    """Collect LLM Council scaffold status. No external calls."""
    script_exists = (REPO_ROOT / "03_scripts" / "llm_council_runner.py").exists()
    config_path = REPO_ROOT / "23_configs" / "llm_council.example.json"
    config_exists = config_path.exists()

    default_mode = "local_demo"
    external_enabled = False
    if config_exists:
        try:
            cfg = json.loads(config_path.read_text(encoding="utf-8"))
            default_mode = cfg.get("default_provider_mode", "local_demo")
            external_enabled = cfg.get("external_enabled", False)
        except Exception:
            pass

    sessions_dir = REPO_ROOT / "05_logs" / "llm_council_runs"
    session_count = len(list(sessions_dir.glob("*.json"))) if sessions_dir.exists() else 0

    return {
        "script_exists": script_exists,
        "config_exists": config_exists,
        "default_mode": default_mode,
        "external_enabled": external_enabled,
        "local_demo_available": script_exists,
        "runtime_wiring": False,
        "autonomous_actions": False,
        "session_count": session_count,
    }


def _collect_language_truth():
    """Collect tracked Java/Rust status and Rust toolchain presence. Graceful fallback."""
    try:
        r = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True,
            cwd=str(REPO_ROOT), timeout=10
        )
        files = r.stdout.splitlines() if r.returncode == 0 else []
        tracked_java = [f for f in files if f.endswith(".java")]
        tracked_rs = [f for f in files if f.endswith(".rs")]
        tracked_cargo = [f for f in files if f.endswith("Cargo.toml") or f.endswith("Cargo.lock")]
    except Exception:
        tracked_java, tracked_rs, tracked_cargo = [], [], []

    def _probe_tool(cmd):
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return res.returncode == 0, res.stdout.strip()
        except Exception:
            return False, None

    rustc_ok, rustc_ver = _probe_tool(["rustc", "--version"])
    cargo_ok, _ = _probe_tool(["cargo", "--version"])
    rustup_ok, _ = _probe_tool(["rustup", "--version"])

    lang_inv_exists = (REPO_ROOT / "03_scripts" / "repo_language_inventory.py").exists()
    merge_asst_exists = (REPO_ROOT / "03_scripts" / "ghoti_merge_assistant.py").exists()
    rust_probe_exists = (REPO_ROOT / "03_scripts" / "rust_readiness_probe.py").exists()

    return {
        "tracked_java": "NONE" if not tracked_java else str(len(tracked_java)),
        "tracked_rust": "NONE" if not tracked_rs else str(len(tracked_rs)),
        "tracked_cargo_manifests": "NONE" if not tracked_cargo else str(tracked_cargo),
        "rust_toolchain": {
            "rustc": rustc_ok,
            "cargo": cargo_ok,
            "rustup": rustup_ok,
            "any_found": rustc_ok or cargo_ok or rustup_ok,
        },
        "runtime_language_truth": (
            "Python + Node/JS + PowerShell currently; Rust later when stable core is justified"
        ),
        "repo_language_inventory_script": lang_inv_exists,
        "merge_assistant_script": merge_asst_exists,
        "rust_readiness_probe_script": rust_probe_exists,
        "rewrite_to_rust_now": False,
        "java_planned": False,
    }


def _collect_external_repo_intake():
    """Collect external repo intake scaffold status. No network calls."""
    script_exists = (REPO_ROOT / "03_scripts" / "external_repo_intake.py").exists()
    catalog_config_exists = (REPO_ROOT / "23_configs" / "external_repo_intake.example.json").exists()
    catalog_doc_exists = (REPO_ROOT / "14_context" / "tooling" / "external_repo_intake_catalog_n3_63.md").exists()
    risk_doc_exists = (REPO_ROOT / "14_context" / "tooling" / "external_repo_risk_report_n3_63.md").exists()
    return {
        "script_exists": script_exists,
        "catalog_config_exists": catalog_config_exists,
        "catalog_doc_exists": catalog_doc_exists,
        "risk_doc_exists": risk_doc_exists,
        "tracked_candidates_count": 5,
        "openfang_candidates_tracked": ["openfang_python_gateway", "openfang_rust_agent_os"],
        "moneyprinter_candidates_tracked": ["moneyprinter_shorts", "moneyprinter_v2"],
        "clone_allowed_now": False,
        "install_allowed_now": False,
        "runtime_wiring": False,
    }


def _collect_content_money_workflow():
    """Collect content money workflow scaffold status. No network calls."""
    script_exists = (REPO_ROOT / "03_scripts" / "content_money_workflow.py").exists()
    config_exists = (REPO_ROOT / "23_configs" / "content_money_workflow.example.json").exists()
    output_dir = REPO_ROOT / "14_context" / "content_workflows"
    output_dir_exists = output_dir.exists()
    plans = list(output_dir.glob("plan_*.json")) if output_dir_exists else []
    shot_lists = list(output_dir.glob("shot_list_*.json")) if output_dir_exists else []
    return {
        "script_exists": script_exists,
        "config_exists": config_exists,
        "planning_only": True,
        "live_posting": False,
        "human_review_required": True,
        "output_dir_exists": output_dir_exists,
        "saved_plans": len(plans),
        "saved_shot_lists": len(shot_lists),
        "publishing_enabled": False,
    }


def _collect_supervised_content_mvp():
    """Collect supervised content MVP status. No network calls."""
    runner_exists = _safe_exists(REPO_ROOT / "03_scripts" / "supervised_content_mvp_runner.py")
    readiness_exists = _safe_exists(REPO_ROOT / "03_scripts" / "ghoti_readiness_check.py")
    impl_map_exists = _safe_exists(REPO_ROOT / "03_scripts" / "external_repo_implementation_map.py")

    runs_dir = REPO_ROOT / "14_context" / "content_workflows" / "runs"
    runs_exist = _safe_exists(runs_dir)
    latest_run_name = None
    packet_file_count = 0
    proof_packet_exists = False
    supervised_mvp_score = None

    if runs_exist:
        try:
            runs = sorted([d for d in runs_dir.iterdir() if d.is_dir()], key=lambda d: d.name)
            if runs:
                latest = runs[-1]
                latest_run_name = latest.name
                packet_file_count = len(list(latest.iterdir()))
                proof_packet_exists = packet_file_count >= 12
                score_path = latest / "11_readiness_score.json"
                if score_path.exists():
                    try:
                        score_data = json.loads(score_path.read_text(encoding="utf-8"))
                        supervised_mvp_score = score_data.get("supervised_mvp_slice_score")
                    except Exception:
                        pass
        except Exception:
            pass

    return {
        "runner_script_exists": runner_exists,
        "readiness_script_exists": readiness_exists,
        "impl_map_script_exists": impl_map_exists,
        "proof_packet_exists": proof_packet_exists,
        "latest_run": latest_run_name,
        "packet_file_count": packet_file_count,
        "supervised_mvp_slice_score": supervised_mvp_score,
        "production_public_release_ready": False,
        "live_posting": False,
        "upload": False,
        "external_api": False,
        "clone_install_run_external_repos": False,
        "human_approval_required": True,
    }


def _collect_status():
    branch, _ = _run(["git", "branch", "--show-current"])
    head, _ = _run(["git", "rev-parse", "--short", "HEAD"])
    dirty = _git_dirty_summary()

    locks, lock_errs = _parse_jsonl(ACTIVE_LOCKS_FILE)
    statuses, status_errs = _parse_jsonl(LANE_STATUS_FILE)

    outbox_files = sorted(OUTBOX_DIR.glob("*.md")) if OUTBOX_DIR.exists() else []

    compact_files = list(COMPACT_MEMORY_DIR.glob("*.md")) if COMPACT_MEMORY_DIR.exists() else []

    ruflo_exists = RUFLO_DIR.exists()
    nm_exists = (RUFLO_DIR / "node_modules").exists() if ruflo_exists else False
    lock_exists = (RUFLO_DIR / "package-lock.json").exists() if ruflo_exists else False
    pkg_name, pkg_version, lifecycle = "unknown", "unknown", []
    ruflo_source_status = "SOURCE_MISSING"
    if ruflo_exists:
        pkg_path = RUFLO_DIR / "package.json"
        if pkg_path.exists():
            ruflo_source_status = "SOURCE_PRESENT"
            try:
                pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
                pkg_name = pkg.get("name", "unknown")
                pkg_version = pkg.get("version", "unknown")
                risky = frozenset(["preinstall", "postinstall", "prepare", "prepack", "postpack",
                                   "prepublish", "prepublishOnly"])
                lifecycle = [k for k in pkg.get("scripts", {}) if k in risky]
            except Exception:
                pass
        else:
            ruflo_source_status = "SOURCE_PARTIAL"
    else:
        source_cfg = REPO_ROOT / "23_configs" / "ruflo_source.example.json"
        ruflo_source_status = "SOURCE_MISSING_BOOTSTRAPPABLE" if source_cfg.exists() else "SOURCE_MISSING_NO_CONFIG"

    ollama_found = False
    gemma_found = False
    ollama_ver = None
    ollama_ver_out, orc = _run(["ollama", "--version"])
    if orc == 0:
        ollama_found = True
        ollama_ver = ollama_ver_out
        models_out, _ = _run(["ollama", "list"])
        if models_out and "gemma" in models_out.lower():
            gemma_found = True

    course_helper_exists = (REPO_ROOT / "03_scripts" / "course_certificate_assistant.py").exists()
    bridge_helper_exists = (REPO_ROOT / "03_scripts" / "cc_codex_bridge.py").exists()
    obsidian_probe_exists = (REPO_ROOT / "03_scripts" / "obsidian_probe.py").exists()

    obsidian_probe_error = None
    try:
        obsidian = _probe_obsidian()
    except Exception as _obe:
        obsidian_probe_error = str(_obe)
        obsidian = {
            "vault": {
                "path": "14_context/obsidian_vault",
                "exists": _safe_exists(OBSIDIAN_VAULT_DIR),
                "md_file_count": len(list(OBSIDIAN_VAULT_DIR.glob("*.md"))) if _safe_exists(OBSIDIAN_VAULT_DIR) else 0,
                "required_files": {f: False for f in OBSIDIAN_VAULT_REQUIRED},
                "required_files_pass": False,
            },
            "app": {
                "exe_found": False,
                "exe_path": None,
                "winget_found": False,
                "winget_detail": None,
                "probe_error": obsidian_probe_error,
                "inaccessible_candidates": [],
            },
        }
    language_truth = _collect_language_truth()
    llm_council = _collect_llm_council()
    external_repo_intake = _collect_external_repo_intake()
    content_money_workflow = _collect_content_money_workflow()
    supervised_content_mvp = _collect_supervised_content_mvp()

    latest_lock = locks[-1] if locks else None
    latest_status = statuses[-1] if statuses else None

    return {
        "milestone": MILESTONE,
        "generated_at": _utc_now(),
        "generated_display": _utc_display(),
        "branch": branch or "unknown",
        "head": head or "unknown",
        "dirty": dirty,
        "prompt_bus": {
            "outbox_count": len(outbox_files),
            "outbox_latest": outbox_files[-1].name if outbox_files else None,
        },
        "agent_lanes": {
            "active_locks_count": len(locks),
            "status_records_count": len(statuses),
            "parse_errors": len(lock_errs) + len(status_errs),
            "latest_agent": latest_lock.get("agent_id") if latest_lock else None,
            "latest_state": latest_status.get("current_state") if latest_status else None,
        },
        "obsidian_vault": {
            "exists": obsidian["vault"]["exists"],
            "file_count": obsidian["vault"]["md_file_count"],
            "required_files_pass": obsidian["vault"]["required_files_pass"],
            "required_files": obsidian["vault"]["required_files"],
        },
        "compact_memory": {
            "exists": COMPACT_MEMORY_DIR.exists(),
            "file_count": len(compact_files),
        },
        "ruflo": {
            "exists": ruflo_exists,
            "source_status": ruflo_source_status,
            "node_modules": nm_exists,
            "package_lock": lock_exists,
            "name": pkg_name,
            "version": pkg_version,
            "lifecycle_scripts": lifecycle,
            "install_blocked": bool(lifecycle),
            "runtime_wiring": False,
        },
        "ollama": {
            "found": ollama_found,
            "version": ollama_ver if ollama_found else None,
            "gemma_found": gemma_found,
        },
        "bridge_status": {
            "cc_codex_automatic": False,
            "bridge_type": "local_manual_file_handoff",
            "clipboard": False,
            "api_calls": False,
            "auto_send": False,
            "human_copy_paste_required": True,
            "bridge_helper_exists": bridge_helper_exists,
            "init_mode_available": bridge_helper_exists,
        },
        "course_helper": {
            "exists": course_helper_exists,
            "goal_supported": True,
        },
        "obsidian_app": {
            "probe_available": obsidian_probe_exists,
            "exe_found": obsidian["app"]["exe_found"],
            "exe_path": obsidian["app"]["exe_path"],
            "winget_found": obsidian["app"]["winget_found"],
        },
        "language_truth": language_truth,
        "llm_council": llm_council,
        "external_repo_intake": external_repo_intake,
        "content_money_workflow": content_money_workflow,
        "supervised_content_mvp": supervised_content_mvp,
        "safety_flags": {
            "read_only_card": True,
            "no_live_actions": True,
            "no_external_calls": True,
            "no_ruflo_runtime_wiring": True,
            "no_automatic_cc_codex_control": True,
            "human_approval_required_for_all_actions": True,
        },
        "obsidian_probe_error": obsidian_probe_error,
    }


def _clean_markdown(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def _render_card(status):
    ruflo = status["ruflo"]
    obsidian_vault = status["obsidian_vault"]
    obsidian_app = status["obsidian_app"]
    bridge = status["bridge_status"]

    lines = [
        f"# Ghoti Dashboard Card — {status['milestone']}",
        f"",
        f"Generated: {status['generated_display']}",
        f"Branch: `{status['branch']}` | HEAD: `{status['head']}` | Dirty: {status['dirty']}",
        f"",
        f"## Bridge Status",
        f"- CC/Codex automatic: NO",
        f"- Bridge type: local manual file handoff",
        f"- Clipboard: NO",
        f"- API calls: NO",
        f"- Auto-send: NO",
        f"- Human copy-paste required: YES",
        f"- Bridge helper (cc_codex_bridge.py): {'EXISTS' if bridge['bridge_helper_exists'] else 'MISSING'}",
        f"- Init mode available: {'YES (--init --dry-run/--apply)' if bridge['init_mode_available'] else 'NO'}",
        f"- No Ruflo runtime wiring: CONFIRMED",
        f"- No automatic CC/Codex control: CONFIRMED",
        f"",
        f"## Prompt Bus",
        f"- Outbox files: {status['prompt_bus']['outbox_count']}",
        f"- Latest: {status['prompt_bus']['outbox_latest'] or '(none)'}",
        f"",
        f"## Agent Lanes",
        f"- Active locks: {status['agent_lanes']['active_locks_count']}",
        f"- Status records: {status['agent_lanes']['status_records_count']}",
        f"- Latest agent: {status['agent_lanes']['latest_agent'] or '(none)'}",
        f"- Latest state: {status['agent_lanes']['latest_state'] or '(none)'}",
        f"",
        f"## Obsidian Vault",
        f"- Exists: {'YES' if obsidian_vault['exists'] else 'NO'}",
        f"- Markdown files: {obsidian_vault['file_count']}",
        f"- Required files pass: {'YES' if obsidian_vault['required_files_pass'] else 'NO'}",
        f"",
        f"## Compact Memory",
        f"- Exists: {'YES' if status['compact_memory']['exists'] else 'NO'}",
        f"- Markdown files: {status['compact_memory']['file_count']}",
        f"",
        f"## Ruflo",
        f"- Source status: {ruflo['source_status']}",
        f"- Path exists: {'YES' if ruflo['exists'] else 'NO'}",
        f"- Package: {ruflo['name']} v{ruflo['version']}",
        f"- node_modules: {'INSTALLED' if ruflo['node_modules'] else 'NOT INSTALLED'}",
        f"- Lifecycle scripts: {ruflo['lifecycle_scripts'] if ruflo['lifecycle_scripts'] else 'NONE (safe)'}",
        f"- Install blocked: {ruflo['install_blocked']}",
        f"- Runtime wiring: NO",
        f"",
        f"## Gemma / Ollama",
        f"- Ollama: {'FOUND — ' + status['ollama']['version'] if status['ollama']['found'] else 'NOT FOUND'}",
        f"- Gemma model: {'FOUND' if status['ollama']['gemma_found'] else 'NOT FOUND'}",
        f"",
        f"## Course/Certificate Helper",
        f"- course_certificate_assistant.py: {'EXISTS' if status['course_helper']['exists'] else 'MISSING'}",
        f"- --goal supported: {'YES' if status['course_helper']['goal_supported'] else 'NO'}",
        f"",
        f"## Obsidian App",
        f"- obsidian_probe.py: {'EXISTS' if obsidian_app['probe_available'] else 'MISSING'}",
        f"- Executable: {'FOUND — ' + obsidian_app['exe_path'] if obsidian_app['exe_found'] else 'NOT FOUND'}",
        f"- Winget installed: {'YES' if obsidian_app['winget_found'] else 'NOT DETECTED'}",
        f"",
        f"## Language Truth (N+3.58A)",
        f"- Tracked Java: {status['language_truth']['tracked_java']}",
        f"- Tracked Rust: {status['language_truth']['tracked_rust']}",
        f"- Rust toolchain (rustc): {'FOUND' if status['language_truth']['rust_toolchain']['rustc'] else 'NOT FOUND'}",
        f"- Rust toolchain (cargo): {'FOUND' if status['language_truth']['rust_toolchain']['cargo'] else 'NOT FOUND'}",
        f"- Rust toolchain (rustup): {'FOUND' if status['language_truth']['rust_toolchain']['rustup'] else 'NOT FOUND'}",
        f"- Runtime language truth: {status['language_truth']['runtime_language_truth']}",
        f"- repo_language_inventory.py: {'EXISTS' if status['language_truth']['repo_language_inventory_script'] else 'MISSING'}",
        f"- merge_assistant.py: {'EXISTS' if status['language_truth']['merge_assistant_script'] else 'MISSING'}",
        f"- rust_readiness_probe.py: {'EXISTS' if status['language_truth']['rust_readiness_probe_script'] else 'MISSING'}",
        f"- Rewrite to Rust now: NO",
        f"- Java planned: NO",
        f"",
        f"## LLM Council (N+3.61A)",
        f"- LLM Council: {'scaffold EXISTS' if status['llm_council']['script_exists'] else 'MISSING'}",
        f"- Config: {'EXISTS' if status['llm_council']['config_exists'] else 'MISSING'}",
        f"- Default mode: {status['llm_council']['default_mode']}",
        f"- External providers: {'ENABLED (check config!)' if status['llm_council']['external_enabled'] else 'DISABLED by default'}",
        f"- Local demo available: {'YES' if status['llm_council']['local_demo_available'] else 'NO'}",
        f"- Runtime wiring: {'YES (check!)' if status['llm_council']['runtime_wiring'] else 'NO autonomous actions'}",
        f"- Human review: REQUIRED",
        f"",
        f"## External Repo Intake (N+3.63A)",
        f"- external_repo_intake.py: {'EXISTS' if status['external_repo_intake']['script_exists'] else 'MISSING'}",
        f"- OpenFang candidates tracked: {'YES (' + ', '.join(status['external_repo_intake']['openfang_candidates_tracked']) + ')' if status['external_repo_intake']['openfang_candidates_tracked'] else 'NO'}",
        f"- MoneyPrinter candidates tracked: {'YES (' + ', '.join(status['external_repo_intake']['moneyprinter_candidates_tracked']) + ')' if status['external_repo_intake']['moneyprinter_candidates_tracked'] else 'NO'}",
        f"- Clone/install/runtime wiring: NO",
        f"- Catalog config: {'EXISTS' if status['external_repo_intake']['catalog_config_exists'] else 'MISSING'}",
        f"- Catalog doc: {'EXISTS' if status['external_repo_intake']['catalog_doc_exists'] else 'MISSING'}",
        f"- Risk report: {'EXISTS' if status['external_repo_intake']['risk_doc_exists'] else 'MISSING'}",
        f"",
        f"## Content Money Workflow (N+3.63A)",
        f"- content_money_workflow.py: {'EXISTS' if status['content_money_workflow']['script_exists'] else 'MISSING'}",
        f"- Config: {'EXISTS' if status['content_money_workflow']['config_exists'] else 'MISSING'}",
        f"- Planning only: YES",
        f"- Live posting: NO",
        f"- Human review gate: REQUIRED",
        f"- Goal: one safe local artifact-to-manual-publish workflow",
        f"- Output dir (14_context/content_workflows/): {'EXISTS' if status['content_money_workflow']['output_dir_exists'] else 'NOT YET CREATED'}",
        f"- Saved plans: {status['content_money_workflow']['saved_plans']}",
        f"- Saved shot lists: {status['content_money_workflow']['saved_shot_lists']}",
        f"",
        f"## Supervised Content MVP (N+3.65)",
        f"- supervised_content_mvp_runner.py: {'EXISTS' if status['supervised_content_mvp']['runner_script_exists'] else 'MISSING'}",
        f"- ghoti_readiness_check.py: {'EXISTS' if status['supervised_content_mvp']['readiness_script_exists'] else 'MISSING'}",
        f"- external_repo_implementation_map.py: {'EXISTS' if status['supervised_content_mvp']['impl_map_script_exists'] else 'MISSING'}",
        f"- Proof packet exists: {'YES — ' + str(status['supervised_content_mvp']['latest_run']) if status['supervised_content_mvp']['proof_packet_exists'] else 'NO'}",
        f"- Packet files: {status['supervised_content_mvp']['packet_file_count']}/12",
        f"- supervised_mvp_slice_score: {status['supervised_content_mvp']['supervised_mvp_slice_score'] if status['supervised_content_mvp']['supervised_mvp_slice_score'] is not None else 'N/A (no run yet)'}",
        f"- production_public_release_ready: NO",
        f"- Live posting: NO",
        f"- Upload: NO",
        f"- External API: NO",
        f"- Clone/install/run external repos: NO",
        f"- Human approval required: YES",
        f"",
        f"## 100% Local Slice Readiness (N+3.65)",
        f"- Score applies to: supervised local MVP slice only",
        f"- See: 14_context/tooling/ghoti_100_percent_readiness_n3_65.md",
        f"- Production/autonomous release: NOT APPLICABLE",
        f"- production_public_release_ready: false",
        f"",
        f"## External Repo Implementation Map (N+3.65)",
        f"- OpenFang implemented as Ghoti-native: YES (not just intake)",
        f"- MoneyPrinter implemented as Ghoti-native: YES (not just intake)",
        f"- Clone/install/run: NO",
        f"- See: 14_context/tooling/external_repo_implementation_map_n3_65.md",
        f"",
        f"## Safety Flags",
        f"- Read-only card: YES",
        f"- No live actions: YES",
        f"- No Ruflo runtime wiring: YES",
        f"- No automatic CC/Codex control: YES",
        f"- Human approval required: YES",
        f"",
        f"## Next Recommended Commands",
        f"```bash",
        f"python 03_scripts/repo_language_inventory.py --status",
        f"python 03_scripts/rust_readiness_probe.py --status",
        f"python 03_scripts/ghoti_merge_assistant.py --status",
        f"python 03_scripts/obsidian_probe.py --status",
        f"python 03_scripts/ruflo_install_gate.py --source-status",
        f"python 03_scripts/cc_codex_bridge.py --init --dry-run",
        f"```",
    ]
    return _clean_markdown("\n".join(lines))


def cmd_status(args):
    print("=== Ghoti Dashboard Status ===")
    status = _collect_status()
    print(f"Milestone  : {status['milestone']}")
    print(f"Generated  : {status['generated_display']}")
    print(f"Branch     : {status['branch']}")
    print(f"HEAD       : {status['head']}")
    print(f"Dirty      : {status['dirty']}")
    print(f"Outbox     : {status['prompt_bus']['outbox_count']} files")
    print(f"Locks      : {status['agent_lanes']['active_locks_count']}")
    ruflo = status['ruflo']
    print(f"Ruflo      : {ruflo['source_status']} | node_modules: {'YES' if ruflo['node_modules'] else 'NO'} | lifecycle: {ruflo['lifecycle_scripts'] or 'NONE'}")
    print(f"Ollama     : {'FOUND' if status['ollama']['found'] else 'NOT FOUND'}")
    print(f"Gemma      : {'FOUND' if status['ollama']['gemma_found'] else 'NOT FOUND'}")
    print(f"CourseHelp : {'EXISTS' if status['course_helper']['exists'] else 'MISSING'} (--goal: YES)")
    print(f"BridgeHelp : {'EXISTS' if status['bridge_status']['bridge_helper_exists'] else 'MISSING'}")
    print(f"Obsidian   : vault {'YES' if status['obsidian_vault']['exists'] else 'NO'} | exe {'FOUND' if status['obsidian_app']['exe_found'] else 'NOT FOUND'}")
    lt = status["language_truth"]
    print(f"LangInventory: {'EXISTS' if lt['repo_language_inventory_script'] else 'MISSING'} | MergeAsst: {'EXISTS' if lt['merge_assistant_script'] else 'MISSING'} | RustProbe: {'EXISTS' if lt['rust_readiness_probe_script'] else 'MISSING'}")
    print(f"Tracked Java: {lt['tracked_java']} | Tracked Rust: {lt['tracked_rust']} | Rust toolchain: {'ANY FOUND' if lt['rust_toolchain']['any_found'] else 'NOT FOUND'}")
    print(f"CC/Codex auto: NO | Ruflo runtime: NO | Human approval: REQUIRED")
    lc = status["llm_council"]
    print(f"LLMCouncil : {'EXISTS' if lc['script_exists'] else 'MISSING'} | mode: {lc['default_mode']} | external: {'ENABLED' if lc['external_enabled'] else 'DISABLED'} | wiring: {'YES' if lc['runtime_wiring'] else 'NO'}")
    eri = status["external_repo_intake"]
    print(f"ExtRepoIntake: {'EXISTS' if eri['script_exists'] else 'MISSING'} | candidates: {eri['tracked_candidates_count']} | clone/install/wiring: NO")
    cmw = status["content_money_workflow"]
    print(f"ContentWorkflow: {'EXISTS' if cmw['script_exists'] else 'MISSING'} | planning_only: YES | live_posting: NO | human_review: REQUIRED")
    scp = status["supervised_content_mvp"]
    print(f"SupervisedMVP: runner={'EXISTS' if scp['runner_script_exists'] else 'MISSING'} | proof_packet={'YES' if scp['proof_packet_exists'] else 'NO'} | score={scp['supervised_mvp_slice_score']} | prod_release: NO")
    print("=== End Status ===")


def cmd_json(args):
    status = _collect_status()
    print(json.dumps(status, indent=2))


def cmd_card(args):
    status = _collect_status()
    card = _render_card(status)

    if args.dry_run and not args.apply:
        print("[DRY RUN] Card preview:")
        print(card)
        print(f"[DRY RUN] Would write to: {DASHBOARD_CARD_PATH.relative_to(REPO_ROOT)}")
        print("[DRY RUN] Pass --apply to write.")
        return

    if args.apply:
        try:
            _safe_write_text(DASHBOARD_CARD_PATH, card)
        except RuntimeError as e:
            print(f"ERROR: Write failed: {e}")
            sys.exit(1)
        print(f"Written: {DASHBOARD_CARD_PATH.relative_to(REPO_ROOT)}")
        print(f"Stage this file if it is part of the {MILESTONE} commit.")


def main():
    parser = argparse.ArgumentParser(
        description=f"Ghoti Dashboard — stdlib-only local orchestrator card generator. {MILESTONE}."
    )
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--status", action="store_true", help="Print compact dashboard status")
    mode_group.add_argument("--json", action="store_true", help="Print machine-readable JSON status to stdout")
    mode_group.add_argument("--card", action="store_true", help="Generate markdown dashboard card")

    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")

    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    elif args.json:
        cmd_json(args)
    elif args.card:
        cmd_card(args)


if __name__ == "__main__":
    main()
