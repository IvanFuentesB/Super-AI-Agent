# Context Snapshot — N+6.32A No-AI-Attribution Guard

**Milestone:** N+6.32A
**Date:** 2026-06-08
**Branch:** `feat/ghoti-agent-claude-n6-32a-no-ai-attribution-guard`
**Base:** `ca90fbd`
**Status:** IMPLEMENTED_AND_PUSHED — awaiting Codex audit

---

## What this milestone does

Adds a forward-looking guard so the GitHub contributor/co-author/author/committer
surface is never populated with an AI identity again. Does not rewrite history,
does not force-push.

## Root cause found

The local git identity was set to an AI name/email, so feature-branch commits
were authored/committed under it. Fixed by resetting the local git identity to
the human operator and adding checks.

## Changes

- `03_scripts/public_repo_security_audit.py` — attribution check now inspects the
  committer line (`%cn <%ce>`) in addition to the author, and the forbidden
  regex now explicitly includes the "generated with/by <AI>" phrasing and `gpt`.
- `01_projects/runtime_mvp/tests/test_n6_32a_no_ai_attribution_guard.py` — new
  unittest guard (identity, HEAD author+committer, new-range messages, new-range
  authors/committers, doc collaborator wording, plus regex sanity tests).
- `docs/GHOTI_N6_32A_NO_AI_ATTRIBUTION_GUARD.md` — milestone doc.

## Guard scope (forward-looking, no rewrite)

Hard-fails on: configured identity is AI; HEAD author/committer is AI; new commit
messages carry an AI attribution trailer; new commit authors/committers are AI;
docs name an AI as co-author/contributor/collaborator.

Does NOT hard-fail on already-pushed inherited authorship — that is a reviewed
warning in the audit (respecting no-force-push / no-rewrite).

## Branch confirmations (this session)

| Branch | Confirmation |
|--------|-------------|
| N+6.29A | file:// remote-authority fix present; 56 tests pass |
| N+6.30A | Dreams/memory consolidation patch present; 36 tests pass |
| N+6.31A | rust/target/ gitignored; 19 rust + 42 python tests pass |

All three still have pre-existing AI-authored commits (left as-is; not rewritten).

## Overlap with Codex audit

Codex audit does not cover git identity/attribution — no duplication. N+6.32A
extends the existing Ghoti audit and adds a unittest.

## Codex audit target

`audit/ghoti-agent-codex-n6-32a-no-ai-attribution-guard`
