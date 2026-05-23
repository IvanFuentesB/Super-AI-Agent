This is a Codex audit task for N+4.5A Seed — Parallel Agent Relay Seed Pair.

MODE / EFFORT
Codex effort: extra-high.
Codex does NOT use /goal.
Codex does NOT use /ultraplan.
Goal: poll for the N+4.5A Seed implementation branch, then audit it fully once pushed.

Do not stop after one missing-branch check.
Do not audit stale refs.
Start from remote truth.
Do not push main.
Do not clone/install/run external repos.
Do not accept fake green output.

IMPORTANT
Claude Code may still be implementing. Poll longer than usual.

TARGET BRANCH
feat/ghoti-agent-claude-n4-5a-parallel-agent-relay-command-center

TARGET REMOTE REF
refs/heads/feat/ghoti-agent-claude-n4-5a-parallel-agent-relay-command-center

AUDIT BRANCH
audit/ghoti-agent-codex-n4-5a-parallel-agent-relay-command-center-real-audit-3

If the audit branch already exists on the remote:
- DO NOT force-push over it.
- Create a fresh branch with a higher suffix (e.g. -3 if -2 exists).
- Never overwrite a prior audit result.

BASE EXPECTED
origin/main at or after 70b1525dc473ba0cbd9a8562a00c5e417d0b416f

STEP 1 — POLL FOR REMOTE REF
Run:
git ls-remote origin refs/heads/feat/ghoti-agent-claude-n4-5a-parallel-agent-relay-command-center

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
git rev-parse origin/feat/ghoti-agent-claude-n4-5a-parallel-agent-relay-command-center
git log origin/feat/ghoti-agent-claude-n4-5a-parallel-agent-relay-command-center --oneline -30

Verify:
- fetched local hash equals ls-remote hash
- branch is based on main at/after expected base commit

STEP 3 — ISOLATED AUDIT WORKTREE
Create inside the repo root. Never use C:\w\.
Branch from origin/main.
git merge --no-commit --no-ff origin/feat/ghoti-agent-claude-n4-5a-parallel-agent-relay-command-center
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
python 03_scripts/parallel_agent_relay.py --create-pair \
  --milestone "N+4.5A Audit Test" \
  --title "Parallel Agent Relay Audit Test" \
  --implementation-branch "feat/test-implementation" \
  --audit-branch "audit/test-audit" \
  --codex-effort extra-high \
  --write-packets --json

Validate:
- JSON valid
- pair folder created
- manifest has claude and codex lanes
- Claude prompt contains /ultraplan
- Claude prompt contains /goal
- Claude prompt mentions max planning and Sonnet high execution
- Codex prompt contains extra high
- Codex prompt does NOT contain /goal
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
- no JS shell true option
- fixed argv
- repo-local md/json only
- no arbitrary file read
- no secret/env paths
- no automatic Claude/Codex launch

Verify dashboard labels:
- Parallel Agent Relay Truth
- Claude Code lane: /ultraplan + /goal
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
Push: audit/ghoti-agent-codex-n4-5a-parallel-agent-relay-command-center-real-audit-3 (or fresh -3 if -2 exists — never force-push)
Do not push main.
