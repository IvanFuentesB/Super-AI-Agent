# Next Actions

- **N+3.9 re-verified (Claude lane, HEAD 9850c46)**: Docker daemon STILL NOT running; WSL STILL NOT installed; verdict unchanged: docker_installed_daemon_not_running + wsl_setup_required; all docs stable; 25 seeds unchanged; push of 9850c46 pending
- **N+3.9 delivered (Claude lane)**: Docker daemon verified NOT running; WSL2 NOT installed; verdict: docker_installed_daemon_not_running + wsl_setup_required; daemon verification doc + CUA image/source truth doc + CUA smoke exact plan created; wait/resume updated to 25 seeds — commit 6f95359 pushed (ff75f8e)
- **IMMEDIATE OPERATOR MANUAL ACTION REQUIRED** — launch Docker Desktop to start daemon and install WSL2:
  1. Open Start menu → search "Docker Desktop" → click to launch
  2. Accept any WSL2 install prompts that appear on first launch
  3. Wait for "Docker is running" green icon in system tray
  4. Reboot if prompted; then relaunch Docker Desktop
  5. After daemon running: verify in a **new** terminal:
     - `docker info` — must show Server section with daemon details
     - `wsl --status` — must confirm WSL2 installed
- **NEXT MILESTONE after daemon verified**: request separate CUA screenshot-only smoke approval (image digest must be pinned and approved before any pull; see `14_context/cua_screenshot_smoke_exact_plan_n3_9.md`)
- N+3.8 delivered (Claude lane): Docker Desktop 4.70.0 installed via winget; CLI verified (29.4.0); Compose verified (v5.1.2); install verification doc created; CUA smoke plan doc created; wait/resume updated to 23 seeds — commit 45335fa (push pending)
- N+3.7 delivered (Claude lane, PATH B): Screenpipe read-only dashboard status route added (`GET /api/ghoti/screenpipe/status`), Obsidian vault notes synced (00_Index, 01_Current_State, 04_Tools, 05_Safety_Gates), wait/resume updated to 21 seeds — commit eee0cc0 included in N+3.8 push
- N+3.6 delivered (Claude lane): Docker/CUA install gate doc, CUA Docker/Ubuntu sandbox path doc, execution decision record, status reconcile doc, wait/resume updated to 20 seeds, state docs updated

- N+3.3 delivered: CUA Driver readiness plan, OpenFang Rust candidate plan, Screenpipe retention plan + policy JSON + cleanup script, Obsidian local vault (00_Index, 01_Current_State, 04_Tools, 05_Safety_Gates), wait/resume updated to 12 gates
- Push N+3.3 commit to origin after operator confirms (push command: `git push origin feat/ghoti-visible-operator-stack`)
- Operator approval required before: Gemma pull, AutoBrowser wiring, TryCUA eval, OpenFang clone, Screenpipe capture start, any external adapter execution
- Start using vault notes at `14_context/obsidian_vault/` in future prompts to reduce token usage — reference vault note + file path instead of re-pasting context
- Decide first candidate from tool_intake_new_candidates_n3_2.md to evaluate next (AnythingLLM or Open WebUI are lowest-risk local-UI options)
- N+3.2 delivered: wait/resume supervisor, dashboard wait-resume read route, LOC report, computer-use/CUA strategy update, token-saving update, tool intake for new candidates, Gemma diagnostic, Obscura recovery commit (87357f1)
- Review wait/resume queue: run `python 01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py` to see active gates and resume commands

- N+3.1 delivered: ActionIntent contracts, CapabilityAdapterDescriptor, approval-bound gating demo, JSONL audit trail, dashboard read route, computer-use strategy note, and token-saving workflow update
- Validate N+3.1 demo output: run `python 01_projects/runtime_mvp/src/super_ai_agent/action_demo.py` and check `05_logs/action_audit.jsonl` and `05_logs/action_intent_runs/<latest>/action_intent_demo_summary.md`
- Evaluate AutoBrowser as the first external browser adapter: create a CapabilityAdapterDescriptor, design the ActionIntent approval flow, and propose in a separate milestone with explicit user approval
- Connect the approval inbox to the ActionIntent flow in a future milestone so the dashboard shows pending action intents under the approval queue
- Use the visible Ghoti operator stack in dashboard and CLI for the next manual operator-validation pass instead of adding new surface area
- Use the new desktop action cue, target marker, and desktop-action truth as the default operator view during real desktop validation
- Manually validate visible mouse aiming, clicking, waiting, and controlled one-line typing with the new overlay cue before adding broader desktop behaviors
- Confirm that `type_text` stays narrow: explicit allowlisted target only, no freeform broad typing, and no auto-submit unless a later recipe explicitly opts in
- Pull the configured Gemma model into Ollama and rerun `python -m super_ai_agent.cli brain-status` until `brain_inference_ready: yes` is true
- Run `python 01_projects/runtime_mvp/src/super_ai_agent/multi_agent_mvp.py` when a visible local multi-agent coordination demo is needed
- Build one tiny local-only `CapabilityAdapter` implementation that can consume an approved `ActionIntent` and produce a harmless repo-local artifact; keep AutoBrowser, RUFLO, Obscura, Browser Use, and all external operator candidates disabled
- Keep multi-agent shared memory compact and file-backed; cite run artifacts instead of pasting large summaries into prompts
- Choose one narrow approval-aware task path later that should explicitly call the local brain so `current_task_used_model_inference` can become true for real work instead of remaining a dashboard-only truth field
- Keep the provider/model layer swappable so Gemma local can be the default local brain without locking the operator core to a single vendor or model
- Keep the floating overlay, target marker, and Operator Watchdog visible during manual desktop and handoff validation so wrong-window blocks and stalled work are obvious immediately
- Manually re-test `codex_to_chatgpt_handoff_mvp` with real Codex and ChatGPT windows using the new candidate picker and remembered candidate toggle
- Validate that a foreground terminal or other wrong active window blocks the handoff before any paste or send step
- Validate that explicit terminal-targeted actions still behave honestly as terminal actions when the operator intentionally targets a terminal
- Validate that the browser-local remembered Codex and ChatGPT candidate selections restore only exact visible windows and clear stale picks safely
- Walk through the dashboard control center, floating overlay, Operator Watchdog, and `ghoti-*` CLI commands as the default first operator view for approvals, active work, failures, and artifacts
- Keep 04_docs\ghoti_control_center.md aligned with the real launch path, stop path, and operator workflow
- Improve operator-facing task filtering and recent views further only if it reduces noise without adding any deletion path
- Add a clean usage-exhaustion or handoff-point note later only if it helps the operator decide when to refresh context without widening autonomy
- Decide later whether anything broader than the browser-local remembered candidate option is justified so the operator does not need to re-pick the same windows every run
- Tighten Codex and ChatGPT target resolution further only if it reduces manual picks without widening into unsafe guessing
- Add a small operator-confirmed handoff review step later only if it improves safety without reintroducing terminal or shell fallback
- Keep repeated identical blocked handoff payloads from being re-run beyond the current two-attempt ceiling
- Keep paste-only as the default and only add an operator-reviewed send step if real target matching becomes reliable
- Keep no-task-deletion as an explicit policy and use filter/archive/history instead
- Keep the recipe library narrow, composable, approval-aware, and ready for later provider swapping
- Keep the operator stack separate from the brain/provider layer so future ChatGPT, Claude, Gemini, or Gemma routing does not force a core rewrite
- Capture the OpenClaw patterns that are most useful for later channel, browser-assist, and long-running operator evolution without introducing a hard dependency
- Capture the OpenClaw patterns that matter most for later brain-routing, channel, and control-surface evolution without replacing the current local operator core
- Test the safe repo executor manually from the operator console, including read, artifact, checker, and failure visibility paths
- Test the desktop bridge hand layer manually from the operator console, including focus, clipboard read/write, paste, hotkeys, mouse actions, waits, and the Ctrl+8 failsafe
- Test the workspace-boundary flow manually from the operator console
- Test the manual supervisor loop from the operator console, including review, resume, re-queue, repo executor actions, and desktop executor actions
- Manually test the new Ghoti state cue, control center summaries, resource guard warnings, retry ceiling, and interrupted-task messaging from the dashboard
- Add a narrow hardware-builder-assist experiment later only as a local-first research module, not as a Blueprint.am dependency
- Design an explicit allowlist-expansion or workspace-override path later
- Choose the next narrow desktop-control addition only if it stays approval-aware and builds directly on the visible cue and target-marker layer
- Use the new specialist-role registry and browser-capability truth only as operator-visible scaffolding until a real router or browser-session executor is justified
- Install Browser Use later and validate it honestly before describing any browser-agent path as live
- Keep Playwright as the deterministic browser-control fallback until Browser Use is truly ready
- Start using the new compact memory files under `14_context\compact_memory` to compress future thread handoffs instead of repeating giant summaries
- Keep the business-outreach review scaffold planning-only until identification, drafting, review, and approval checkpoints are each explicit
- Add a real notification channel later
- Expand the executor layer later only if each new action stays allowlisted, workspace-bound, and approval-aware
- N+3.5 delivered: CUA exact source verified (ls-remote HEAD 46dbcb47), shallow clone at 21_repos/third_party/evals/cua, isolated clone audit doc, sandbox profile validated, descriptor confirmed, wait/resume updated (17 seeds), state docs updated
- CUA all local paths currently blocked on Windows 11 Home: Lume=macOS-only, Cua Driver=macOS-only, Windows Sandbox=Pro/Enterprise required, Docker=not installed, WSL=not installed
- Request operator approval to install Docker Desktop — this is the lowest-risk path to unlock CUA Docker/Ubuntu containers and AutoBrowser on Windows 11 Home
- Once Docker Desktop approved and installed: evaluate `21_repos/third_party/evals/cua/libs/qemu-docker/linux` for Ubuntu container CUA agent
- Once Docker Desktop approved and installed: evaluate AutoBrowser Docker Compose run as supervised browser milestone
- Request operator approval to enable the CUA sandbox profile before any CUA driver evaluation begins; review `23_configs/cua_sandbox_profile.example.json` first
- Run first screenshot-only CUA sandbox smoke test against local test page only, with ActionIntent approval gate, after Docker Desktop install and operator approves sandbox profile
- CUA descriptor in action_intent.py is confirmed as descriptor_only / can_execute=false — no changes needed until Docker path is unlocked
