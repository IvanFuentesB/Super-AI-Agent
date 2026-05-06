#!/usr/bin/env python3
"""Ghoti Dashboard — stdlib-only local orchestrator card generator."""
import argparse
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


def _collect_status():
    branch, _ = _run(["git", "branch", "--show-current"])
    head, _ = _run(["git", "rev-parse", "--short", "HEAD"])

    locks, lock_errs = _parse_jsonl(ACTIVE_LOCKS_FILE)
    statuses, status_errs = _parse_jsonl(LANE_STATUS_FILE)

    outbox_files = sorted(OUTBOX_DIR.glob("*.md")) if OUTBOX_DIR.exists() else []

    obsidian_files = list(OBSIDIAN_VAULT_DIR.glob("*.md")) if OBSIDIAN_VAULT_DIR.exists() else []
    compact_files = list(COMPACT_MEMORY_DIR.glob("*.md")) if COMPACT_MEMORY_DIR.exists() else []

    ruflo_exists = RUFLO_DIR.exists()
    nm_exists = (RUFLO_DIR / "node_modules").exists() if ruflo_exists else False
    lock_exists = (RUFLO_DIR / "package-lock.json").exists() if ruflo_exists else False
    pkg_name, pkg_version, lifecycle = "unknown", "unknown", []
    if ruflo_exists:
        pkg_path = RUFLO_DIR / "package.json"
        if pkg_path.exists():
            try:
                pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
                pkg_name = pkg.get("name", "unknown")
                pkg_version = pkg.get("version", "unknown")
                risky = frozenset(["preinstall", "postinstall", "prepare", "prepack", "postpack",
                                   "prepublish", "prepublishOnly"])
                lifecycle = [k for k in pkg.get("scripts", {}) if k in risky]
            except Exception:
                pass

    ollama_found = False
    gemma_found = False
    ollama_ver, orc = _run(["ollama", "--version"])
    if orc == 0:
        ollama_found = True
        models_out, _ = _run(["ollama", "list"])
        if models_out and "gemma" in models_out.lower():
            gemma_found = True

    latest_lock = locks[-1] if locks else None
    latest_status = statuses[-1] if statuses else None

    return {
        "generated_at": _utc_now(),
        "generated_display": _utc_display(),
        "branch": branch or "unknown",
        "head": head or "unknown",
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
            "exists": OBSIDIAN_VAULT_DIR.exists(),
            "file_count": len(obsidian_files),
        },
        "compact_memory": {
            "exists": COMPACT_MEMORY_DIR.exists(),
            "file_count": len(compact_files),
        },
        "ruflo": {
            "exists": ruflo_exists,
            "node_modules": nm_exists,
            "package_lock": lock_exists,
            "name": pkg_name,
            "version": pkg_version,
            "lifecycle_scripts": lifecycle,
            "install_blocked": bool(lifecycle),
        },
        "ollama": {
            "found": ollama_found,
            "version": ollama_ver if ollama_found else None,
            "gemma_found": gemma_found,
        },
        "safety_flags": {
            "read_only_card": True,
            "no_live_actions": True,
            "no_external_calls": True,
            "human_approval_required_for_all_actions": True,
        },
    }


def _render_card(status):
    lines = [
        f"# Ghoti Dashboard Card — N+3.50A",
        f"",
        f"Generated: {status['generated_display']}",
        f"Branch: `{status['branch']}` | HEAD: `{status['head']}`",
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
        f"- Exists: {'YES' if status['obsidian_vault']['exists'] else 'NO'}",
        f"- Markdown files: {status['obsidian_vault']['file_count']}",
        f"",
        f"## Compact Memory",
        f"- Exists: {'YES' if status['compact_memory']['exists'] else 'NO'}",
        f"- Markdown files: {status['compact_memory']['file_count']}",
        f"",
        f"## Ruflo",
        f"- Path exists: {'YES' if status['ruflo']['exists'] else 'NO'}",
        f"- Package: {status['ruflo']['name']} v{status['ruflo']['version']}",
        f"- node_modules: {'INSTALLED' if status['ruflo']['node_modules'] else 'NOT INSTALLED'}",
        f"- Lifecycle scripts: {status['ruflo']['lifecycle_scripts'] if status['ruflo']['lifecycle_scripts'] else 'NONE (safe)'}",
        f"- Install blocked: {status['ruflo']['install_blocked']}",
        f"",
        f"## Gemma / Ollama",
        f"- Ollama: {'FOUND' if status['ollama']['found'] else 'NOT FOUND'}",
        f"- Gemma model: {'FOUND' if status['ollama']['gemma_found'] else 'NOT FOUND'}",
        f"",
        f"## Safety Flags",
        f"- Read-only card: YES",
        f"- No live actions: YES",
        f"- Human approval required: YES",
        f"",
        f"## Next Recommended Commands",
        f"```bash",
        f"python 03_scripts/ghoti_dashboard.py --json",
        f"python 03_scripts/ruflo_install_gate.py --status",
        f"python 03_scripts/gemma_compact_memory_worker.py --status",
        f"python 03_scripts/prompt_bus.py --write-context-pack --target all --title n3-50 --dry-run",
        f"```",
    ]
    return "\n".join(lines) + "\n"


def cmd_status(args):
    print("=== Ghoti Dashboard Status ===")
    status = _collect_status()
    print(f"Generated  : {status['generated_display']}")
    print(f"Branch     : {status['branch']}")
    print(f"HEAD       : {status['head']}")
    print(f"Outbox     : {status['prompt_bus']['outbox_count']} files")
    print(f"Locks      : {status['agent_lanes']['active_locks_count']}")
    print(f"Ruflo      : {'EXISTS' if status['ruflo']['exists'] else 'MISSING'}")
    print(f"Ollama     : {'FOUND' if status['ollama']['found'] else 'NOT FOUND'}")
    print(f"Gemma      : {'FOUND' if status['ollama']['gemma_found'] else 'NOT FOUND'}")
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
        DASHBOARD_CARD_PATH.write_text(card, encoding="utf-8")
        print(f"Written: {DASHBOARD_CARD_PATH.relative_to(REPO_ROOT)}")
        print("Stage this file if it is part of the N+3.50A commit.")


def main():
    parser = argparse.ArgumentParser(
        description="Ghoti Dashboard — stdlib-only local orchestrator card generator."
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
