# Ghoti Finish-Line Log

## Current session date
2026-04-19T17:00:00Z

## Current branch
feat/ghoti-visible-operator-stack

## Latest commits before this run
```
f27d998 Finish Active Mode per-session frame UI wiring and hardening
0a82e2a Fix Active Mode per-session capture cleanup isolation
88197c4 Add manual Active Session cleanup workflow
6186035 Add reviewed Active Session archive panel
2da7055 Add Ghoti active session timeline and gallery
403de95 Finalize Ghoti active capture preview
86c01b4 Add Ghoti continuous screen capture MVP
5fefa1d Verify Ghoti external repos and active mode truth
d8acc68 Add Ghoti active mode prototype
1b45d88 Refine Ghoti dashboard into professional tabbed prototype
bd3141c Add proper tab navigation to Ghoti operator console
672de70 Polish Ghoti operator console prototype
```

## Dirty working tree before this run
```
## feat/ghoti-visible-operator-stack...origin/feat/ghoti-visible-operator-stack [ahead 13]
 M 21_repos/third_party/.gitkeep   ← excluded from commits
?? 01_projects/mcp_server/test.txt  ← excluded from commits
```

## Honest product status
- Active Mode capture/gallery/archive/cleanup: **DONE** — per-session isolation, session_id-wired gallery, cleanup confirmed and validated
- Presence overlay: **BUILT THIS RUN** — `/overlay.html` + `overlay.js` + `overlay.css` at port 3210; shows active/capture/voice-placeholder; Start/Stop Ghoti, Start/Stop Watching, live frame thumb
- Voice input: **NOT BUILT** — `audio_enabled: false`; vosk-api and whisper are reference clones only; no microphone code
- Mute: **PLACEHOLDER ONLY** — overlay shows "Voice: Muted (not configured)"; no real audio state API
- Browser operator: **SCAFFOLDED BUT NOT FUNCTIONAL** — browser-use, playwright, stagehand cloned as reference; no real browser control code in `01_projects/`
- YouTube-following: **NOT BUILT** — no transcript extraction, no step execution
- Desktop operator: **PARTIAL** — PowerShell bridge, recipe runner, focus/hotkey actions exist; no AI-driven decision loop
- External repo integrations: **NONE** — all 37 cloned repos are reference-only
- GitHub push: **PENDING THIS RUN**

## External repo truth table

| Repo/concept | Present locally? | Actually used in product? | If used, where? | Next useful step |
|---|---|---|---|---|
| claw-code | Yes | No — reference only | — | Review agent loop architecture |
| openclaw | Yes | No — reference only | — | Review channels/remote-control design |
| browser-use | Yes | No — reference only | — | Review agent browser action patterns |
| browser-harness | Yes | No — reference only | — | Review CDP interface |
| browser-use-examples | Yes | No — reference only | — | Review example action patterns |
| browser-use-web-ui | Yes | No — reference only | — | Review web UI scaffolding |
| playwright | Yes | No — reference only | — | Evaluate for future test harness |
| playwright-official | Yes | No — reference only | — | Same as playwright |
| stagehand | Yes | No — reference only | — | Review AI browser actions |
| aider | Yes | No — reference only | — | Review diff/patch application |
| awesome-claude-code | Yes | No — reference only | — | Review ecosystem index |
| openarm | Yes | No — reference only | — | Review teleoperation interface |
| dora | Yes | No — reference only | — | Review dataflow node model |
| dora-hub | Yes | No — reference only | — | Review example nodes |
| python-mss | Yes | No — reference only | — | Evaluate for continuous frame capture |
| python-mss-examples | Yes | No — reference only | — | Review recording loop patterns |
| vosk-api | Yes | No — reference only | — | Evaluate for offline STT |
| whisper | Yes | No — reference only | — | Evaluate for STT integration |
| python-sounddevice | Yes | No — reference only | — | Evaluate for microphone input |
| unsloth | Yes | No — reference only | — | Review GRPO training patterns |
| Kronos | Yes | No — reference only | — | Review model architecture |
| Kronos-demo | Yes | No — reference only | — | Review demo inference |
| MiroFish | Yes | No — reference only | — | Review multi-agent simulation |
| mirofish-english | Yes | No — reference only | — | Review CLI interface |
| claw-code-android | Yes | No — reference only | — | Review mobile agent interface |
| open-computer-use | Yes | No — reference only | — | Review desktop computer-use patterns |
| open-interpreter | Yes | No — reference only | — | Review interpreter loop |
| openhands | Yes | No — reference only | — | Review agent task patterns |
| openhands-cli | Yes | No — reference only | — | Review CLI agent interface |
| logto | Yes | No — reference only | — | Review auth/identity patterns |
| n8n | Yes | No — reference only | — | Review workflow automation patterns |
| mcp-servers | Yes | No — reference only | — | Review MCP server patterns |
| windows-mcp | Yes | No — reference only | — | Review Windows MCP integration |
| windows-use | Yes | No — reference only | — | Review Windows computer-use patterns |
| career-ops | Yes | No — reference only | — | Personal reference |
| claude-code-official | Yes | No — reference only | — | Claude Code docs reference |
| cv-santiago | Yes | No — reference only | — | Personal reference |
| mithi/robotics-coursework | No — concept only | No | — | Robotics learning resources reference |

## Work chosen for this run
Built the Ghoti Presence Overlay MVP:
- `01_projects/dashboard_mvp/public/overlay.html` — compact dark-theme overlay page
- `01_projects/dashboard_mvp/public/overlay.js` — polls active-state + capture-state every 3s; Start/Stop Ghoti, Start/Stop Watching, live frame refresh
- `01_projects/dashboard_mvp/public/overlay.css` — compact dark theme matching Ghoti brand
- Added "⬡ Overlay" link in the active-mode rail in `index.html`
- Added `.ghoti-overlay-link` CSS in `styles.css`

## Files changed this run
- `01_projects/dashboard_mvp/public/overlay.html` (created)
- `01_projects/dashboard_mvp/public/overlay.js` (created)
- `01_projects/dashboard_mvp/public/overlay.css` (created)
- `01_projects/dashboard_mvp/public/index.html` (1 line added: overlay link in active rail)
- `01_projects/dashboard_mvp/public/styles.css` (14 lines added: `.ghoti-overlay-link` CSS)
- `14_context/ghoti_finish_line_log.md` (created this file)
- `14_context/external_repo_clone_registry.md` (no change needed; already current)

## Validation run
```
node --check server.js           → OK
node --check public/app.js       → OK
node --check public/overlay.js   → OK
GET /overlay.html                → HTTP 200
GET /overlay.js                  → HTTP 200
GET /overlay.css                 → HTTP 200
GET /api/ghoti/active-state      → ok:true, active:false
GET /api/ghoti/active/capture-state → ok:true, capturing:false
POST /api/ghoti/active/start     → ok:true, session_id present
POST /api/ghoti/active/capture/start → ok:true
(wait 3s) capture-state          → capturing:true, session_id present
POST /api/ghoti/active/capture/stop → ok:true
POST /api/ghoti/active/stop      → ok:true
```

## Final result
Overlay MVP built and serving at `http://127.0.0.1:3210/overlay.html`.
All APIs reachable. All syntax checks pass.
Browser visual verification not available from CLI — see honest note below.

## Next best step
Add voice mute state API (`GET/POST /api/ghoti/voice/state`) with muted/unmuted toggle,
update overlay to use real mute state, and add a mute button to the main dashboard Active tab.
This is the cheapest "real" step before tackling browser operator or YouTube-following.
