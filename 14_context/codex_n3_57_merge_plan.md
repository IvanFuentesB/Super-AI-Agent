# Codex N+3.57 - Merge Plan

## Merge Verdict

BLOCKED / PENDING TARGET BRANCH.

Do not merge N+3.56-FIX because the target branch does not exist on the remote.

## Required Operator Action

Claude or the operator must push the branch:

```powershell
git push origin feat/ghoti-agent-claude-n3-56-fix-bridge-ruflo-gemma-clean-pass
```

## Audit Commands After Branch Exists

```powershell
git fetch origin
git rev-parse origin/feat/ghoti-agent-claude-n3-56-fix-bridge-ruflo-gemma-clean-pass
git switch -c audit/ghoti-agent-codex-n3-57-n3-56-fix-clean-pass-audit-v2 origin/feat/ghoti-visible-operator-stack
git merge --no-commit --no-ff origin/feat/ghoti-agent-claude-n3-56-fix-bridge-ruflo-gemma-clean-pass
```

Then run the full N+3.57 validation suite before any merge to main.

## Merge Commands If Future Audit Passes

Only after PASS:

```powershell
git switch feat/ghoti-visible-operator-stack
git pull --ff-only origin feat/ghoti-visible-operator-stack
git fetch origin
git merge --no-ff origin/feat/ghoti-agent-claude-n3-56-fix-bridge-ruflo-gemma-clean-pass -m "merge(ghoti): land N+3.56 bridge clean-pass hardening"
git diff --check
git push origin feat/ghoti-visible-operator-stack
```

## Do Not Merge If

- Target branch is missing.
- Canonical prompt/memory can be overwritten without explicit flag.
- Course helper enables fake certificates, cheating, impersonation, or assessment submission.
- Any live actions, secret reads, Ruflo runtime launch, MCP/swarm launch, `npx`, or global install path appears.
