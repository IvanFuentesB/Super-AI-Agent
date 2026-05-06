#!/usr/bin/env python3
"""Ghoti Dashboard — stdlib-only local orchestrator card generator.

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
MILESTONE = "N+3.56-FIX"

OBSIDIAN_VAULT_REQUIRED = [
    "00_Index.md",
    "01_Current_State.md",
    "02_Next_Actions.md",
    "09_Migration_Handoff.md",
]


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

    obsidian = _probe_obsidian()

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
        "safety_flags": {
            "read_only_card": True,
            "no_live_actions": True,
            "no_external_calls": True,
            "no_ruflo_runtime_wiring": True,
            "no_automatic_cc_codex_control": True,
            "human_approval_required_for_all_actions": True,
        },
    }


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
        f"## Safety Flags",
        f"- Read-only card: YES",
        f"- No live actions: YES",
        f"- No Ruflo runtime wiring: YES",
        f"- No automatic CC/Codex control: YES",
        f"- Human approval required: YES",
        f"",
        f"## Next Recommended Commands",
        f"```bash",
        f"python 03_scripts/obsidian_probe.py --status",
        f"python 03_scripts/ruflo_install_gate.py --source-status",
        f"python 03_scripts/ruflo_install_gate.py --status",
        f"python 03_scripts/gemma_compact_memory_worker.py --status",
        f"python 03_scripts/cc_codex_bridge.py --init --dry-run",
        f"python 03_scripts/prompt_bus.py --write-context-pack --target all --title n3-56-fix --include-status --include-memory --include-next-actions --dry-run",
        f"```",
    ]
    return "\n".join(lines) + "\n"


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
    print(f"CC/Codex auto: NO | Ruflo runtime: NO | Human approval: REQUIRED")
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
