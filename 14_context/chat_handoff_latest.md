# Chat Handoff Latest

## 1. Project Purpose
- Build a local-first Windows AI operator for legitimate business, documentation, research, owned-account workflows, and later browser/app control.
- Keep execution explicit, approval-gated, workspace-bound, inspectable, resumable, and easy to hand off when chats get long.
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

## 4. Current Working Capabilities
- Approval queue UI with approve, deny, and defer.
- Workspace-bound task classification and blocking.
- Manual supervisor loop with waiting, review, resume, re-queue, and task history.
- Safe repo-local executor for allowlisted file, git, artifact, and checker actions.
- Local dashboard operator console with artifact preview, open, and reveal.
- Browser playground with headless smoke and visible local demo.
- Narrow desktop bridge with persisted window, clipboard, hotkey, wait, screenshot, and mouse action results.
- Narrow operator recipes built from the existing desktop hand primitives.

## 5. Current Safety Model
- Risky actions require approval.
- The workspace root is the default hard boundary.
- Out-of-scope targets stay blocked by workspace policy even if approval is recorded.
- No arbitrary shell passthrough.
- No admin automation.
- No silent daemon or hidden autonomy.
- Desktop recipes stay explicit, allowlisted, approval-aware, and stop on `Ctrl+8`.

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
- The chat context fills quickly, so handoff files matter.
- Sometimes PowerShell or Node windows can still appear during checks or desktop actions; focus-first reuse has improved this, but clutter is still a concern.
- The desktop bridge and recipe layer are narrow and deterministic, not a full UI-state-aware desktop controller.
- `codex_to_dashboard_progress_handoff` is only a narrow prototype. It is not a real ChatGPT-specific workflow yet.
- The repo has a lot of persisted checker-created tasks in runtime data.

## 8. Repo Integration Map
- Core now:
  this repo itself, runtime MVP, dashboard MVP, browser playground, desktop playground, durable context files, supervisor flow, allowlisted executors, and the recipe layer.
- DNA/reference:
  Claude Code official, Codex operating patterns, OpenClaw, official Playwright, Windows-Use, Windows-MCP, Open Interpreter, Open Computer Use, browser-use, and Stagehand.
- Later experiment:
  OpenHands or OpenHarness style systems, Claw Code, Kronos, MiroFish, Blueprint.am or Blueprint, future local model routing and eval layers.
- Use-only / optional utility:
  career-ops, pi-mono, seomachine, thepopebot, RedditVideoMakerBot, awesome-claude-code, side demo tools, and design helpers.
- Not foundation:
  leak-style extraction repos, unrelated side tools, and anything that pushes the system toward spam, fake autonomy, or platform abuse.

## 9. Immediate Next Recommended Branch
- `feat/cross-window-handoff-recipes`
- Purpose:
  tighten real window targeting, clipboard confirmation, and wait/resume around a true Codex-to-ChatGPT style handoff without pretending full desktop autonomy exists.

## 10. What Still Does NOT Exist Yet
- No full browser executor loop.
- No full Windows app or desktop executor.
- No unrestricted typing, drag-and-drop, or free-roaming desktop automation.
- No true Codex-to-ChatGPT workflow with reliable real target-window matching yet.
- No real external notifications.
- No live Notion integration.
- No live mail or LinkedIn execution adapters.
- No multi-model routing or council execution layer yet.

## 11. 14_context Files To Read First In A New Thread
- `14_context/chat_handoff_latest.md`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/decisions.md`
- `14_context/status_board.md`
- `14_context/open_questions.md`
- `14_context/recent_failures.md`
