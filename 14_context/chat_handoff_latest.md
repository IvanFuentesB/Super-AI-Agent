# Chat Handoff Latest

## 1. Project Purpose
- Build Ghoti: a supervised, local-first Windows operator that can help think, plan, build, document, and perform narrow approved actions on the machine.
- Keep the operator stack separate from the brain/provider layer so ChatGPT, Claude, Gemini, Gemma local, or later models can be swapped without rewriting approvals, memory, recipes, dashboard, or integrations.
- Keep the operator stack compatible with later OpenClaw-style channel, browser-assisted, messaging, and long-running operator components without turning OpenClaw into a hard dependency now.
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
- `fix/codex-handoff-no-terminal-fallback`
- `feat/real-window-handoff-targeting`
- `feat/ghoti-control-center`
- current branch:
  `feat/ghoti-visible-operator-stack`

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
- Real-window handoff target discovery now exists for Codex and ChatGPT candidate windows.
- Manual target resolution now exists in the dashboard for the current handoff run through explicit candidate selection.
- The dashboard can now optionally remember selected visible Codex and ChatGPT candidate IDs locally in the browser and clear stale remembered picks when the exact windows disappear.
- Handoff detail now shows matched source and destination windows, whether selection was automatic or manual, and why matching failed when it stops safely.
- Codex-to-ChatGPT handoff now re-verifies the active destination immediately before paste or send and blocks safely if the foreground window does not still match the intended explicit Codex or ChatGPT target.
- Operator-facing task filtering for noisy task history:
  recent-only and visibility filters are now present in the dashboard.
- A top-level Ghoti control center now exists in the dashboard with live state, hotkey visibility, current task, pending approvals, blocked tasks, recent actionable work, recent failures, quick actions, capabilities, artifacts, and next-step guidance.
- CLI operator visibility now exists through `ghoti-help`, `ghoti-status`, `ghoti-hotkeys`, and `ghoti-recent`.
- A real local brain/provider foundation now exists through `super_ai_agent.brain`, with `gemma_local` as the default local-first provider target and Ollama as the live local call path when the configured Gemma model is installed.
- Dashboard and CLI now expose active brain provider, active model, current-task model-use truth, and last model-call status so the operator can see whether Ghoti is actually using Gemma or only local rules.
- A compact operator usage doc now exists at `04_docs/ghoti_control_center.md`.
- A lightweight floating Ghoti overlay now exists in the dashboard with live state, watchdog summary, Ctrl+8 reminder, and current target visibility.
- A visible target marker now exists for the current local focus, pointer, handoff, or input destination summary.
- An Operator Watchdog summary now exists in both dashboard and CLI so wrong-window blocks, stalled work, did-not-complete work, and manual-intervention pressure are easier to spot.
- The desktop bridge now shows a lightweight live action cue for aiming, clicking, typing, and waiting, including the target description and Ctrl+8 stop reminder.
- Controlled one-line `type_text` now exists for explicit allowlisted desktop targets, and dashboard plus CLI surfaces now expose whether typing is enabled for the current or last desktop action.

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
- If the active window changes unexpectedly or does not still match the intended Codex or ChatGPT destination at execution time, block safely before input.
- Explicit terminal-targeted actions remain valid when the operator intentionally targets a terminal; the no-terminal rule applies to Codex-to-ChatGPT handoff destinations.
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
- `type_text`
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
  wrong-active-window execution now stops before any paste or send step,
  and repeated identical blocked payloads are counted and reported instead of looping.
- Current targeting result:
  the dashboard can list real Codex and ChatGPT window candidates,
  ambiguous ChatGPT matches now block safely,
  the operator can choose a specific candidate for the current run when needed,
  and the dashboard can optionally remember those exact candidate IDs locally for later runs.

## 8. Known Weird Behaviors / Current Issues
- Chat context still fills quickly, so the handoff files matter.
- Window matching still depends on visible titles and narrow aliases, so real Codex/ChatGPT targeting is improved but still somewhat brittle.
- The wrong-destination input bug is now blocked in the recipe path, so a foreground terminal or other mismatched window should stop the handoff before input.
- Terminal or PowerShell must not be used as a fallback target for Codex-to-ChatGPT handoff, although explicit terminal-targeted actions elsewhere are still allowed.
- Honest current brain truth: Gemma is now wired as the default local brain path, but `ollama list` is currently empty in this environment and no broad operator task path automatically uses model inference yet.
- Some focus-sensitive desktop actions can still hit `manual_focus_required` depending on the Windows session.
- Desktop screenshot capture can still hit `desktop_capture_unavailable` in some sessions.
- PowerShell or Node windows can still appear during some checks or desktop actions, although focus-first reuse and resource guards reduce this.
- Task history is still large, but the new control center and filters make the current work much easier to spot than the older raw task lists alone.
- Remembered candidate selection now exists only as an opt-in browser-local dashboard preference; there is still no broader runtime-stored durable target profile.
- Older failed checker tasks still exist and should not be over-weighted without checking the latest checker results.

## 9. Repo Integration Map Summary
- Core now:
  this repo, runtime MVP, dashboard MVP, browser playground, desktop playground, supervisor flow, approval flow, workspace policy, allowlisted executor, and narrow operator recipes.
- DNA/reference:
  Codex, Claude Code, OpenClaw, official Playwright, Windows-Use, Windows-MCP, Open Interpreter, Open Computer Use, browser-use, Stagehand, and Blueprint.am as product inspiration, with OpenClaw now treated as a major strategic reference for future control-surface and remote-assistant design.
- Later experiment:
  OpenHands or OpenHarness style systems, Claw Code, Kronos, MiroFish, and future local model routing and eval layers.
- Use-only / optional utility:
  career-ops, pi-mono, seomachine, thepopebot, RedditVideoMakerBot, and side helper repos.
- Not foundation:
  leak-style extraction repos, abuse-oriented automation, and unrelated side tools.

## 10. Exact Next Recommended Step
- Use the new dashboard control center and `ghoti-*` CLI commands for the next manual operator-validation pass.
- Re-test real Codex-to-ChatGPT handoff with the candidate picker and remembered candidate toggle, confirm wrong-active-window blocking again in live use, and confirm explicit terminal-targeted actions still behave honestly when intentionally chosen.
- Keep the current handoff safety, workspace boundary, approval model, Ctrl+8 failsafe, and no-delete policy intact while validating the clearer operator surface.

## 11. What Still Does NOT Exist Yet
- No runtime-stored durable Codex or ChatGPT target profile beyond the browser-local remembered candidate toggle.
- No unrestricted desktop control, freeform broad typing, drag-and-drop, or free-roaming automation.
- No full browser executor loop.
- No full Windows app executor.
- No external notifications or remote replies.
- No live Notion, mail-send, or LinkedIn execution adapters.
- No multi-model council/router execution layer yet.
- No broad task-routing layer yet that automatically sends operator work through the local Gemma brain.
- No task deletion flow, and none should be added without explicit user approval.

## 12. Current Practical Conclusions
- Terminal junk or label payloads can now be blocked safely.
- Valid paste and allowlisted hotkey actions can succeed.
- The first narrow supervised Codex-to-ChatGPT handoff workflow now blocks terminal fallback by design and remains paste-only by default.
- Repeated identical blocked handoff payloads now stop after the second explicit operator-approved retry path instead of looping.
- Real-window targeting is now strong enough to list Codex and ChatGPT candidates and require explicit manual choice when matching is ambiguous.
- Browser-local remembered candidate selection now exists and restores only exact visible candidate IDs.
- Runtime, dashboard, and desktop checkers now cover the real-window targeting path honestly, including the wrong-active-window block before input.
- The dashboard and CLI now provide a real operator-facing Ghoti control center, so current state, hotkeys, actionable work, failures, and recent artifacts are much easier to inspect.
- The visible overlay, target marker, and watchdog summary now make Ghoti feel much more present during real operator use without adding hidden autonomy.
- The new desktop action cue, target marker, and desktop-action truth make aiming, clicking, waiting, and controlled typing visible to the operator instead of hidden in raw task logs.
- Explicit terminal-targeted actions still remain possible for terminal recipes or actions outside the Codex-to-ChatGPT handoff path.
- Task history is still large, so further cleanup should continue to prefer filtering, recent views, and history visibility rather than deletion.

## 13. 14_context Files To Read First In A New Thread
- `14_context/chat_handoff_latest.md`
- `14_context/current_state.md`
- `14_context/next_actions.md`
- `14_context/decisions.md`
- `14_context/status_board.md`
- `14_context/open_questions.md`
- `14_context/recent_failures.md`
