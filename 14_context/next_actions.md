# Next Actions

- Manually test `codex_to_chatgpt_handoff_mvp` with real Codex and ChatGPT windows, not only terminal-safe checker targets
- Tighten target-window naming and matching so the handoff recipe can find the right Codex and ChatGPT windows deterministically without opening duplicate windows
- Keep paste-only as the default and only add an operator-reviewed send step if real target matching becomes reliable
- Improve operator-facing task-history filtering and recent views instead of adding any deletion path
- Keep the recipe library narrow, composable, approval-aware, and ready for later provider swapping
- Keep the operator stack separate from the brain/provider layer so future ChatGPT, Claude, Gemini, or Gemma routing does not force a core rewrite
- Test the safe repo executor manually from the operator console, including read, artifact, checker, and failure visibility paths
- Test the desktop bridge hand layer manually from the operator console, including focus, clipboard read/write, paste, hotkeys, mouse actions, waits, and the Ctrl+8 failsafe
- Test the workspace-boundary flow manually from the operator console
- Test the manual supervisor loop from the operator console, including review, resume, re-queue, repo executor actions, and desktop executor actions
- Manually test the new Ghoti state cue, resource guard warnings, retry ceiling, and interrupted-task messaging from the dashboard
- Add a narrow hardware-builder-assist experiment later only as a local-first research module, not as a Blueprint.am dependency
- Design an explicit allowlist-expansion or workspace-override path later
- Choose the next narrow desktop-control addition, such as safe text insertion or known-target clicks, only if it stays approval-aware
- Add a real notification channel later
- Expand the executor layer later only if each new action stays allowlisted, workspace-bound, and approval-aware
