# Next Actions

- Test the safe repo executor manually from the operator console, including read, artifact, checker, and failure visibility paths
- Test the desktop bridge hand layer manually from the operator console, including focus, clipboard read/write, paste, hotkeys, mouse actions, waits, and the Ctrl+8 failsafe
- Test the workspace-boundary flow manually from the operator console
- Test the manual supervisor loop from the operator console, including review, resume, re-queue, repo executor actions, and desktop executor actions
- Define the first tiny multi-step operator recipe path for Codex-to-ChatGPT style handoff using focus, clipboard, paste, and wait primitives
- Design an explicit allowlist-expansion or workspace-override path later
- Choose the next narrow desktop-control addition, such as safe text insertion, known-target clicks, or recipe composition, only if it stays approval-aware
- Add a real notification channel later
- Expand the executor layer later only if each new action stays allowlisted, workspace-bound, and approval-aware
