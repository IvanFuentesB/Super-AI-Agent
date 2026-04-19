# Ghoti Active Mode — External Repo Audit & Integration Note

Generated: 2026-04-19

## Concept / Repo Audit Table

| Concept / Repo | Found in notes | Downloaded locally | Used in product code | Working | Verdict | Next step |
|---|---|---|---|---|---|---|
| Screen recording + voice input assistant | yes (chat_handoff_latest.md, current_state.md) | no | no | no | postponed | Install `sounddevice`+`vosk` or `whisper` for voice; continuous screen use `mss` for fast capture. Wire to active_mode_state.json. |
| Real-time phone / remote control | yes (chat_handoff_latest.md mentions OpenClaw remote-assistant) | no | no | no | postponed | Evaluate OpenClaw remote channel design. Requires auth layer first. |
| Claude Code / claw-code integration | yes | yes — `21_repos/third_party/claude-code-official`, `claw-code` in temp AI_Workspace | reference only | no | reference | Keep as reference. Do not add to product code yet. |
| OpenClaw / OpenArm | yes (current_state.md, decisions.md) | yes — `21_repos/third_party/openclaw` | reference only | no | reference | Major strategic reference for future control surface. Not a hard dep. |
| Yuchen robotic / math project | no | no | no | no | not found | No URL in notes. Track as open question if user provides link. |
| ROS / ROS2 | no | no | no | no | not found | No reference in notes. Out of scope for current MVP. |
| dora-rs / Dora robotics | no | no | no | no | not found | No reference in notes. Out of scope for current MVP. |
| browser-use | yes (current_state.md, decisions.md) | yes — `21_repos/third_party/browser-use` | no (capability truth exposed) | no — not installed | postponed | Install `browser-use` pip package when a real browser-role task path is ready. |
| Playwright | yes | yes — `21_repos/third_party/playwright-official` | yes — browser_playground | yes — Playwright binaries present | keep | Keep as deterministic browser fallback. Browser Use is the future target. |
| MCP server | yes | yes — `01_projects/mcp_server/server.py`, `03_scripts/run_mcp_server.ps1` | yes | partially | keep | Run via `powershell -File .\03_scripts\run_mcp_server.ps1` from repo root. |
| Gemma 4 / local brain / GRPO / unsloth | yes (current_state.md, preferences) | no model pulled yet | yes — `super_ai_agent.brain` wires Ollama | no — ollama list empty | postponed | Pull configured Gemma model into Ollama before claiming inference ready. |
| Kronos price prediction AI | yes (chat_handoff_latest.md mentions Kronos) | no | no | no | postponed | No URL found. Track as open question. |
| mirofish / mirror fish | yes (chat_handoff_latest.md mentions MiroFish) | no | no | no | postponed | No URL found. Track as open question. |
| elder plinius god mode | yes (chat_handoff_latest.md) | no | no | no | postponed | Referenced as inspiration only. No direct integration path yet. |
| multica | yes (chat_handoff_latest.md) | no | no | no | postponed | No URL found. Track as open question. |
| public API list repos | no specific ref | no | no | no | not found | No specific repo identified in notes. |
| memory export / memory tools | yes (compact_memory scaffolding) | no external tool | yes — `14_context/compact_memory/` | partially | keep | Compact memory files exist. No autonomous summarizer loop yet. |
| live video transform / face swap | no | no | no | no | not found | Out of scope for current MVP. |
| screen capture / screenshot | yes | PIL available (ImageGrab) | yes — NOW in active_mode_state + /api/ghoti/active/snapshot | yes — PIL.ImageGrab works on Windows | keep | Snapshot-only MVP implemented. Continuous capture deferred. |
| speech / voice / realtime audio | yes (concept) | no library installed | no | no | not ready | Need: `sounddevice`, `vosk` or `openai-whisper`. Wire push-to-talk placeholder in Active tab. Push-to-talk button exists as text fallback for now. |
| OpenHands / OpenInterpreter | yes (current_state.md) | yes — `21_repos/third_party/openhands`, `open-interpreter` | reference only | no | reference | Keep as reference. Too heavy to adopt directly. |
| windows-use / windows-mcp | yes | yes — `21_repos/third_party/windows-use`, `windows-mcp` | reference only | no | reference | Keep as reference for future Windows desktop control surface. |
| stagehand | yes (current_state.md) | yes — `21_repos/third_party/stagehand` | reference only | no | reference | Keep as reference for browser control. |
| n8n | yes (21_repos) | yes — `21_repos/third_party/n8n` | no | no | reference | Keep as reference for automation workflow design. |

## What is still missing for real screen-recording + voice realtime assistant

1. **Continuous screen capture**: PIL.ImageGrab is snapshot-only. For continuous/near-realtime use `mss` (fast multi-monitor) — `pip install mss`. Wire to a background thread that saves frames to a rolling buffer in the ignored screenshots dir.
2. **Real-time voice input**: No microphone library installed. Need `pip install sounddevice` + `pip install vosk` (offline) or `pip install openai-whisper` (local model). Push-to-talk placeholder in Active tab currently uses text fallback.
3. **Realtime display**: Dashboard polls every 6s. For near-realtime, use WebSocket or SSE from server.js. Node.js already has `http.createServer` so SSE is straightforward to add.
4. **Visual overlay on screen**: The Active Mode rail in the dashboard is browser-only. A true always-on overlay visible outside the browser requires a separate Windows Forms or Electron overlay process (similar to the existing desktop_playground cue — already partially implemented there).
5. **Audio indicator**: No audio feedback when active. Add a short OS sound on start/stop via PowerShell `[console]::beep()` or `media.SoundPlayer`.
6. **Remote / phone access**: Requires HTTPS, auth, and a reverse tunnel (e.g. ngrok or Cloudflare Tunnel) or VPN. Not implemented. Approval gating required before any remote access.

## Ghoti Active Mode MVP — what IS implemented now

- `active_mode_state.json` state machine in runtime_data
- GET /api/ghoti/active-state
- POST /api/ghoti/active/start
- POST /api/ghoti/active/stop
- POST /api/ghoti/active/snapshot (uses PIL.ImageGrab, saves to .tmp-screenshots/)
- POST /api/ghoti/active/message (text fallback instruction, approval-gated)
- "Active" tab in dashboard with status pill, Start/Stop/Snapshot/Message UI
- Persistent top-right "Ghoti idle / Ghoti active" rail badge visible across all tabs
- Privacy note and safety text in UI
- .gitignore covers screenshots and external repo clones
