# Claude Skills Status — N+1.6

**Date:** 2026-04-24  
**Branch:** feat/ghoti-visible-operator-stack

## Folder audit

| Path | Exists |
|------|--------|
| `.claude/skills/` (repo-local, untracked) | YES |
| `%USERPROFILE%\.claude\skills\` (user-level) | NO |
| `21_repos/third_party/awesome-claude-skills` | YES |

## Current state

- The repo-local `.claude/skills/` folder exists and is **untracked** (not in git).
- The user-level `%USERPROFILE%\.claude\skills\` does not yet exist.
- `awesome-claude-skills` is present in the third-party intake folder as reference.

## Recommended safe installation path (future milestone)

1. Inspect available skills one by one in `awesome-claude-skills`
2. Evaluate each skill for trust, safety, and usefulness
3. Install only useful skills — copy to `.claude/skills/` or the user folder
4. Avoid any skill that runs shell commands without confirmation or exposes API keys
5. Maintain a skills inventory doc (what is installed, why, when)
6. Never expose API keys or tokens inside skill files

## This milestone

Documentation only. No skills staged or installed. The repo-local `.claude/skills/` folder is intentionally not staged.
