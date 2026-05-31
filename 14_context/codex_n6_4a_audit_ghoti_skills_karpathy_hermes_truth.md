# Codex Audit Report - N+6.4A Ghoti Skills / Karpathy / Hermes Truth

Date: 2026-05-31

Auditor: Codex

## Verdict

BLOCKED

The milestone content is broadly present and the runtime validation passes, but
the target feature commit contains an AI co-author trailer:

`Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>`

This violates the explicit audit rule: no AI co-author trailers. Because the
target branch is not merge-ready under the stated rules, this audit branch
records a BLOCKED verdict.

## Branches

- Target branch: `feat/ghoti-agent-claude-n6-4a-ghoti-skills-karpathy-hermes-truth`
- Target commit audited: `a70c756f4b25b1f2cda17825a90d754ec089cd1b`
- Starting main: `8613508674deb9abb44dc1b9e5a54dfee3261ee6`
- Audit branch: `audit/ghoti-agent-codex-n6-4a-ghoti-skills-karpathy-hermes-truth`
- Audit merge HEAD before this report: `cbe8eaa2add00ad3e729dbcffda7230b2c637695`

Fetch note: `git fetch origin --prune` from the dirty primary worktree failed
with local permission/proxy errors, so this audit used the existing local
remote-tracking refs. The target remote-tracking ref and origin/main ref were
present locally and were verified before the audit merge.

## Required Artifacts

All required milestone artifacts were present after merging the target branch
into the isolated audit worktree:

- `14_context/agent_handoff_vault/`
- `14_context/ghoti_current_truth.md`
- `docs/HERMES_LOCAL_SETUP_CURRENT_TRUTH.md`
- `docs/GHOTI_SKILLS_AND_AGENT_WORKFLOW.md`
- `docs/CLAUDE_CODE_SKILLS_POLICY.md`
- `docs/CODEX_AUDIT_WORKFLOW.md`
- `14_context/skills/ghoti_skill_registry.md`
- `14_context/skills/karpathy_guidelines_intake.md`
- `14_context/skills/claude_code_skill_install_log.md`
- `14_context/skills/codex_working_rules.md`
- `01_projects/runtime_mvp/tests/test_n6_4a_ghoti_skills_karpathy_hermes_truth.py`
- `14_context/agent_handoff_vault/05_Backlog/dashboard_performance_and_local_analytics.md`

## Truth Registration

PASS for documentation truth:

- ChatGPT is represented as the main strategy / architecture / prompt brain.
- Hermes is represented as the local coordinator / switchboard / memory writer.
- Obsidian is represented as durable shared memory / handoff board.
- Claude Code is represented as implementation.
- Codex is represented as audit / review / verification.
- Gemma is represented as cheap summaries / compression / classification.
- Llama is represented as the Hermes local coordinator brain.
- Human is represented as final approval.
- Hermes v0.14.0 is recorded.
- `llama3.1:8b` and `gemma3:4b` are recorded as available.
- qwen is recorded as removed.
- Telegram is recorded as not configured.
- Browser/computer-use is recorded as not enabled for Ghoti.

## Dashboard Performance / Local Analytics Verdict

PASS as backlog-only direction.

`14_context/agent_handoff_vault/05_Backlog/dashboard_performance_and_local_analytics.md`
documents that the dashboard should become fast, reliable, and low-friction, and
that any future analytics must be local-first, privacy-safe, opt-in,
inspectable, and reversible.

It names future local metrics such as page/view events, feature usage, command
counts, task success/failure, latency/performance, and errors. It also clearly
states:

- no external tracking by default
- no invasive telemetry
- no analytics leaving the machine without explicit human approval
- no claim that production analytics is implemented in N+6.4A

## Safety Audit

PASS for content and runtime wiring, BLOCKED for commit attribution.

The N+6.4A files do not introduce live provider setup, Telegram setup, browser
automation, computer-use click/type, live APIs, external telemetry, secrets, or
runtime wiring of unsafe external skills.

The target commit attribution is the only blocker found.

## Validation

- `git diff --check`: PASS
- `git show --check --stat HEAD`: PASS
- `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_*.py" -v`: PASS on elevated rerun, 30 tests OK
- `python 03_scripts/ghoti_product_launcher.py --status --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --context-pack --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --repo-map --json`: PASS
- `python 03_scripts/public_repo_security_audit.py --run --json`: completed with 150 checks, 0 blockers, 8 warnings, and 1 non-blocking failed attribution check

N+6 test note: the first sandboxed unittest run hit Windows `PermissionError`
while creating/removing temporary directories under dashboard `runtime_data`.
The same N+6 suite passed when rerun with normal filesystem permissions.

Public audit note: direct commit inspection confirmed the target feature commit
has an actual AI co-author trailer. This is treated as a blocker even though the
public audit's blocking findings list is empty.

## Blockers

1. Target commit `a70c756f4b25b1f2cda17825a90d754ec089cd1b` contains:
   `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>`

## Cleanup

- Validation-generated context pack and repo knowledge artifacts were restored.
- Primary worktree was not edited.
- No generated validation residue is intentionally committed except this audit
  report.

## Exact Next Action

Do not merge the current target branch.

Create a clean replacement feature branch from `origin/main` that applies the
same file tree/content without an AI co-author trailer, or otherwise produce a
merge strategy that lands the changes on main without preserving the offending
feature commit in main history. Then rerun this Codex audit against the clean
replacement branch.

Final verdict: BLOCKED.
