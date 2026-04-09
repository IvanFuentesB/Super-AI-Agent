# Chat Handoff Latest

## 1. Project Purpose
- Build Ghoti: a local-first supervised Windows operator for legitimate business, documentation, research, owned-account workflows, and later browser/app control.
- Keep execution explicit, approval-gated, workspace-bound, resumable, inspectable, and easy to hand off when chats get long.
- Long term, support a model council or router across ChatGPT, Claude, Gemini, Gemma local, and later others.

## 2. Current Repo Root And Boundary Rules
- Canonical repo and workspace root:
  `C:\Users\ai_sandbox\Documents\AI_Managed_Only`
- Do not touch files outside that root unless the user explicitly approves it.
- Out-of-scope paths must stay blocked or escalated, never treated as normal work.
- Do not affect the other Windows profile.

## 3. Completed Feature Branches In Order
- `feat/supervisor-and-approval-inbox`
- `feat/approval-queue-ui`
- `feat/workspace-boundaries`
- `feat/manual-supervisor-loop`
- `feat/safe-repo-executor`
- `feat/desktop-bridge-actions`
- `feat/desktop-input-mouse-failsafe`
- `feat/operator-recipes-handoff-memory`
- `feat/ghoti-visual-cue-resource-guard` (current working branch)

## 4. Current Working Capabilities
- Approval queue UI with approve, deny, and defer.
- Workspace-bound task classification and blocking.
- Manual supervisor loop with waiting, review, resume, re-queue, and task history.
- Safe repo-local executor for allowlisted file, git, artifact, and checker actions.
- Local dashboard operator console with artifact preview, open, reveal, and supervisor views.
- Browser playground with headless smoke and visible local demo.
- Narrow desktop bridge with window, clipboard, hotkey, wait, screenshot, and mouse actions.
- Narrow operator recipes built from the desktop hand primitives.
- Ghoti state cue in the dashboard for `idle`, `active`, `waiting`, `approval_needed`, `interrupted`, and `resource_guard_triggered`.
- Resource/process guard for duplicate terminal/process pressure.
- Two-attempt retry ceiling for desktop actions and recipe steps.
- Clipboard guard that blocks obvious checker or recipe labels from being pasted into terminals.
- Compact handoff memory and repo-integration mapping inside `14_context` and `08_research`.

## 5. Current Safety Model
- Risky actions require approval.
- The workspace root is the default hard boundary.
- Out-of-scope targets stay blocked by workspace policy even if approval is recorded.
- No arbitrary shell passthrough.
- No admin automation.
- No silent daemon or hidden autonomy.
- Desktop recipes stay explicit, allowlisted, approval-aware, and stop on `Ctrl+8`.
- Focus-sensitive desktop actions stop safely when Windows cannot grant or confirm foreground control.

## 6. Current Desktop-Control Capabilities
- `list_windows`
- `get_active_window`
- `focus_window`
- `open_allowed_app`
- `capture_desktop_screenshot`
- `get_clipboard_text`
- `set_clipboard_text`
- `copy_selection`
- `paste_clipboard`
- allowlisted hotkeys: `ctrl+c`, `ctrl+v`, `ctrl+l`, `enter`, `escape`
- `wait_seconds`
- `wait_for_window`
- `move_mouse`
- `left_click`
- `double_click`
- `right_click`
- `scroll_mouse`
- narrow operator recipes:
  - `observe_desktop_state`
  - `focus_or_reuse_terminal`
  - `copy_from_focused_window`
  - `paste_into_target_window`
  - `wait_and_resume_operator_step`
  - `codex_to_dashboard_progress_handoff`
- `Ctrl+8` interrupt path that persists an interrupted state and requires operator review before re-queueing

## 7. Known Weird Behaviors / Current Issues
- The chat context fills quickly, so the handoff files matter.
- In this current checker session, some focus-sensitive desktop actions can hit `manual_focus_required` because Windows foreground access is not always available to the spawned process.
- In this current checker session, desktop screenshot capture can hit `desktop_capture_unavailable`, so manual capture is still needed there.
- PowerShell or Node windows can still appear during checks or desktop actions; focus-first reuse now exists, but clutter is still a concern.
- The desktop bridge and recipe layer are still narrow and deterministic, not a full UI-state-aware desktop controller.
- `codex_to_dashboard_progress_handoff` is only a narrow prototype. It is not a real ChatGPT-specific workflow yet.
- Runtime data contains a lot of persisted checker-created tasks.

## 8. Repo Integration Map Summary
- Core now:
  this repo itself, runtime MVP, dashboard MVP, browser playground, desktop playground, supervisor flow, approval flow, workspace policy, allowlisted executor, and narrow operator recipes.
- DNA/reference:
  Codex, Claude Code, OpenClaw, official Playwright, Windows-Use, Windows-MCP, Open Interpreter, Open Computer Use, browser-use, Stagehand, and Blueprint.am as product inspiration only.
- Later experiment:
  OpenHands or OpenHarness style systems, Claw Code, Kronos, MiroFish, and future local model routing and eval layers.
- Use-only / optional utility:
  career-ops, pi-mono, seomachine, thepopebot, RedditVideoMakerBot, awesome-claude-code, and side demo/design helpers.
- Not foundation:
  leak-style extraction repos, abuse-oriented automation, and unrelated side tools.

## 9. Immediate Next Recommended Branch
- `feat/practical-codex-chatgpt-handoff-loop`
- Purpose:
  build the first serious cross-window handoff recipe on top of the new Ghoti cue, retry policy, resource guard, and failsafe. Start narrow:
  focus source window, copy safe progress text, verify clipboard, focus target window, paste, wait, and stop safely if context is unclear.

## 10. What Still Does NOT Exist Yet
- No full browser executor loop.
- No full Windows app or desktop executor.
- No unrestricted typing, drag-and-drop, or free-roaming desktop automation.
- No real ChatGPT-specific target window matching or durable Codex-to-ChatGPT workflow yet.
- No tray app, always-on-top standalone cue window, or external notification channel yet.
- No live Notion integration.
- No live mail or LinkedIn execution adapters.
- No multi-model routing or council execution layer yet.
- No strong skip-policy layer beyond the current retry ceiling and manual review flow.

## 11. 14_context Files To Read First In A New Thread
- `14_context/chat_handoff_latest.md`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/decisions.md`
- `14_context/status_board.md`
- `14_context/open_questions.md`
- `14_context/recent_failures.md`
