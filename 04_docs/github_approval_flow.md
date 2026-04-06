# GitHub Approval Flow

- Read-only GitHub inspection does not require extra approval
- Local draft generation is low-risk and allowed
- Local branch creation requires approval
- Remote issue creation requires approval
- Remote PR creation requires approval
- The CLI must receive an explicit `--approve yes` for write actions
- All write commands should return readable results or readable refusal messages
- If approval is absent, the system should refuse cleanly
