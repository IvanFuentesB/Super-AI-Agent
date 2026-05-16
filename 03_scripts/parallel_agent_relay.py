#!/usr/bin/env python3
"""
Parallel Agent Relay Command Center (N+4.5A)

Generates paired prompt packets for Claude Code (implementation) and Codex (audit)
so they can run in parallel. Copy-paste only — no autonomous Claude/Codex launch.

CLI:
  --status --json       Print relay status as JSON
  --json                Same as --status --json
  --create-pair         Generate a paired prompt packet
    --milestone TEXT    Milestone name (e.g. "N+4.5A")
    --title TEXT        Feature title
    --implementation-branch TEXT
    --audit-branch TEXT
    --codex-effort TEXT (default: extra-high)
    --write-packets     Write packet files to disk
    --output-dir PATH   Optional repo-local output directory
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo root discovery: 03_scripts/parallel_agent_relay.py -> repo root
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent.resolve()
PAIRS_DIR = REPO_ROOT / "14_context" / "agent_relay" / "pairs"
RELAY_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Path containment (replicates N+4.4D pattern)
# ---------------------------------------------------------------------------

def _is_path_inside_repo(target) -> bool:
    """Return True if target resolves to a path inside REPO_ROOT."""
    try:
        resolved = Path(str(target)).resolve()
        repo = REPO_ROOT.resolve()
        return resolved == repo or repo in resolved.parents
    except Exception:
        return False


def _require_repo_local(target) -> Path:
    """
    Resolve target (relative or absolute) and reject anything outside REPO_ROOT.
    Raises ValueError for out-of-repo paths.
    """
    p = Path(str(target).replace("/", os.sep))
    if not p.is_absolute():
        p = REPO_ROOT / p
    p = p.resolve()
    if not _is_path_inside_repo(p):
        raise ValueError(
            f"Path is outside repo root and is not allowed: {p}\n"
            "Only repo-local paths are accepted."
        )
    return p


# ---------------------------------------------------------------------------
# Prompt generation
# ---------------------------------------------------------------------------

def _claude_prompt(milestone: str, title: str, impl_branch: str, audit_branch: str) -> str:
    slug = milestone.lower().replace("+", "").replace(".", "_").replace(" ", "_")
    return f"""/ultraplan
/goal

Continue {milestone} implementation now.

You are Claude Code. Codex is already auditing/polling in parallel, but the
implementation branch is missing because Claude has not pushed it yet. Your job
is to create, implement, validate, commit, push, and verify the feature branch.

Target branch:
{impl_branch}

Current main:
origin/main — confirm with: git ls-remote origin refs/heads/main

PLANNING: Use /ultraplan for deep planning mode. Maximum planning effort.
Use the strongest available reasoning. Produce a complete, risk-checked plan
before writing any code.

EXECUTION: Use /goal for long-horizon execution. Claude Sonnet 4.6, high effort.
Work until IMPLEMENTED_AND_PUSHED or a real, confirmed blocker.

MISSION: {title}

REQUIRED STEPS:
1. Create isolated worktree from origin/main.
   Use a path inside the repo root — never C:\\w\\.
   If CLAUDE.md demands stricter containment, use:
   ..\\AI_Managed_Only\\.claude\\worktrees\\<branch-slug>
2. Implement all milestone deliverables (see milestone spec above).
3. Run all validations:
   - git diff --check
   - node --check (dashboard JS files if changed)
   - python -m unittest (all test modules)
   - python 03_scripts/... --validate / --status / --json
   - pwsh 03_scripts/check_runtime_mvp.ps1
   - pwsh 03_scripts/check_dashboard_mvp.ps1
4. Write milestone report to:
   14_context/claude_{slug}_*.md
5. Commit: feat(ghoti): {title.lower()}
6. Push:   git push origin {impl_branch}
7. Verify: git ls-remote origin refs/heads/{impl_branch}

SAFETY RULES:
- Do not push main. Do not force-push. Never rewrite history.
- No live account actions. No cap bypass.
- No external repo clone/install/run.
- No autonomous Claude/Codex launch.
- No secrets or API keys committed.
- Stage only intentional milestone files — never git add -A.
- All writes must stay inside repo root.

CODEX AUDIT BRANCH (do NOT push — Codex handles it):
{audit_branch}

FINAL RESPONSE PACKET must include:
- Branch
- New commit hash
- Pushed yes/no
- ls-remote verification hash
- Test totals (pass/fail/error)
- Runtime check result
- Dashboard check result
- Safety summary
- Final verdict: IMPLEMENTED_AND_PUSHED or real blocker with exact error
"""


def _codex_prompt(
    milestone: str,
    title: str,
    impl_branch: str,
    audit_branch: str,
    codex_effort: str = "extra-high",
) -> str:
    return f"""This is a Codex audit task for {milestone} — {title}.

MODE / EFFORT
Codex effort: {codex_effort}.
Codex does NOT use the ultraplan or goal slash commands (those are Claude-only).
Goal: poll for the {milestone} implementation branch, then audit it fully once pushed.

Do not stop after one missing-branch check.
Do not audit stale refs.
Start from remote truth.
Do not push main.
Do not clone/install/run external repos.
Do not accept fake green output.

IMPORTANT
Claude Code may still be implementing. Poll longer than usual.

TARGET BRANCH
{impl_branch}

TARGET REMOTE REF
refs/heads/{impl_branch}

AUDIT BRANCH
{audit_branch}

If the audit branch already exists on the remote:
- DO NOT force-push over it.
- Create a fresh branch with a higher suffix (e.g. -3 if -2 exists).
- Never overwrite a prior audit result.

BASE EXPECTED
origin/main at or after 70b1525dc473ba0cbd9a8562a00c5e417d0b416f

STEP 1 — POLL FOR REMOTE REF
Run:
git ls-remote origin refs/heads/{impl_branch}

If missing:
- git fetch origin --prune
- retry up to 60 times over about 45-60 minutes (one attempt every ~50s)
- list nearby n4-5a / relay / parallel-agent branches every 5 attempts

If still missing after 60 attempts:
- write BLOCKED_REMOTE_REF_MISSING report
- final verdict BLOCKED_REMOTE_REF_MISSING
- do not run normal audit

Only continue when remote branch exists.

STEP 2 — REMOTE TRUTH
After branch appears:
git fetch origin --prune
git rev-parse origin/{impl_branch}
git log origin/{impl_branch} --oneline -30

Verify:
- fetched local hash equals ls-remote hash
- branch is based on main at/after expected base commit

STEP 3 — ISOLATED AUDIT WORKTREE
Create inside the repo root. Never use C:\\w\\.
Branch from origin/main.
git merge --no-commit --no-ff origin/{impl_branch}
If conflicts: verdict BLOCKED_CONFLICTS

STEP 4 — VERIFY DELIVERABLES
Expected:
- 03_scripts/parallel_agent_relay.py
- 01_projects/runtime_mvp/tests/test_n4_5a_parallel_agent_relay_command_center.py
- 14_context/agent_relay/pairs/<seed_pair>/
- 14_context/claude_n4_5a_parallel_agent_relay_command_center.md
- Dashboard Parallel Agent Relay Truth section
- Server relay endpoints if implemented

Verify pair files include:
00_manifest.json, 01_claude_code_prompt.md, 02_codex_audit_prompt.md,
03_parallel_run_instructions.md, 04_status.json, 05_safety_review.md,
06_operator_checklist.md, 07_next_steps.md

STEP 5 — CLI VALIDATION
python 03_scripts/parallel_agent_relay.py --status --json
python 03_scripts/parallel_agent_relay.py --json
python 03_scripts/parallel_agent_relay.py --create-pair \\
  --milestone "N+4.5A Audit Test" \\
  --title "Parallel Agent Relay Audit Test" \\
  --implementation-branch "feat/test-implementation" \\
  --audit-branch "audit/test-audit" \\
  --codex-effort extra-high \\
  --write-packets --json

Validate:
- JSON valid
- pair folder created
- manifest has claude and codex lanes
- Claude prompt contains the ultraplan slash command
- Claude prompt contains the goal slash command
- Claude prompt mentions max planning and Sonnet high execution
- Codex prompt contains extra high
- Codex prompt does NOT contain the goal slash command
- Codex prompt includes polling remote refs
- Codex prompt says create fresh -3, never force-push
- safety review says no autonomous Claude/Codex launch
- external coordinator repos planning-only

STEP 6 — DASHBOARD/BACKEND VALIDATION
If endpoints exist, test:
GET /api/agent-relay/status
POST /api/agent-relay/create-pair
GET /api/agent-relay/latest
GET /api/agent-relay/pair?id=<pair_id>
GET /api/agent-relay/prompt?path=<repo-local-md-path>

Verify:
- no shell:true
- fixed argv
- repo-local md/json only
- no arbitrary file read
- no secret/env paths
- no automatic Claude/Codex launch

Verify dashboard labels:
- Parallel Agent Relay Truth
- Claude Code lane: ultraplan + goal slash commands
- Codex lane: extra high, poll remote refs
- paired prompt generation enabled
- manual copy-paste approval required
- no autonomous Claude/Codex launch
- Agent Exchange / AEX future-compatible
- Claude Cowork future-compatible

STEP 7 — TESTS AND REGRESSION
git diff --check
node --check dashboard JS files
python -m unittest all test modules (capture real pass/fail)
python script validations
pwsh check_runtime_mvp.ps1
pwsh check_dashboard_mvp.ps1

STEP 8 — SAFETY SCAN
- no secrets/API keys
- no autonomous Claude/Codex launch
- no external repo clone/install/run
- no external coordinator runtime wiring
- no live account/API/posting/money/trading actions
- prompt files repo-local only
- no arbitrary file read
- approval gates intact

STEP 9 — REPORT
Create: 14_context/codex_n4_5a_parallel_agent_relay_command_center_real_audit_3.md
(use -3 suffix; if -2 already exists, never overwrite)

Include all required fields and final verdict.

STEP 10 — COMMIT AND PUSH AUDIT
Stage only the audit report.
Commit: audit(ghoti): validate N+4.5A parallel agent relay
Push: {audit_branch} (or fresh -3 if -2 exists — never force-push)
Do not push main.
"""


def _safety_review(impl_branch: str, audit_branch: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""# Safety Review — Parallel Agent Relay Command Center (N+4.5A)

Generated: {now}

## Relay Mode
copy_paste_only

## Autonomous Launch
NO_AUTONOMOUS_LAUNCH

Human must manually copy and paste each prompt. No button, API call, or
subprocess starts Claude Code or Codex automatically.

## Claude Lane
- Humans copy 01_claude_code_prompt.md and paste into a Claude Code session.
- Claude Code implements on the feature branch.
- No automatic execution triggered by this relay.

## Codex Lane
- Humans copy 02_codex_audit_prompt.md and paste into a Codex session.
- Codex polls the remote ref (git ls-remote) and audits once Claude pushes.
- No automatic execution triggered by this relay.

## External Coordinator Repos
Planning-only. None are runtime-wired, cloned, installed, or run:
- Agent Exchange / AEX: future-compatible, not wired
- Claude Cowork: future-compatible, not wired
- The Agency: future-compatible, not wired
- agent-skills-eval: future-compatible, not wired

## Audit Branch Conflict Policy
If the audit branch already exists on the remote:
- DO NOT force-push over it.
- Create a fresh branch with a higher suffix (-3 if -2 exists).
- Prior audit results are preserved.

## Approval Gates
HUMAN APPROVAL REQUIRED at each step:
1. Before pasting any prompt into Claude Code or Codex.
2. Before pushing any branch.
3. Before any live/external action.
4. Before main merge (both CLEAN PASS required).

## Implementation Branch
{impl_branch}

## Audit Branch
{audit_branch}

## Final Verdict
NO_AUTONOMOUS_LAUNCH confirmed.
Copy-paste only. Human approval required at every step.
"""


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def get_status() -> dict:
    pairs = []
    if PAIRS_DIR.exists():
        for p in sorted(PAIRS_DIR.iterdir()):
            if not p.is_dir():
                continue
            manifest_path = p / "00_manifest.json"
            entry: dict = {"id": p.name}
            if manifest_path.exists():
                try:
                    with open(manifest_path, encoding="utf-8") as fh:
                        m = json.load(fh)
                    entry.update({
                        "milestone": m.get("milestone", ""),
                        "title": m.get("title", ""),
                        "created_at": m.get("created_at", ""),
                    })
                except Exception as exc:
                    entry["error"] = str(exc)
            else:
                entry["error"] = "no manifest"
            pairs.append(entry)

    latest = pairs[-1] if pairs else None
    return {
        "relay_version": RELAY_VERSION,
        "milestone_context": "N+4.5A",
        "pairs_dir": str(PAIRS_DIR.relative_to(REPO_ROOT)).replace(os.sep, "/"),
        "pair_count": len(pairs),
        "latest_pair": latest,
        "pairs": pairs,
        "relay_mode": "copy_paste_only",
        "autonomous_launch": False,
        "human_approval_required": True,
        "future_compatible": {
            "agent_exchange_aex": True,
            "claude_cowork": True,
            "the_agency": True,
            "agent_skills_eval": True,
        },
        "labels": {
            "title": "Parallel Agent Relay Truth",
            "claude_lane": "/ultraplan + /goal",
            "codex_lane": "extra high, poll remote refs",
            "paired_prompt_generation": "enabled",
            "manual_copy_paste_approval": "required",
            "autonomous_claude_codex_launch": "disabled",
            "agent_exchange_aex": "future-compatible",
            "claude_cowork": "future-compatible",
            "the_agency": "future-compatible",
            "agent_skills_eval": "future-compatible",
        },
        "generated_at": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
    }


# ---------------------------------------------------------------------------
# Pair creation
# ---------------------------------------------------------------------------

def _make_pair_id(milestone: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = "".join(
        c if (c.isalnum() or c in "-_") else "_"
        for c in milestone.lower()
    )[:40].strip("_")
    return f"{ts}_{slug}"


def create_pair(
    milestone: str,
    title: str,
    impl_branch: str,
    audit_branch: str,
    codex_effort: str = "extra-high",
    output_dir=None,
    write_packets: bool = False,
) -> dict:
    pair_id = _make_pair_id(milestone)
    base_dir = _require_repo_local(output_dir) if output_dir else PAIRS_DIR
    pair_dir = base_dir / pair_id

    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rel_base = f"14_context/agent_relay/pairs/{pair_id}"
    claude_prompt_rel = f"{rel_base}/01_claude_code_prompt.md"
    codex_prompt_rel  = f"{rel_base}/02_codex_audit_prompt.md"

    claude_prompt = _claude_prompt(milestone, title, impl_branch, audit_branch)
    codex_prompt  = _codex_prompt(milestone, title, impl_branch, audit_branch, codex_effort)
    safety        = _safety_review(impl_branch, audit_branch)

    manifest = {
        "pair_id": pair_id,
        "milestone": milestone,
        "title": title,
        "created_at": now,
        "relay_version": RELAY_VERSION,
        "lanes": {
            "claude": {
                "role": "implementation",
                "branch": impl_branch,
                "prompt_path": claude_prompt_rel,
                "model": "Claude Sonnet 4.6",
                "effort": "high",
                "planning": "/ultraplan max",
                "execution": "/goal Sonnet high",
                "autonomous_launch": False,
            },
            "codex": {
                "role": "audit",
                "branch": audit_branch,
                "prompt_path": codex_prompt_rel,
                "effort": codex_effort,
                "planning": "none (audit only, no /ultraplan, no /goal)",
                "execution": f"poll remote refs ({codex_effort}), audit once branch appears",
                "autonomous_launch": False,
            },
        },
        "relay_mode": "copy_paste_only",
        "human_approval_required": True,
        "autonomous_launch": False,
        "external_coordinator_repos": "planning_only",
        "future_compatible": {
            "agent_exchange_aex": True,
            "claude_cowork": True,
            "the_agency": True,
            "agent_skills_eval": True,
        },
    }

    run_instructions = f"""# Parallel Run Instructions — {milestone}: {title}

## Overview
Run Claude Code and Codex in parallel using the generated prompt packets.
Claude implements while Codex polls and waits. Both run simultaneously.

## Step 1 — Open Claude Code
Copy and paste the contents of:
  01_claude_code_prompt.md

Claude Code will:
- Use /ultraplan for deep planning (maximum effort)
- Use /goal for long-horizon execution (Sonnet 4.6 high)
- Implement all deliverables on {impl_branch}
- Run validations, write report, commit, and push

## Step 2 — Open Codex (run in parallel with Step 1)
Copy and paste the contents of:
  02_codex_audit_prompt.md

Codex will:
- Poll for the implementation branch (git ls-remote, every ~50s, up to 60 attempts)
- Wait until Claude pushes the branch
- Audit all deliverables once the branch appears
- Push audit report to {audit_branch} (or fresh -3 if -2 exists — never force-push)

## Step 3 — Human Review and Approval
- Review Claude Code's implementation commit
- Review Codex's audit report
- Approve main merge ONLY if both show CLEAN PASS / IMPLEMENTED_AND_PUSHED
- If either is BLOCKED: investigate root cause before proceeding

## Safety
- No button or automated trigger starts Claude Code or Codex.
- Human must manually paste each prompt.
- Human must review all output before any main merge.
- Approval gates are intact at every step.

## Codex effort: {codex_effort}
## Claude planning: /ultraplan max
## Claude execution: /goal Sonnet high
"""

    status_content = {
        "pair_id": pair_id,
        "status": "ready",
        "created_at": now,
        "claude_lane": "pending_human_paste",
        "codex_lane": "pending_human_paste",
        "implementation_branch": impl_branch,
        "audit_branch": audit_branch,
        "codex_effort": codex_effort,
    }

    operator_checklist = f"""# Operator Checklist — {milestone}: {title}

## Pre-Launch
- [ ] Review 01_claude_code_prompt.md before pasting into Claude Code
- [ ] Review 02_codex_audit_prompt.md before pasting into Codex
- [ ] Confirm implementation branch: {impl_branch}
- [ ] Confirm audit branch: {audit_branch}
- [ ] Confirm Codex effort: {codex_effort}
- [ ] Confirm no live actions will be triggered

## Claude Code Lane
- [ ] Open a fresh Claude Code session
- [ ] Paste 01_claude_code_prompt.md
- [ ] Monitor until IMPLEMENTED_AND_PUSHED or confirmed blocker
- [ ] Record commit hash returned by Claude Code

## Codex Lane (run in parallel with Claude lane)
- [ ] Open a fresh Codex session
- [ ] Paste 02_codex_audit_prompt.md
- [ ] Codex will poll (git ls-remote) and wait for Claude to push
- [ ] Monitor until CLEAN PASS or BLOCKED

## Post-Audit Review
- [ ] Review Claude Code implementation commit on GitHub
- [ ] Review Codex audit report in {audit_branch}
- [ ] Both CLEAN PASS? Approve main merge gate
- [ ] Either BLOCKED? Investigate root cause, fix, re-run

## Safety Gates (must hold)
- [ ] No live account actions taken by either agent
- [ ] No external repos cloned, installed, or run
- [ ] No secrets committed to any branch
- [ ] Human approval confirmed for all pushes
- [ ] Main merge approved only after human review
"""

    next_steps = f"""# Next Steps — {milestone}: {title}

## After Claude pushes {impl_branch}

1. Codex poll detects branch (git ls-remote returns hash).
2. Codex proceeds to audit: fetch, merge --no-commit, verify deliverables.
3. Codex runs full regression suite (python -m unittest, node --check, pwsh checks).
4. Codex writes audit report to 14_context/.
5. Codex pushes audit to {audit_branch} (fresh -3 if -2 exists — never force-push).

## After Codex audit is complete

1. Human reviews both reports on GitHub.
2. If both CLEAN PASS:
   - Approve main merge gate.
   - Run final main merge (separate merge gate process).
3. If either BLOCKED:
   - Investigate root cause.
   - Fix on the implementation branch.
   - Re-run the failing lane.

## Future: Agent Exchange / AEX

When AEX becomes available, this relay workflow will be enhanced via:
- Claude Cowork for automated implementation coordination
- The Agency for audit orchestration
- agent-skills-eval for skill benchmarking

Currently: copy-paste only. Human approval required at every step.

## Codex effort: {codex_effort}
## Claude planning: /ultraplan max
## Claude execution: /goal Sonnet high
"""

    result: dict = {
        "pair_id": pair_id,
        "pair_dir": None,
        "claude_prompt_path": None,
        "codex_prompt_path": None,
        "manifest": manifest,
        "relay_mode": "copy_paste_only",
        "generated_at": now,
    }

    if write_packets:
        pair_dir.mkdir(parents=True, exist_ok=True)
        files = {
            "00_manifest.json":              json.dumps(manifest, indent=2),
            "01_claude_code_prompt.md":      claude_prompt,
            "02_codex_audit_prompt.md":      codex_prompt,
            "03_parallel_run_instructions.md": run_instructions,
            "04_status.json":                json.dumps(status_content, indent=2),
            "05_safety_review.md":           safety,
            "06_operator_checklist.md":      operator_checklist,
            "07_next_steps.md":              next_steps,
        }
        for fname, content in files.items():
            with open(pair_dir / fname, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(content)
        result["pair_dir"] = str(pair_dir.relative_to(REPO_ROOT)).replace(os.sep, "/")
        result["claude_prompt_path"] = claude_prompt_rel
        result["codex_prompt_path"]  = codex_prompt_rel
        result["files_written"] = list(files.keys())

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parallel Agent Relay Command Center — N+4.5A"
    )
    parser.add_argument("--status",       action="store_true")
    parser.add_argument("--json",         action="store_true", dest="output_json")
    parser.add_argument("--create-pair",  action="store_true")
    parser.add_argument("--milestone",    default="")
    parser.add_argument("--title",        default="")
    parser.add_argument("--implementation-branch", default="", dest="impl_branch")
    parser.add_argument("--audit-branch",          default="", dest="audit_branch")
    parser.add_argument("--codex-effort", default="extra-high", dest="codex_effort")
    parser.add_argument("--write-packets", action="store_true")
    parser.add_argument("--output-dir",   default=None, dest="output_dir")
    args = parser.parse_args()

    if args.create_pair:
        required = [
            ("--milestone",             args.milestone),
            ("--title",                 args.title),
            ("--implementation-branch", args.impl_branch),
            ("--audit-branch",          args.audit_branch),
        ]
        for flag, val in required:
            if not val:
                err = {"ok": False, "error": f"{flag} is required for --create-pair"}
                print(json.dumps(err))
                sys.exit(1)
        try:
            result = create_pair(
                milestone=args.milestone,
                title=args.title,
                impl_branch=args.impl_branch,
                audit_branch=args.audit_branch,
                codex_effort=args.codex_effort,
                output_dir=args.output_dir,
                write_packets=args.write_packets,
            )
            result["ok"] = True
            if args.output_json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Pair created: {result['pair_id']}")
                if result.get("pair_dir"):
                    print(f"Pair dir:    {result['pair_dir']}")
                print(f"Claude:      {result.get('claude_prompt_path', 'n/a')}")
                print(f"Codex:       {result.get('codex_prompt_path', 'n/a')}")
        except ValueError as exc:
            out = {"ok": False, "error": str(exc)}
            if args.output_json:
                print(json.dumps(out))
            else:
                print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)
        return

    # Default / --status / bare --json: print status
    status = get_status()
    if args.output_json or args.status:
        print(json.dumps(status, indent=2))
    else:
        print(f"Parallel Agent Relay v{RELAY_VERSION}")
        print(f"Pairs: {status['pair_count']}")
        if status["latest_pair"]:
            lp = status["latest_pair"]
            print(f"Latest: {lp.get('id', '?')}")


if __name__ == "__main__":
    main()
