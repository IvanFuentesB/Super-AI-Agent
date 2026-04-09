# Decisions

- Canonical workspace root is C:\Users\ai_sandbox\Documents\AI_Managed_Only
- Anything outside the canonical workspace root is out-of-scope by default and must not execute normally without explicit human approval or a future allowlist expansion
- Do not touch files or areas outside the canonical workspace root unless the user explicitly approves it
- Do not affect the other Windows profile
- No task should be deleted without the user's explicit approval; prefer archive, filter, and history visibility instead
- System direction is local-first where practical
- Risky actions require approval
- Durable memory stays compact and summarized
- Operator stack and provider brain should stay separable so future model or provider swaps do not require rewriting the whole system
- Continue is the current local control layer
- Codex is the current execution layer
- Local Git repo is initialized
- Project is pushed to a private GitHub repo named Super-AI-Agent
- Claw Code remains temporary reference, not foundation
- Notion is not integrated yet
