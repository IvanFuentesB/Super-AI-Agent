# Chat Handoff Latest

## 1. Project Purpose
- Build Ghoti: a supervised, local-first Windows operator that can help think, plan, build, document, and perform narrow approved actions on the machine.
- Keep the operator stack separate from the brain/provider layer so ChatGPT, Claude, Gemini, Gemma local, or later models can be swapped without rewriting approvals, memory, recipes, dashboard, or integrations.
- Stay practical: explicit actions, visible state, approval gates, compact durable memory, and clean handoff when chats get long.

## 2. Repo Root And Boundary Rules
- Canonical workspace root:
  `C:\Users\ai_sandbox\Documents\AI_Managed_Only`
- Do not touch files or areas outside that root unless the user explicitly approves it.
- Do not affect the other Windows profile.
- Out-of-scope paths must stay blocked or escalated, never treated as normal work.
- No task should be deleted without the user's explicit approval.
- Prefer archive, filter, and history visibility instead of deletion.

## 3. Completed Feature Branches In Order
- `feat/supervisor-and-approval-inbox`
- `feat/approval-queue-ui`
- `feat/workspace-boundaries`
- `feat/manual-supervisor-loop`
- `feat/safe-repo-executor`
- `feat/desktop-bridge-actions`
- `feat/desktop-input-mouse-failsafe`
- `feat/operator-recipes-handoff-memory`
- `feat/ghoti-visual-cue-resource-guard`
- `feat/codex-chatgpt-handoff-mvp`
- current hardening branch:
  `fix/codex-handoff-no-terminal-fallback`

## 4. Current Working Capabilities
- Approval queue UI with approve, deny, and defer.
- Workspace-bound task classification and policy blocking.
- Manual supervisor loop with waiting, review, resume, re-queue, interruption, and task history.
- Safe repo-local executor for allowlisted file, git, artifact, checker, and recipe actions.
- Dashboard operator console with artifact preview/open/reveal, supervisor views, desktop bridge status, and recent actions.
- Browser playground with headless smoke and visible local demo.
- Narrow desktop bridge with window, clipboard, hotkey, wait, screenshot, and mouse actions.
- Ghoti dashboard state cue for `idle`, `active`, `waiting`, `approval_needed`, `interrupted`, and `resource_guard_triggered`.
- Resource/process guard for duplicate terminal and process pressure.
- Two-attempt retry ceiling for desktop actions and recipe steps.
- Clipboard guard that blocks checker or recipe junk before it reaches terminal or handoff targets.
- First reusable operator recipe layer.
- First narrow supervised Codex-to-ChatGPT handoff MVP recipe.
- Operator-facing task filtering for noisy task history:
  recent-only and visibility filters are now present in the dashboard.

## 5. Current Safety Model
- Risky actions require approval.
- Workspace root is the hard default boundary.
- Out-of-scope targets stay blocked even if approval is recorded.
- No arbitrary shell passthrough.
- No admin automation.
- No unrestricted desktop control.
- No silent daemon or hidden autonomy.
- Desktop actions and recipes stay explicit, allowlisted, approval-aware, and stop on `Ctrl+8`.
- Handoff defaults to paste-only. Auto-send is blocked unless the recipe explicitly allows it.
- Codex-to-ChatGPT handoff must not fall back to terminal or PowerShell targets.
- If the intended source or target window cannot be resolved confidently, block safely instead of pasting anywhere.
- If the same action or payload fails 2 times, stop retrying it and clearly report the problem.
- No task should be deleted without the user's explicit approval; prefer archive, filter, and history visibility instead.

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
- `Ctrl+8` interrupt path with persisted interrupted state

## 7. Current Handoff MVP
- New recipe:
  `codex_to_chatgpt_handoff_mvp`
- Current behavior:
  focus source window, copy or reuse prepared clipboard text, classify clipboard payload, focus target window, paste safely, optionally wait, optionally allow explicit send.
- Current defaults:
  source `codex`, target `chatgpt`, paste-only by default, no auto-Enter.
- Current narrow safe target aliases for this recipe:
  `codex` as source and `chatgpt` as target only.
- Current proven behavior:
  junk or internal label payloads are blocked before paste,
  valid handoff payloads can pass,
  explicit send remains opt-in.
- Current hardening result:
  terminal or PowerShell fallback is rejected for this recipe,
  unresolved targets now stop with manual target resolution required,
  and repeated identical blocked payloads are counted and reported instead of looping.

## 8. Known Weird Behaviors / Current Issues
- Chat context still fills quickly, so the handoff files matter.
- Window matching still depends on visible titles and narrow aliases, so real Codex/ChatGPT targeting is still somewhat brittle.
- The terminal-fallback bug is now blocked in the recipe path, but real Codex and ChatGPT window matching can still stop at manual target resolution if the title match is unclear.
- Terminal or PowerShell must not be used as a fallback target for Codex-to-ChatGPT handoff, and the current recipe now enforces that.
- Some focus-sensitive desktop actions can still hit `manual_focus_required` depending on the Windows session.
- Desktop screenshot capture can still hit `desktop_capture_unavailable` in some sessions.
- PowerShell or Node windows can still appear during some checks or desktop actions, although focus-first reuse and resource guards reduce this.
- Task history is large and noisy even with the new filters; operator-facing filtering still needs another pass.
- Older failed checker tasks still exist and should not be over-weighted without checking the latest checker results.

## 9. Repo Integration Map Summary
- Core now:
  this repo, runtime MVP, dashboard MVP, browser playground, desktop playground, supervisor flow, approval flow, workspace policy, allowlisted executor, and narrow operator recipes.
- DNA/reference:
  Codex, Claude Code, OpenClaw, official Playwright, Windows-Use, Windows-MCP, Open Interpreter, Open Computer Use, browser-use, Stagehand, and Blueprint.am as product inspiration only.
- Later experiment:
  OpenHands or OpenHarness style systems, Claw Code, Kronos, MiroFish, and future local model routing and eval layers.
- Use-only / optional utility:
  career-ops, pi-mono, seomachine, thepopebot, RedditVideoMakerBot, and side helper repos.
- Not foundation:
  leak-style extraction repos, abuse-oriented automation, and unrelated side tools.

## 10. Exact Next Recommended Step
- Manually test `codex_to_chatgpt_handoff_mvp` with real Codex and ChatGPT windows, now that terminal fallback is blocked and repeated junk payload retries are capped safely.
- After that, tighten real Codex and ChatGPT target matching without introducing any terminal or shell substitute path.

## 11. What Still Does NOT Exist Yet
- No durable real ChatGPT-specific target resolver.
- No unrestricted desktop control, freeform typing, drag-and-drop, or free-roaming automation.
- No full browser executor loop.
- No full Windows app executor.
- No external notifications or remote replies.
- No live Notion, mail-send, or LinkedIn execution adapters.
- No multi-model council/router execution layer yet.
- No task deletion flow, and none should be added without explicit user approval.

## 12. Current Practical Conclusions
- Terminal junk or label payloads can now be blocked safely.
- Valid paste and allowlisted hotkey actions can succeed.
- The first narrow supervised Codex-to-ChatGPT handoff workflow now blocks terminal fallback by design and remains paste-only by default.
- Repeated identical blocked handoff payloads now stop after the second explicit operator-approved retry path instead of looping.
- Task history is large and noisy and needs better operator-facing filtering rather than deletion.

## 13. 14_context Files To Read First In A New Thread
- `14_context/chat_handoff_latest.md`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/decisions.md`
- `14_context/status_board.md`
- `14_context/open_questions.md`
- `14_context/recent_failures.md`
