# GHOTI N+6.32A — Strict No-AI-Attribution Guard

## Overview

N+6.32A adds a forward-looking guard so the GitHub contributor / co-author /
author / committer surface is never populated with an AI identity again
(for example `claude`, `gpt` / `chatgpt`, `codex`, `anthropic`, `openai`, or a
generic `assistant` / `bot`).

**Original feature base:** `ca90fbd`
**Branch:** `feat/ghoti-agent-claude-n6-32a-no-ai-attribution-guard`

The guard itself does **not** rewrite history or force-push. It prevents future
contamination and adds checks. N+6.32B separately completed the explicitly
approved targeted cleanup before this guard was merged.

---

## Root cause

The local git identity had been set to an AI name/email, so commits made on the
feature branches were authored and committed under that identity. The fix:

1. Reset the local git identity to the human operator (`IvanFuentesB`).
2. Extend the existing audit to also inspect the **committer** line.
3. Add a dedicated unittest guard that runs in the normal test suite.

---

## What the guard checks

| # | Check | Severity | Where |
|---|-------|----------|-------|
| 1 | Configured git identity (next commit) is not an AI | hard fail | `test_n6_32a_*` |
| 2 | HEAD author **and** committer are not an AI | hard fail | `test_n6_32a_*` + audit |
| 3 | New commit messages (`origin/main..HEAD`) carry no AI attribution trailer | hard fail | `test_n6_32a_*` + audit |
| 4 | New commit authors/committers in range are not an AI | hard fail | `test_n6_32a_*` |
| 5 | Tracked docs do not name an AI as a co-author / contributor / collaborator | hard fail | `test_n6_32a_*` |
| 6 | Historical inherited AI authorship in range | reviewed warning | audit only |

The forbidden trailer forms the guard rejects include the `Co-authored-by`
trailer naming an AI, the "generated with / by `<AI>`" phrasing, the robot-emoji
"generated" phrasing, and prose asserting an AI "is a"/"as a" co-author,
contributor, or collaborator.

Normal workflow prose is intentionally **not** flagged — e.g. "Claude Code
implements features; Codex audits each branch" passes, because the patterns are
scoped to attribution/identity, not to any mention of a tool name.

---

## Files

| File | Change |
|------|--------|
| `01_projects/runtime_mvp/tests/test_n6_32a_no_ai_attribution_guard.py` | New unittest guard |
| `03_scripts/public_repo_security_audit.py` | Extended attribution check to include committer (`%cn <%ce>`) and explicit "generated with `<AI>`" phrasing |
| `docs/GHOTI_N6_32A_NO_AI_ATTRIBUTION_GUARD.md` | This document |
| `14_context/claude_n6_32a_no_ai_attribution_guard.md` | Context snapshot |

---

## Post-cleanup truth

N+6.32B replaced the forbidden author/committer identity on the affected main
commit and sanitized the pending N+6.29A, N+6.30A, N+6.31A, and N+6.32A feature
refs. Cleaned `origin/main` and those pending refs no longer contain the old bad
commit or the forbidden author/committer identity.

The guard remains forward-looking: it ensures every new commit uses a human
operator identity and carries no attribution trailer. Historical message-only
attribution text outside the targeted cleanup remains review-only because broad
history rewriting was explicitly out of scope.

---

## Overlap with the Codex audit (no duplication)

- **Codex audit** (`docs/CODEX_AUDIT_WORKFLOW.md`) covers scope, safety,
  truthfulness, validation, and reversibility. It does **not** inspect git
  author/committer identity or attribution trailers. **No overlap.**
- **`public_repo_security_audit.py`** already checked the latest commit author
  and message and warned on inherited range trailers. N+6.32A **extends** it
  (committer line + explicit "generated with `<AI>`" phrasing) rather than
  duplicating it, and adds a unittest so the rule runs in the test suite.

---

## Codex Audit Target

`audit/ghoti-agent-codex-n6-32a-no-ai-attribution-guard`
