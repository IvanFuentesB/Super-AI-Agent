#!/usr/bin/env python3
"""Ghoti Merge Assistant — N+3.58A: help the operator merge audited branches safely.

Dry-run-first. No merge/push by default. Generates operator commands and validation checklist.
Stdlib only. No external APIs. No live actions.
"""
import argparse
import datetime
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
TOOLING_DIR = REPO_ROOT / "14_context" / "tooling"
REPORT_PATH = TOOLING_DIR / "merge_assistant_n3_58.md"
MAIN_BRANCH = "feat/ghoti-visible-operator-stack"


def _run_git(args, cwd=None, timeout=10):
    try:
        r = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True,
            cwd=str(cwd or REPO_ROOT), timeout=timeout
        )
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except Exception as e:
        return "", str(e), -1


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _collect_status(target_branch=None):
    branch, _, _ = _run_git(["branch", "--show-current"])
    head, _, _ = _run_git(["rev-parse", "--short", "HEAD"])
    dirty_out, _, _ = _run_git(["status", "--short"])
    dirty_lines = [l for l in (dirty_out or "").splitlines() if l.strip()]

    main_head, _, main_rc = _run_git(["rev-parse", "--short", MAIN_BRANCH])
    main_remote_head, _, _ = _run_git(["rev-parse", "--short", f"origin/{MAIN_BRANCH}"])

    target_exists = None
    target_head = None
    if target_branch:
        tb_head, _, tb_rc = _run_git(["rev-parse", "--short", target_branch])
        target_exists = tb_rc == 0
        target_head = tb_head if target_exists else None

    return {
        "generated_at": _utc_now(),
        "current_branch": branch or "unknown",
        "current_head": head or "unknown",
        "main_branch": MAIN_BRANCH,
        "main_local_head": main_head if main_rc == 0 else "NOT_FOUND",
        "main_remote_head": main_remote_head or "NOT_FOUND",
        "primary_worktree_dirty": len(dirty_lines) > 0,
        "dirty_file_count": len(dirty_lines),
        "target_branch": target_branch,
        "target_exists": target_exists,
        "target_head": target_head,
    }


def cmd_status(args):
    target = getattr(args, "target_branch", None)
    s = _collect_status(target_branch=target)
    print("=== Ghoti Merge Assistant — Status ===")
    print(f"Current branch   : {s['current_branch']}")
    print(f"Current HEAD     : {s['current_head']}")
    print(f"Main branch      : {s['main_branch']}")
    print(f"Main local HEAD  : {s['main_local_head']}")
    print(f"Main remote HEAD : {s['main_remote_head']}")
    dirty_label = f"YES — {s['dirty_file_count']} files" if s["primary_worktree_dirty"] else "NO (clean)"
    print(f"Primary worktree dirty: {dirty_label}")
    if target:
        exists_label = "EXISTS" if s["target_exists"] else "NOT FOUND"
        print(f"Target branch    : {target} ({exists_label})")
        if s["target_head"]:
            print(f"Target HEAD      : {s['target_head']}")
    print("=== End Status ===")


def cmd_plan(args):
    target = getattr(args, "target_branch", None)
    if not target:
        print("ERROR: --target-branch is required for --plan")
        sys.exit(1)
    s = _collect_status(target_branch=target)
    dirty_label = f"YES ({s['dirty_file_count']} files)" if s["primary_worktree_dirty"] else "NO"

    plan_md = f"""# Ghoti Merge Assistant — Merge Plan — N+3.58A

Generated: {s['generated_at']}
Current branch: `{s['current_branch']}`
Main branch: `{s['main_branch']}`
Main local HEAD: `{s['main_local_head']}`
Main remote HEAD: `{s['main_remote_head']}`
Target branch: `{target}`
Target exists: {s['target_exists']}
Target HEAD: `{s['target_head'] or 'NOT_FOUND'}`
Primary worktree dirty: {dirty_label}

## Pre-Merge Checklist

- [ ] Codex N+3.56-FIX audit must say PASS (not CONDITIONAL PASS, not BLOCKED)
- [ ] **Do not merge if Codex says BLOCKED**
- [ ] Primary worktree is clean or dirty files are intentionally unstaged
- [ ] Target branch is fetched and up-to-date with remote
- [ ] All validation scripts pass on target branch
- [ ] Codex N+3.56-FIX clean-pass audit (N+3.57) PASS confirmed before merge

## Phase-by-Phase Merge Commands (PowerShell — Operator Executes Manually)

### Phase 1 — Fetch

```powershell
cd C:\\Users\\ai_sandbox\\Documents\\AI_Managed_Only
git fetch origin
```

### Phase 2 — Switch to Main

```powershell
git switch {s['main_branch']}
```

### Phase 3 — Pull Fast-Forward Only

```powershell
git pull --ff-only origin {s['main_branch']}
```

### Phase 4 — Merge Target Branch (no fast-forward, preserve history)

```powershell
git merge --no-ff {target} -m "merge: land {target} into {s['main_branch']}"
```

### Phase 5 — Run Validations

```powershell
python -c "import ast, pathlib; files=['03_scripts/repo_language_inventory.py','03_scripts/rust_readiness_probe.py','03_scripts/ghoti_merge_assistant.py','03_scripts/ghoti_dashboard.py','03_scripts/local_worker_router.py','03_scripts/agent_lane_status.py']; [ast.parse(pathlib.Path(f).read_text(encoding='utf-8')) for f in files]; print('AST OK')"
python 03_scripts/ghoti_dashboard.py --status
python 03_scripts/ghoti_dashboard.py --json
python 03_scripts/repo_language_inventory.py --status
python 03_scripts/rust_readiness_probe.py --status
python 03_scripts/local_worker_router.py --recommend --task "check Rust readiness for future runtime core"
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
git diff --check
```

### Phase 6 — Push Main (only after validations pass and operator approves)

```powershell
git push origin {s['main_branch']}
```

## Safety Notes

- **Do not merge if Codex says BLOCKED.**
- Codex N+3.56-FIX clean-pass audit (N+3.57) should PASS before merging.
- Do not force-push main.
- Do not skip the validation phase.
- If merge conflicts arise, resolve them manually before pushing.
- Primary worktree dirt should be stashed or committed separately before merging.
- This script generates commands only. It does NOT execute the merge.
"""

    if args.dry_run and not args.apply:
        print("[DRY RUN] Merge plan preview:")
        print(plan_md)
        print(f"[DRY RUN] Would write to: {REPORT_PATH.relative_to(REPO_ROOT)}")
        print("[DRY RUN] Pass --apply to write.")
        return
    if args.apply:
        TOOLING_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(plan_md, encoding="utf-8")
        print(f"Written: {REPORT_PATH.relative_to(REPO_ROOT)}")
        print("This file contains commands only. Merge must be executed manually by the operator.")


def main():
    parser = argparse.ArgumentParser(
        description="Ghoti Merge Assistant — N+3.58A. Dry-run-first. No merge/push by default."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true", help="Print current branch and merge status")
    group.add_argument("--plan", action="store_true", help="Generate merge plan (commands only)")
    parser.add_argument("--target-branch", help="Branch to merge into main (required for --plan)")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    elif args.plan:
        cmd_plan(args)


if __name__ == "__main__":
    main()
