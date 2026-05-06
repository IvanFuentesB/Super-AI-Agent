#!/usr/bin/env python3
"""Prompt Bus — local copy-paste manager for Claude/Codex/ChatGPT coordination.

stdlib only, repo-local, no external APIs, no clipboard by default, no live actions.
"""
import argparse
import datetime
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
PROMPT_BUS_DIR = REPO_ROOT / "14_context" / "prompt_bus"
INBOX_DIR = PROMPT_BUS_DIR / "inbox"
OUTBOX_DIR = PROMPT_BUS_DIR / "outbox"
ARCHIVE_DIR = PROMPT_BUS_DIR / "archive"
TEMPLATES_DIR = PROMPT_BUS_DIR / "templates"
CANONICAL_CLAUDE_PROMPT = REPO_ROOT / "14_context" / "ghoti_current_prompt.md"
STATUS_FILE = PROMPT_BUS_DIR / "current_status.md"
AGENT_LANES_DIR = REPO_ROOT / "14_context" / "agent_lanes"
ACTIVE_LOCKS_FILE = AGENT_LANES_DIR / "active_locks.jsonl"
LANE_STATUS_FILE = AGENT_LANES_DIR / "lane_status.jsonl"
COMPACT_MEMORY_DIR = REPO_ROOT / "14_context" / "compact_memory"


def _utc_now_ts():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _get_branch():
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _get_head():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _ensure_dirs():
    for d in [PROMPT_BUS_DIR, INBOX_DIR, OUTBOX_DIR, ARCHIVE_DIR, TEMPLATES_DIR]:
        d.mkdir(parents=True, exist_ok=True)


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


def cmd_init(args):
    if args.dry_run and not args.apply:
        print("[DRY RUN] Would create directories:")
        for d in [PROMPT_BUS_DIR, INBOX_DIR, OUTBOX_DIR, ARCHIVE_DIR, TEMPLATES_DIR]:
            print(f"  {d.relative_to(REPO_ROOT)}")
        print("[DRY RUN] Pass --apply to create.")
        return
    _ensure_dirs()
    print("Directories verified/created:")
    for d in [PROMPT_BUS_DIR, INBOX_DIR, OUTBOX_DIR, ARCHIVE_DIR, TEMPLATES_DIR]:
        print(f"  OK: {d.relative_to(REPO_ROOT)}")
    print("Init complete.")


def cmd_status(args):
    branch = _get_branch()
    print(f"Branch: {branch}")
    print(f"Canonical Claude prompt: {CANONICAL_CLAUDE_PROMPT.relative_to(REPO_ROOT)}")
    if CANONICAL_CLAUDE_PROMPT.exists():
        stat = CANONICAL_CLAUDE_PROMPT.stat()
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        size = stat.st_size
        print(f"  exists: yes  size: {size}b  modified: {mtime}")
    else:
        print("  exists: NO (not yet created)")

    outbox_files = sorted(OUTBOX_DIR.glob("*.md")) if OUTBOX_DIR.exists() else []
    print(f"Outbox ({OUTBOX_DIR.relative_to(REPO_ROOT)}): {len(outbox_files)} file(s)")
    for f in outbox_files[-5:]:
        print(f"  {f.name}")

    inbox_files = sorted(INBOX_DIR.glob("*")) if INBOX_DIR.exists() else []
    inbox_files = [f for f in inbox_files if f.name != ".gitkeep"]
    print(f"Inbox: {len(inbox_files)} file(s)")


def cmd_write_claude(args):
    if not args.title:
        print("ERROR: --title required")
        sys.exit(1)
    if not args.body:
        print("ERROR: --body required")
        sys.exit(1)

    header = (
        f"# Claude Code Prompt — {args.title}\n\n"
        f"Generated: {_utc_now_ts()}\n"
        f"Branch: {_get_branch()}\n\n"
        f"---\n\n"
    )
    content = header + args.body + "\n"

    print(f"Target: {CANONICAL_CLAUDE_PROMPT.relative_to(REPO_ROOT)}")
    print("--- Preview (first 400 chars) ---")
    print(content[:400])
    print("---")

    if args.apply:
        CANONICAL_CLAUDE_PROMPT.write_text(content, encoding="utf-8")
        print(f"Written: {CANONICAL_CLAUDE_PROMPT.relative_to(REPO_ROOT)}")
        print("Copy-paste instruction: open the file above and paste into Claude Code.")
    else:
        print("[DRY RUN] Pass --apply to write.")


def cmd_write_codex(args):
    if not args.title:
        print("ERROR: --title required")
        sys.exit(1)
    if not args.body:
        print("ERROR: --body required")
        sys.exit(1)

    ts = _utc_now_ts()
    slug = args.title.lower().replace(" ", "_")[:40]
    filename = f"codex_{ts}_{slug}.md"
    dest = OUTBOX_DIR / filename

    header = (
        f"# Codex Prompt — {args.title}\n\n"
        f"Generated: {ts}\n"
        f"Branch: {_get_branch()}\n\n"
        f"---\n\n"
    )
    content = header + args.body + "\n"

    print(f"Target: {dest.relative_to(REPO_ROOT)}")
    print("--- Preview (first 400 chars) ---")
    print(content[:400])
    print("---")

    if args.apply:
        OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        print(f"Written: {dest.relative_to(REPO_ROOT)}")
        print("Copy-paste instruction: open the file above and paste into Codex.")
    else:
        print(f"[DRY RUN] Would write to: {dest.relative_to(REPO_ROOT)}")
        print("[DRY RUN] Pass --apply to write.")


def cmd_list_outbox(args):
    if not OUTBOX_DIR.exists():
        print("Outbox directory does not exist. Run --init first.")
        return
    files = sorted(OUTBOX_DIR.glob("*.md"))
    if not files:
        print("Outbox is empty.")
        return
    print(f"Outbox ({len(files)} file(s)):")
    for f in files:
        size = f.stat().st_size
        mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"  {f.name}  ({size}b  {mtime})")


def cmd_write_chatgpt(args):
    if not args.title:
        print("ERROR: --title required")
        sys.exit(1)
    if not args.body:
        print("ERROR: --body required")
        sys.exit(1)

    ts = _utc_now_ts()
    slug = args.title.lower().replace(" ", "_")[:40]
    filename = "chatgpt_handoff_" + ts + "_" + slug + ".md"
    dest = OUTBOX_DIR / filename

    nl = chr(10)
    header = (
        "# ChatGPT Handoff -- " + args.title + nl + nl
        + "Generated: " + ts + nl
        + "Branch: " + _get_branch() + nl + nl
        + "---" + nl + nl
    )
    content = header + args.body + nl

    print("Target: " + str(dest.relative_to(REPO_ROOT)))
    print("--- Preview (first 400 chars) ---")
    print(content[:400])
    print("---")

    if args.apply:
        OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        print("Written: " + str(dest.relative_to(REPO_ROOT)))
        print("Copy-paste instruction: open the file above and paste into ChatGPT.")
    else:
        print("[DRY RUN] Would write to: " + str(dest.relative_to(REPO_ROOT)))
        print("[DRY RUN] Pass --apply to write.")


def cmd_status_json(args):
    branch = _get_branch()
    outbox_files = sorted(OUTBOX_DIR.glob("*.md")) if OUTBOX_DIR.exists() else []
    inbox_files = sorted(INBOX_DIR.glob("*")) if INBOX_DIR.exists() else []
    inbox_files = [f for f in inbox_files if f.name != ".gitkeep"]
    prompt_exists = CANONICAL_CLAUDE_PROMPT.exists()
    prompt_size = CANONICAL_CLAUDE_PROMPT.stat().st_size if prompt_exists else 0
    status = {
        "generated": _utc_now_ts(),
        "branch": branch,
        "canonical_prompt": {
            "path": str(CANONICAL_CLAUDE_PROMPT.relative_to(REPO_ROOT)),
            "exists": prompt_exists,
            "size_bytes": prompt_size,
        },
        "outbox": {
            "path": str(OUTBOX_DIR.relative_to(REPO_ROOT)),
            "count": len(outbox_files),
            "files": [f.name for f in outbox_files[-5:]],
        },
        "inbox": {"count": len(inbox_files)},
    }
    print(json.dumps(status, indent=2))


def _build_context_pack(args):
    ts = _utc_now_ts()
    branch = _get_branch()
    head = _get_head()

    sections = []
    sections.append(f"# Ghoti Context Pack — {args.title or 'context'}")
    sections.append(f"\nGenerated: {ts}")
    sections.append(f"Branch: `{branch}` | HEAD: `{head}`")
    sections.append(f"\n---\n")

    if args.include_status:
        sections.append("## System Status Summary")
        # Prompt bus
        outbox_files = sorted(OUTBOX_DIR.glob("*.md")) if OUTBOX_DIR.exists() else []
        inbox_files = [f for f in (sorted(INBOX_DIR.glob("*")) if INBOX_DIR.exists() else [])
                       if f.name != ".gitkeep"]
        prompt_exists = CANONICAL_CLAUDE_PROMPT.exists()
        sections.append(f"- Canonical Claude prompt: {'EXISTS' if prompt_exists else 'MISSING'}")
        sections.append(f"- Outbox files: {len(outbox_files)}")
        sections.append(f"- Inbox files: {len(inbox_files)}")

        # Agent lanes
        locks, _ = _parse_jsonl(ACTIVE_LOCKS_FILE)
        statuses, _ = _parse_jsonl(LANE_STATUS_FILE)
        sections.append(f"- Active lane locks: {len(locks)}")
        sections.append(f"- Lane status records: {len(statuses)}")
        if locks:
            last = locks[-1]
            sections.append(f"- Latest lock: {last.get('agent_id','?')} / {last.get('task_slug','?')} / {last.get('branch','?')}")
        if statuses:
            last = statuses[-1]
            sections.append(f"- Latest state: {last.get('agent_id','?')} = {last.get('current_state','?')}")
        sections.append("")

    if args.include_memory:
        sections.append("## Compact Memory Pointers")
        if COMPACT_MEMORY_DIR.exists():
            mem_files = sorted(COMPACT_MEMORY_DIR.glob("*.md"))
            for f in mem_files:
                sections.append(f"- `{f.relative_to(REPO_ROOT)}`")
        else:
            sections.append("- (compact memory directory not found)")
        sections.append("")

    if args.include_next_actions:
        sections.append("## Next Recommended Commands")
        sections.append("```bash")
        sections.append("python 03_scripts/ghoti_dashboard.py --json")
        sections.append("python 03_scripts/ruflo_install_gate.py --status")
        sections.append("python 03_scripts/gemma_compact_memory_worker.py --status")
        sections.append("python 03_scripts/agent_lane_status.py --check")
        sections.append("```")
        sections.append("")

    sections.append("## Safety Rules")
    sections.append("- No live email, posting, buying, selling, payments, or account creation.")
    sections.append("- No secrets, no .env reads, no credential printing.")
    sections.append("- No global npm install. No Ruflo runtime wiring yet.")
    sections.append("- No autonomous external browser actions.")
    sections.append("- Human approval required for all live/public/money actions.")
    sections.append("")

    return "\n".join(sections) + "\n"


def cmd_write_context_pack(args):
    if not args.title:
        print("ERROR: --title required")
        sys.exit(1)

    target = args.target or "all"
    valid_targets = {"claude", "codex", "chatgpt", "all"}
    if target not in valid_targets:
        print(f"ERROR: --target must be one of {sorted(valid_targets)}")
        sys.exit(1)

    ts = _utc_now_ts()
    slug = (args.title or "context").lower().replace(" ", "_")[:40]
    content = _build_context_pack(args)

    targets_to_write = ["claude", "codex", "chatgpt"] if target == "all" else [target]

    print(f"Context pack targets: {targets_to_write}")
    print(f"Title: {args.title}")
    print(f"Generated: {ts}")
    print()

    if args.dry_run and not args.apply:
        print("[DRY RUN] Content preview (first 800 chars):")
        print(content[:800])
        print("...")
        print()
        for t in targets_to_write:
            if t == "claude":
                print(f"[DRY RUN] Claude: would overwrite {CANONICAL_CLAUDE_PROMPT.relative_to(REPO_ROOT)}")
            else:
                fn = f"{t}_context_pack_{ts}_{slug}.md"
                print(f"[DRY RUN] {t.capitalize()}: would write outbox/{fn}")
        print("[DRY RUN] Pass --apply to write.")
        return

    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    for t in targets_to_write:
        if t == "claude":
            CANONICAL_CLAUDE_PROMPT.write_text(content, encoding="utf-8")
            print(f"Written (Claude): {CANONICAL_CLAUDE_PROMPT.relative_to(REPO_ROOT)}")
        else:
            fn = f"{t}_context_pack_{ts}_{slug}.md"
            dest = OUTBOX_DIR / fn
            dest.write_text(content, encoding="utf-8")
            print(f"Written ({t.capitalize()}): {dest.relative_to(REPO_ROOT)}")

    print()
    print("Copy-paste: open the relevant file above and paste into the target AI tool.")
    print("NOTE: Outbox files are unstaged. Stage only if part of milestone docs.")


def main():
    parser = argparse.ArgumentParser(
        description="Prompt Bus — local copy-paste manager. stdlib only, no live actions."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--init", action="store_true", help="Create prompt bus directories/templates")
    group.add_argument("--status", action="store_true", help="Print current branch, prompt paths, outbox count")
    group.add_argument("--write-claude", action="store_true", help="Write/overwrite canonical Claude prompt")
    group.add_argument("--write-codex", action="store_true", help="Write timestamped Codex prompt to outbox")
    group.add_argument("--list-outbox", action="store_true", help="List outbox prompt files")
    group.add_argument("--write-chatgpt", action="store_true", help="Write timestamped ChatGPT handoff to outbox")
    group.add_argument("--status-json", action="store_true", help="Print status as JSON to stdout")
    group.add_argument("--write-context-pack", action="store_true",
                       help="Generate rich handoff/context packs for Claude/Codex/ChatGPT")

    parser.add_argument("--title", help="Prompt or pack title")
    parser.add_argument("--body", help="Prompt body text")
    parser.add_argument("--target", choices=["claude", "codex", "chatgpt", "all"], default="all",
                        help="Context pack target (default: all)")
    parser.add_argument("--include-status", action="store_true", help="Include system status in context pack")
    parser.add_argument("--include-memory", action="store_true", help="Include compact memory pointers")
    parser.add_argument("--include-next-actions", action="store_true", help="Include next recommended commands")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run (default)")
    parser.add_argument("--apply", action="store_true", help="Actually write the file(s)")

    args = parser.parse_args()

    if args.init:
        cmd_init(args)
    elif args.status:
        cmd_status(args)
    elif args.write_claude:
        cmd_write_claude(args)
    elif args.write_codex:
        cmd_write_codex(args)
    elif args.list_outbox:
        cmd_list_outbox(args)
    elif args.write_chatgpt:
        cmd_write_chatgpt(args)
    elif args.status_json:
        cmd_status_json(args)
    elif args.write_context_pack:
        cmd_write_context_pack(args)


if __name__ == "__main__":
    main()
