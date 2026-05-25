# Local Worker Safe Tasks

Ghoti local worker routing is for compact, low-risk, offline work. It is not an autonomous operator.

Safe tasks in N+6.1A:

- summarize the latest Ghoti report
- produce a one-paragraph status
- generate a concise Codex next prompt
- classify a request as safe or risky
- summarize a known repo context bundle
- outline the next milestone
- turn a report into short bullets

Every routed task must pass the output guard or use `local_demo` fallback. Model output is text only. It must never trigger command execution, file edits, browser clicks, live API calls, posting, money/trading/legal decisions, account actions, or credential/session handling.

Run:

```powershell
python 03_scripts/local_model_worker_lane.py --routing-status --json
python 03_scripts/local_model_worker_lane.py --route-task status-paragraph --json
python 03_scripts/local_model_worker_lane.py --write-routing-demo --json
```

Safety boundaries: no live APIs, no browser control, no autonomous account actions, no provider setup, and no shell commands from model output.
