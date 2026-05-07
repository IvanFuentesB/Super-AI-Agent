# CLAUDE.md — Ghoti Supervised Operator System

## Scope
- Repo root: `C:\Users\ai_sandbox\Documents\AI_Managed_Only`
- All work must stay inside this root. No traversal to parent directories or other user profiles.
- Reference intake repos under `21_repos/third_party` are read-only; do not modify them.

## Safety Model (preserve as-is)
- Approval gates for risky or outbound actions must not be weakened.
- Any action that writes outside the repo root, executes remote calls, or mutates shared state requires explicit user confirmation before proceeding.
- Ask before running shell commands that delete files, push to remotes, modify git history, or touch environment variables.
- Deny reads of `.env`, secret files, credential stores, and OS-level environment variables unless the user explicitly authorizes it in the same turn.
- Stop after 2 repeated failures on the same root-cause issue and surface the blocker.

## Behavior Rules
- Minimal necessary changes only — no features, refactors, or cleanup beyond what was asked.
- No task deletion.
- Prefer compact memory files under `14_context/compact_memory/`.
- Keep outputs concise and factual.

## Key Directories
| Path | Purpose |
|------|---------|
| `01_projects/runtime_mvp` | Core Python runtime and CLI |
| `02_automation` | Automation scripts and configs |
| `14_context/compact_memory` | Preferred location for durable context snapshots |
| `20_agents` | Agent templates and memory |
| `21_repos/third_party` | Read-only reference intake |
| `23_configs` | Local config files |

## Stack
- Python >= 3.11, setuptools build backend
- Entry point: `super-agent` CLI (`super_ai_agent.cli:main`)
- No test framework configured yet

## Working Method
- Summarized context files over long chats.
- Changes small and reversible.
- Risky or outbound actions require approval.
