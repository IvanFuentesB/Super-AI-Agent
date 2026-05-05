#!/usr/bin/env python3
"""Prompt Bus — local copy-paste manager for Claude/Codex/ChatGPT coordination.

stdlib only, repo-local, no external APIs, no clipboard by default, no live actions.
"""
import argparse
import datetime
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
PROMPT_BUS_DIR = REPO_ROOT / "14_context" / "prompt_bus"
INBOX_DIR = PROMPT_BUS_DIR / "inbox"
OUTBOX_DIR = PROMPT_BUS_DIR / "outbox"
ARCHIVE_DIR = PROMPT_BUS_DIR / "archive"
TEMPLATES_DIR = PROMPT_BUS_DIR / "templates"
CANONICAL_CLAUDE_PROMPT = REPO_ROOT / "14_context" / "ghoti_current_prompt.md"
STATUS_FILE = PROMPT_BUS_DIR / "current_status.md"


def _utc_now_ts():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _get_branch():
    try:
        import subprocess
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _ensure_dirs():
    for d in [PROMPT_BUS_DIR, INBOX_DIR, OUTBOX_DIR, ARCHIVE_DIR, TEMPLATES_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def cmd_init(args):
    _ensure_dirs()
    if args.dry_run and not args.apply:
        print("[DRY RUN] Would create directories:")
        for d in [PROMPT_BUS_DIR, INBOX_DIR, OUTBOX_DIR, ARCHIVE_DIR, TEMPLATES_DIR]:
            print(f"  {d.relative_to(REPO_ROOT)}")
        print("[DRY RUN] Pass --apply to create.")
        return
    print("Directories verified/created:")
    for d in [PROMPT_BUS_DIR, INBOX_DIR, OUTBOX_DIR, ARCHIVE_DIR, TEMPLATES_DIR]:
        d.mkdir(parents=True, exist_ok=True)
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

    parser.add_argument("--title", help="Prompt title")
    parser.add_argument("--body", help="Prompt body text")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run (default)")
    parser.add_argument("--apply", action="store_true", help="Actually write the file")

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


if __name__ == "__main__":
    main()
