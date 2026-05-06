#!/usr/bin/env python3
"""CC/Codex Bridge — local file-based handoff bridge. No automatic CC/Codex. Human copy-paste only.

N+3.51A: stdlib-only, local file bridge, no clipboard, no API, no auto-send.
Truthfully states: CC/Codex automatic = NO.
"""
import argparse
import base64
import datetime
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
BRIDGE_DIR = REPO_ROOT / "14_context" / "bridge"
INBOX_DIR = BRIDGE_DIR / "inbox"
OUTBOX_DIR = BRIDGE_DIR / "outbox"
ARCHIVE_DIR = BRIDGE_DIR / "archive"
STATUS_DIR = BRIDGE_DIR / "status"

BRIDGE_DIRS = [BRIDGE_DIR, INBOX_DIR, OUTBOX_DIR, ARCHIVE_DIR, STATUS_DIR]
VALID_TARGETS = {"claude", "codex", "chatgpt", "all"}


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _run(cmd, cwd=None, timeout=5):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd or REPO_ROOT), timeout=timeout)
        return r.stdout.strip(), r.returncode
    except Exception:
        return "", -1


def _safe_write_text(dest: pathlib.Path, content: str) -> None:
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


def _get_branch():
    out, rc = _run(["git", "branch", "--show-current"])
    return out if rc == 0 else "unknown"


def _get_head():
    out, rc = _run(["git", "rev-parse", "--short", "HEAD"])
    return out if rc == 0 else "unknown"


def _outbox_files():
    if not OUTBOX_DIR.exists():
        return []
    return sorted(OUTBOX_DIR.glob("*.md"))


def _ensure_bridge_dirs():
    dirs_json = json.dumps([str(d) for d in BRIDGE_DIRS])
    node_script = (
        "const fs=require('fs');"
        f"const dirs={dirs_json};"
        "dirs.forEach(d=>{try{fs.mkdirSync(d,{recursive:true});}catch(e){}});"
        "console.log('DIRS_OK');"
    )
    out, rc = _run(["node", "-e", node_script], timeout=10)
    if rc != 0 or "DIRS_OK" not in out:
        raise RuntimeError(f"Failed to create bridge dirs (rc={rc})")


def cmd_status(args):
    print("=== CC/Codex Bridge Status ===")
    print(f"Branch          : {_get_branch()}")
    print(f"HEAD            : {_get_head()}")
    dirty_out, _ = _run(["git", "status", "--short"])
    dirty_lines = [l for l in dirty_out.splitlines() if l.strip()] if dirty_out else []
    print(f"Dirty state     : {len(dirty_lines)} file(s)")
    print()
    print("Bridge dirs:")
    for d in BRIDGE_DIRS:
        exists = d.exists()
        count = len(list(d.iterdir())) if exists else 0
        print(f"  {'OK' if exists else 'MISSING'}: {d.relative_to(REPO_ROOT)}  ({count} items)")
    print()
    outbox = _outbox_files()
    print(f"Pending outbox  : {len(outbox)} file(s)")
    for f in outbox[-5:]:
        print(f"  {f.name}")
    print()
    print("IMPORTANT: CC/Codex automatic = NO")
    print("Bridge type    : local/manual file bridge")
    print("No clipboard. No API. No auto-send. Human copies files manually.")
    print("=== End Status ===")


def cmd_write_pair(args):
    if not args.title:
        print("ERROR: --title required")
        sys.exit(1)

    target = args.target or "all"
    if target not in VALID_TARGETS:
        print(f"ERROR: --target must be one of {sorted(VALID_TARGETS)}")
        sys.exit(1)

    ts = _utc_now()
    slug = args.title.lower().replace(" ", "_")[:40]
    branch = _get_branch()
    head = _get_head()
    body = args.body or "(no body provided)"

    targets = ["claude", "codex", "chatgpt"] if target == "all" else [target]

    pairs = []
    for t in targets:
        filename = f"{t}_handoff_{ts}_{slug}.md"
        content = (
            f"# {t.title()} Handoff — {args.title}\n\n"
            f"Generated: {ts}\n"
            f"Branch: `{branch}` | HEAD: `{head}`\n\n"
            f"---\n\n"
            f"{body}\n\n"
            f"---\n\n"
            f"**IMPORTANT**: CC/Codex automatic = NO. Copy-paste this file manually into {t.title()}.\n"
        )
        pairs.append((t, filename, content))

    if args.dry_run and not args.apply:
        print(f"[DRY RUN] Title  : {args.title}")
        print(f"[DRY RUN] Targets: {targets}")
        print(f"[DRY RUN] Would write to: 14_context/bridge/outbox/")
        for t, fn, content in pairs:
            print(f"  [DRY RUN] {t}: {fn}")
            print(f"    Preview: {content[:200]}")
        print("[DRY RUN] Pass --apply to write.")
        return

    if args.apply:
        _ensure_bridge_dirs()
        for t, fn, content in pairs:
            dest = OUTBOX_DIR / fn
            try:
                _safe_write_text(dest, content)
                print(f"Written ({t}): {dest.relative_to(REPO_ROOT)}")
            except RuntimeError as e:
                print(f"ERROR writing {t}: {e}")
                sys.exit(1)
        print()
        print("Copy-paste: Open each file above and paste into the target AI tool.")
        print("IMPORTANT: CC/Codex automatic = NO. No clipboard. No API. Human paste required.")


def cmd_next(args):
    outbox = _outbox_files()
    if not outbox:
        print("Outbox is empty. No pending files.")
        return
    next_file = outbox[0]
    print("=== Next Bridge Action ===")
    print(f"Next file       : {next_file.name}")
    print(f"Full path       : {next_file.relative_to(REPO_ROOT)}")
    print()
    print("Action: Open the file above and paste its contents into the appropriate AI tool.")
    print("IMPORTANT: CC/Codex automatic = NO. Manual paste required.")
    if args.dry_run and not args.apply:
        print("[DRY RUN] No files moved. This is a read-only status report.")
    print("=== End Next ===")


def cmd_list(args):
    print("=== Bridge File List ===")
    for d in [OUTBOX_DIR, INBOX_DIR, ARCHIVE_DIR]:
        name = d.name
        files = sorted(d.glob("*")) if d.exists() else []
        files = [f for f in files if f.name != ".gitkeep"]
        print(f"\n{name.upper()} ({len(files)} files):")
        for f in files:
            size = f.stat().st_size
            print(f"  {f.name}  ({size}b)")
    print("=== End List ===")


def cmd_verify(args):
    print("=== Bridge Verification ===")
    ok = True
    for d in BRIDGE_DIRS:
        if d.exists():
            print(f"  OK: {d.relative_to(REPO_ROOT)}")
        else:
            print(f"  MISSING: {d.relative_to(REPO_ROOT)}")
            ok = False

    outbox = _outbox_files()
    print(f"\nOutbox files: {len(outbox)}")
    bad = []
    for f in outbox:
        try:
            content = f.read_text(encoding="utf-8")
            print(f"  VALID: {f.name}  ({len(content)} chars)")
        except Exception as e:
            print(f"  ERROR: {f.name} — {e}")
            bad.append(f.name)

    print()
    print("CONFIRMED: CC/Codex automatic = NO")
    print("CONFIRMED: Bridge type = local/manual file bridge")
    print("CONFIRMED: No clipboard, no API, no auto-send")
    if bad:
        print(f"WARNING: {len(bad)} files failed to read: {bad}")
    if ok and not bad:
        print("Verification: PASS")
    else:
        print("Verification: PARTIAL (some dirs missing or files unreadable)")
    print("=== End Verify ===")


def cmd_archive_done(args):
    outbox = _outbox_files()
    if not outbox:
        print("Outbox is empty. Nothing to archive.")
        return

    if args.dry_run and not args.apply:
        print(f"[DRY RUN] Would archive {len(outbox)} file(s) from outbox to archive:")
        for f in outbox:
            print(f"  {f.name}")
        print("[DRY RUN] Pass --apply to archive.")
        return

    if args.apply:
        _ensure_bridge_dirs()
        for f in outbox:
            dest = ARCHIVE_DIR / f.name
            try:
                content = f.read_text(encoding="utf-8")
                _safe_write_text(dest, content)
                f.unlink()
                print(f"Archived: {f.name}")
            except Exception as e:
                print(f"ERROR archiving {f.name}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "CC/Codex Bridge — local file-based handoff bridge. "
            "CC/Codex automatic = NO. Human copy-paste only. N+3.51A."
        )
    )
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--status", action="store_true", help="Show bridge status")
    mode_group.add_argument("--write-pair", action="store_true", help="Write Claude/Codex/ChatGPT handoff files")
    mode_group.add_argument("--next", action="store_true", help="Show next paste action")
    mode_group.add_argument("--list", action="store_true", help="List all bridge files")
    mode_group.add_argument("--verify", action="store_true", help="Verify bridge dirs and files")
    mode_group.add_argument("--archive-done", action="store_true", help="Archive outbox files")

    parser.add_argument("--title", help="Handoff title")
    parser.add_argument("--body", help="Handoff body text")
    parser.add_argument("--target", choices=["claude", "codex", "chatgpt", "all"], default="all",
                        help="Target AI tool (default: all)")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--force", action="store_true", help="Force archive even if files look incomplete")

    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    elif args.write_pair:
        cmd_write_pair(args)
    elif args.next:
        cmd_next(args)
    elif args.list:
        cmd_list(args)
    elif args.verify:
        cmd_verify(args)
    elif args.archive_done:
        cmd_archive_done(args)


if __name__ == "__main__":
    main()
