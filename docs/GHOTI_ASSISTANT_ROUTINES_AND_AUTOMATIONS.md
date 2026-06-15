# Ghoti Assistant Routines and Automations

The routines layer is a disabled prompt/spec pack, not an autonomous scheduler.
See:

- `23_configs/assistant_productivity/routines.example.json`
- `14_context/assistant_productivity/routines_and_scheduled_dispatch.md`

It defines morning dashboard review, daily PR/status and handoff summaries,
weekly tool/MCP/money-lane reviews, a pre-merge audit reminder, and an honest
credits/statusline check. Every routine is `enabled:false`,
`mode:prompt_only`, and `live_actions:false`.

Future scheduling may prepare local artifacts after explicit approval. It must
not send email, post content, spend money, trade, authenticate accounts, merge,
or control a browser.
