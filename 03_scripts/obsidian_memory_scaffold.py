#!/usr/bin/env python3
"""
obsidian_memory_scaffold.py — N+3.34

Checks and scaffolds Obsidian vault and compact memory files.
Stdlib only. No external APIs. No model calls. No installs. No live actions.

Usage:
    python 03_scripts/obsidian_memory_scaffold.py --help
    python 03_scripts/obsidian_memory_scaffold.py --check
    python 03_scripts/obsidian_memory_scaffold.py --dry-run
    python 03_scripts/obsidian_memory_scaffold.py --apply
    python 03_scripts/obsidian_memory_scaffold.py --apply --force
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

VAULT_DIR = REPO_ROOT / "14_context" / "obsidian_vault"
COMPACT_DIR = REPO_ROOT / "14_context" / "compact_memory"

VAULT_FILES = [
    "00_Index.md",
    "01_Current_State.md",
    "02_Next_Actions.md",
    "03_Decisions.md",
    "04_Tools_And_Repos.md",
    "05_Money_OS.md",
    "06_Safety_Gates.md",
    "07_Agent_Routing.md",
    "08_Dirty_State.md",
    "09_Migration_Handoff.md",
]

COMPACT_FILES = [
    "project_state.md",
    "repo_and_tool_index.md",
    "money_os_memory.md",
    "agent_routing_memory.md",
    "safety_rules.md",
    "dirty_state_warning.md",
]

VAULT_TEMPLATES = {
    "00_Index.md": (
        "# Ghoti Vault Index\n\n"
        "**Updated:** (stub)\n\n"
        "> Source: vault scaffold. Populate from `14_context/current_state.md`.\n"
    ),
    "01_Current_State.md": (
        "# Ghoti Current State (Compact)\n\n"
        "**Updated:** (stub)\n\n"
        "> Source: `14_context/current_state.md`\n"
    ),
    "02_Next_Actions.md": (
        "# Ghoti Next Actions (Compact)\n\n"
        "**Updated:** (stub)\n\n"
        "> Source: `14_context/next_actions.md`\n"
    ),
    "03_Decisions.md": (
        "# Ghoti Decisions (Compact)\n\n"
        "**Updated:** (stub)\n\n"
        "> Source: Codex planning docs in `14_context/`\n"
    ),
    "04_Tools_And_Repos.md": (
        "# Ghoti Tools And Repos (Compact)\n\n"
        "**Updated:** (stub)\n\n"
        "> Source: `14_context/obsidian_vault/04_Tools.md`, `14_context/tooling_intake_priority_n3_17.md`\n"
    ),
    "05_Money_OS.md": (
        "# Ghoti Money OS (Compact)\n\n"
        "**Updated:** (stub)\n\n"
        "> Source: `14_context/money_workflows/money_os_index.md`\n"
    ),
    "06_Safety_Gates.md": (
        "# Ghoti Safety Gates (Canonical)\n\n"
        "**Updated:** (stub)\n\n"
        "> Source: CLAUDE.md, `14_context/codex_n3_34_memory_safety_gate_review.md`\n"
    ),
    "07_Agent_Routing.md": (
        "# Ghoti Agent Routing (Compact)\n\n"
        "**Updated:** (stub)\n\n"
        "> Source: `14_context/agent_registry/agent_routing_policy_n3_14.md`\n"
    ),
    "08_Dirty_State.md": (
        "# Ghoti Dirty State Warning\n\n"
        "**Updated:** (stub)\n\n"
        "> Source: `git status --short`\n"
    ),
    "09_Migration_Handoff.md": (
        "# Ghoti Migration Handoff\n\n"
        "**Updated:** (stub)\n\n"
        "> Source: `14_context/current_state.md`, `14_context/next_actions.md`\n"
    ),
}

_COMPACT_HEADER = (
    "---\n"
    "memory_type: compact_pointer\n"
    "status: stub\n"
    "last_updated: (stub)\n"
    "source_files:\n"
    "  - (populate from source)\n"
    "generated_by: scaffold\n"
    "reviewed_by: none\n"
    "review_required_before_canonical_use: true\n"
    "---\n\n"
)

COMPACT_TEMPLATES = {
    "project_state.md": (
        _COMPACT_HEADER
        + "# Compact: Project State\n\n"
        + "> WARNING: stub only. Populate from `14_context/current_state.md`.\n"
    ),
    "repo_and_tool_index.md": (
        _COMPACT_HEADER
        + "# Compact: Repo and Tool Index\n\n"
        + "> WARNING: stub only. Populate from tool docs.\n"
    ),
    "money_os_memory.md": (
        _COMPACT_HEADER
        + "# Compact: Money OS Memory\n\n"
        + "> WARNING: stub only. Populate from money workflow docs.\n"
    ),
    "agent_routing_memory.md": (
        _COMPACT_HEADER
        + "# Compact: Agent Routing Memory\n\n"
        + "> WARNING: stub only. Populate from routing policy docs.\n"
    ),
    "safety_rules.md": (
        _COMPACT_HEADER
        + "# Compact: Safety Rules\n\n"
        + "> WARNING: stub only. CLAUDE.md is authoritative.\n"
    ),
    "dirty_state_warning.md": (
        _COMPACT_HEADER
        + "# Compact: Dirty State Warning\n\n"
        + "> WARNING: stub only. Run `git status --short` for current truth.\n"
    ),
}


def _classify(fname, dir_label):
    return (fname, dir_label)


def _check_results():
    results = []
    for fname in VAULT_FILES:
        path = VAULT_DIR / fname
        results.append((fname, "vault", path.exists()))
    for fname in COMPACT_FILES:
        path = COMPACT_DIR / fname
        results.append((fname, "compact_memory", path.exists()))
    return results


def check_files():
    results = _check_results()
    present = [(f, d) for f, d, ok in results if ok]
    missing = [(f, d) for f, d, ok in results if not ok]

    print("=== Obsidian Memory Scaffold Check ===")
    for fname, dname in present:
        print(f"  [OK]     {dname}/{fname}")
    for fname, dname in missing:
        print(f"  [MISS]   {dname}/{fname}")

    total = len(VAULT_FILES) + len(COMPACT_FILES)
    print(f"\nPresent: {len(present)} / {total}")
    print(f"Missing: {len(missing)}")

    return missing


def dry_run():
    results = _check_results()
    missing = [(f, d) for f, d, ok in results if not ok]

    total = len(VAULT_FILES) + len(COMPACT_FILES)
    present_count = total - len(missing)

    print("=== Obsidian Memory Scaffold Dry-Run ===")
    print(f"Present: {present_count} / {total}")

    if not missing:
        print("\nAll expected files already exist. Nothing to create.")
        return

    print(f"\nWould create {len(missing)} missing file(s):")
    for fname, dname in missing:
        print(f"  [WOULD CREATE]  {dname}/{fname}")


def apply_scaffold(force=False):
    results = _check_results()
    missing = [(f, d) for f, d, ok in results if not ok]

    total = len(VAULT_FILES) + len(COMPACT_FILES)
    present_count = total - len(missing)

    print("=== Obsidian Memory Scaffold Apply ===")
    print(f"Present before apply: {present_count} / {total}")

    if not missing:
        print("\nAll expected files already exist. Nothing to create.")
        return

    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    COMPACT_DIR.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0

    for fname, dname in missing:
        if dname == "vault":
            path = VAULT_DIR / fname
            template = VAULT_TEMPLATES.get(fname)
        else:
            path = COMPACT_DIR / fname
            template = COMPACT_TEMPLATES.get(fname)

        if path.exists() and not force:
            print(f"  [SKIP]    {dname}/{fname} — already exists")
            skipped += 1
            continue

        if template is None:
            print(f"  [SKIP]    {dname}/{fname} — no template defined; create manually")
            skipped += 1
            continue

        path.write_text(template, encoding="utf-8")
        print(f"  [CREATED] {dname}/{fname}")
        created += 1

    print(f"\nApply complete. Created: {created}, Skipped: {skipped}.")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Obsidian memory scaffold checker and creator (N+3.34).\n"
            "Stdlib only. No external APIs. No model calls. No live actions.\n\n"
            "Default (no flag): dry-run mode."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Check which expected files exist vs missing",
    )
    parser.add_argument(
        "--dry-run", action="store_true", dest="dry_run",
        help="Show what would be created without creating anything (default)",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Create missing files using stub templates",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite existing files when used with --apply (USE WITH CAUTION)",
    )

    args = parser.parse_args()

    if args.check:
        check_files()
    elif args.apply:
        if args.force:
            print("WARNING: --force is set. Existing files WILL be overwritten.")
        apply_scaffold(force=args.force)
    else:
        dry_run()


if __name__ == "__main__":
    main()
