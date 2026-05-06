# Codex N+3.57 - Next Sequence Lock

## Current Lock

N+3.56-FIX is blocked because the target branch is missing on the remote.

## Exact Next Claude Recommendation

Claude should finish, commit, and push:

```text
feat/ghoti-agent-claude-n3-56-fix-bridge-ruflo-gemma-clean-pass
```

Required fix scope:

- `course_certificate_assistant.py` supports `--goal`.
- `cc_codex_bridge.py` has clean `--init`, `--status`, and `--write-pair` behavior.
- Obsidian detection is unified across probe, dashboard, and PowerShell helper.
- Ruflo source/install wording is truthful for clean checkouts.
- `local_worker_router.py` routes bridge handoff tasks to the bridge helper.
- Prompt-bus canonical overwrite protection remains explicit.
- Dashboard labels remain truthful.
- Gemma/Ruflo/Obsidian checks are accurate.

## Exact Next Codex Recommendation

After the branch is pushed, rerun N+3.57 hard audit from a clean auxiliary worktree and do not rely on primary-worktree dirty files.

## Exact Next Operator Command

```powershell
git push origin feat/ghoti-agent-claude-n3-56-fix-bridge-ruflo-gemma-clean-pass
```

## Do Not Do Next

- Do not merge from local dirty files.
- Do not merge a missing branch.
- Do not run Ruflo runtime, MCP, swarm, `npx`, or global installs.
- Do not read secrets or `.env`.
- Do not post, email, pay, scrape, apply to jobs, create fake certificates, cheat, or submit assessments.
