# External Repo Clone Registry

**Timestamp:** 2026-04-19T00:00:00Z  
**Clone root:** `C:\Users\ai_sandbox\Documents\AI_Managed_Only\21_repos\third_party`

## Clone Table

| Name | URL | Local Path | Status | Commit | Reason | Used in Product Now | Next Integration Step |
|------|-----|-----------|--------|--------|--------|--------------------|-----------------------|
| claw-code | https://github.com/ultraworkers/claw-code.git | 21_repos/third_party/claw-code | cloned | 00d0eb6 | Claude Code/coding-agent architecture reference | No — reference only | Review agent loop architecture |
| openclaw | https://github.com/openclaw/openclaw.git | 21_repos/third_party/openclaw | updated_existing | e9befcff | personal assistant, channels, remote-control reference | No — reference only | Review channels/remote-control design |
| browser-use | https://github.com/browser-use/browser-use.git | 21_repos/third_party/browser-use | updated_existing | 55ca9cb | AI browser-control reference | No — reference only | Review agent browser action patterns |
| browser-harness | https://github.com/browser-use/browser-harness.git | 21_repos/third_party/browser-harness | cloned | 4ec6255 | thin CDP/browser harness reference | No — reference only | Review CDP interface |
| playwright | https://github.com/microsoft/playwright.git | 21_repos/third_party/playwright | cloned | b86038b | browser automation/testing reference | No — reference only | Evaluate for future test harness |
| aider | https://github.com/Aider-AI/aider.git | 21_repos/third_party/aider | updated_existing | bdb4d9f | AI coding-assistant reference | No — reference only | Review diff/patch application patterns |
| awesome-claude-code | https://github.com/hesreallyhim/awesome-claude-code.git | 21_repos/third_party/awesome-claude-code | updated_existing | 829a545 | Claude Code ecosystem index | No — reference only | Review listed tools/integrations |
| openarm | https://github.com/enactic/openarm.git | 21_repos/third_party/openarm | cloned | 9f5b0c6 | robot arm, teleoperation, physical AI reference | No — reference only | Review teleoperation interface |
| dora | https://github.com/dora-rs/dora.git | 21_repos/third_party/dora | cloned | bf45b35 | Rust robotics/dataflow middleware reference | No — reference only | Review dataflow node model |
| dora-hub | https://github.com/dora-rs/dora-hub.git | 21_repos/third_party/dora-hub | cloned | 0bfa9b3 | Dora robot nodes/examples reference | No — reference only | Review example node implementations |
| python-mss | https://github.com/BoboTiG/python-mss.git | 21_repos/third_party/python-mss | cloned | 65cfa6d | continuous screen capture library reference | No — reference only | Evaluate for continuous frame capture |
| python-mss-examples | https://github.com/screenshotone/python-mss-examples.git | 21_repos/third_party/python-mss-examples | cloned | 9fd876c | screen recording examples | No — reference only | Review recording loop patterns |
| vosk-api | https://github.com/alphacep/vosk-api.git | 21_repos/third_party/vosk-api | cloned | 9adbd76 | offline speech recognition reference | No — reference only | Evaluate for offline STT integration |
| whisper | https://github.com/openai/whisper.git | 21_repos/third_party/whisper | cloned | 04f449b | speech-to-text reference | No — reference only | Evaluate for STT integration |
| python-sounddevice | https://github.com/spatialaudio/python-sounddevice.git | 21_repos/third_party/python-sounddevice | cloned | 715d988 | microphone/audio capture reference | No — reference only | Evaluate for microphone input |
| unsloth | https://github.com/unslothai/unsloth.git | 21_repos/third_party/unsloth | cloned | ac2daf8 | local model training/GRPO reference | No — reference only | Review GRPO training patterns |
| Kronos | https://github.com/shiyu-coder/Kronos.git | 21_repos/third_party/Kronos | cloned | 67b630e | financial market foundation model reference | No — reference only | Review model architecture |
| Kronos-demo | https://github.com/shiyu-coder/Kronos-demo.git | 21_repos/third_party/Kronos-demo | cloned | dd62473 | Kronos demo reference | No — reference only | Review demo inference patterns |
| MiroFish | https://github.com/666ghj/MiroFish.git | 21_repos/third_party/MiroFish | cloned | fa0f651 | multi-agent prediction/simulation reference | No — reference only | Review multi-agent simulation design |
| mirofish-english | https://github.com/amadad/mirofish.git | 21_repos/third_party/mirofish-english | cloned | 3e98e77 | English CLI fork of MiroFish | No — reference only | Review CLI interface |
| claw-code-android | https://github.com/friuns2/claw-code-android.git | 21_repos/third_party/claw-code-android | cloned | 594ed1f | phone/mobile coding-agent reference | No — reference only | Review mobile agent interface |

## Truth

### Which repos are cloned
All 21 repos are present and accessible.

### Failed/missing
None failed. 4 repos (openclaw, browser-use, aider, awesome-claude-code) had `dubious ownership` git errors (cloned by user `ai_sandbox`, current user `Navif`) — fixed by adding safe.directory exceptions; commits verified.

### Repos used in product code now
**None.** All 21 repos are reference-only. No third-party repo code has been imported into `01_projects/` or any product path.

### Reference-only repos
All 21 repos listed above.

---

## Concept References (not cloned)

| Name | URL | Reason |
|------|-----|--------|
| mithi/robotics-coursework | https://github.com/mithi/robotics-coursework | Robotics learning resources — reference concept only; not needed for cloning |

## Ghoti Truth

### Real continuous screen recording: NO
The dashboard's snapshot endpoint (`POST /api/ghoti/active/snapshot`) captures a **single screenshot on demand** using PowerShell + `System.Windows.Forms.Screen`. It does NOT loop or continuously record frames. There is no video output, no frame buffer, no python-mss integration.

### Real microphone speech input: NO
`audio_enabled: false` in the active mode state. No microphone capture code exists in server.js or app.js. vosk-api and whisper are reference clones only — not integrated.

### Realtime dashboard streaming: NO
The dashboard polls the server via HTTP fetch. There is no WebSocket, SSE, or push streaming.

### Screenshot capture (on-demand): YES
`POST /api/ghoti/active/snapshot` uses PowerShell to capture the primary screen and saves to `.tmp-screenshots/`. This works when PowerShell is available.

### Visible active indicator: YES
`ghoti-active-pill` element in the UI changes class/label based on active mode state. Rail label shows "Ghoti active — screen view on" or "Ghoti idle".

### How to start/stop
- **Start:** `POST /api/ghoti/active/start` (or click "Start Ghoti" in the Active tab)
- **Stop:** `POST /api/ghoti/active/stop` (or click "Stop Ghoti" in the Active tab)
- **Server:** `cd 01_projects/dashboard_mvp && node server.js` (port 3210)
