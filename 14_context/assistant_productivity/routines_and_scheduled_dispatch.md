# Routines and Scheduled Dispatch

The source of truth is `23_configs/assistant_productivity/routines.example.json`.
Every routine is disabled and `prompt_only`. This is a dispatch specification,
not a live scheduler.

| Routine | Owner | Output | Safe trigger |
|---|---|---|---|
| Morning dashboard review | ChatGPT/Cowork | local brief | human opens routine |
| Daily branch/PR status | Codex | read-only Git/PR summary | manual or approved scheduler later |
| Daily agent handoff summary | Hermes | compact handoff digest | manual |
| Weekly tool intake review | Codex | inspect-first queue review | manual |
| Weekly MCP connector review | Codex | disabled/read-only readiness matrix | manual |
| Weekly money-lane review | ChatGPT/Cowork | research and risk ranking | manual |
| Pre-merge test/audit reminder | Codex | verification checklist | before merge |
| Credits/statusline review | Human | honest usage/reset view | manual |

## Scheduling rule

Only schedule a routine after the platform supports a reviewed local prompt-only
job and the human explicitly approves it. A scheduler may prepare a local
artifact; it must not send, post, purchase, authenticate, merge, or control a
browser.
