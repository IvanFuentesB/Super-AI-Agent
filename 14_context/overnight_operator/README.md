# Overnight Operator MVP

N+6.19A starts the first useful overnight-operator loop while keeping live app control blocked.

The lane can:

- build copy/paste-ready prompt packets from local queue tasks
- keep local inbox/outbox/archive folders for operator handoff
- dry-run clipboard relay without pasting into apps
- clone allowlisted external repos into `21_repos/third_party_runtime_sandbox/`
- static-scan allowlisted repos and run read-only metadata commands
- extract ECC, GBrain, and MarkItDown patterns into Ghoti reports

It cannot:

- paste into apps
- auto-submit anything
- launch live agents
- configure Telegram, MCP, providers, or tokens
- control browsers or OS windows
- run Docker, installers, arbitrary scripts, or unbounded commands
- push or merge main

N+6.20A is the approved-window copy/paste harness, still human-approved and still blocked from auto-submit.
