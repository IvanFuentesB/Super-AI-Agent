---
description: Show current Ghoti repo status — git state, lane locks, and lane statuses.
allowed-tools: Bash
---

Run these commands and summarize the results:

```bash
git status --short
git branch --show-current
git log --oneline -8
python 03_scripts/agent_lane_status.py --check
python 03_scripts/agent_lane_status.py --list
python 03_scripts/prompt_bus.py --status
```

Summarize:
- Current branch
- HEAD commit
- Active lane locks (if any)
- Latest lane statuses (if any)
- Canonical Claude prompt path and last-modified
- Outbox prompt count
- Any untracked/modified files that are relevant (skip known dirt: CVs, skills, logs)
