# Ghoti Agent Vault — Start Here

This vault is the shared memory and handoff board for Ghoti.

Main flow:
1. ChatGPT designs the plan.
2. Hermes writes/maintains handoff notes.
3. Claude implements only assigned tasks.
4. Codex audits.
5. Human approves risky actions and merges.

Do not store secrets here.
Do not let multiple agents edit the same files.
Use branches/worktrees.
