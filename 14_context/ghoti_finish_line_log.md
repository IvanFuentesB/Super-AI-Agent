# Ghoti Finish Line Log

---

## Milestone Run: Approval Queue + Route Guards

Date: 2026-04-19
Milestone: Approval Queue + Route Guards
Branch: feat/ghoti-visible-operator-stack
Commit: d64d7fa
Pushed: YES
Port: 3210

### What is real

- Approval queue storage: real ÔÇö JSON-backed at `runtime_data/approvals.json`, gitignored
- Payload sanitization: real ÔÇö sensitive keys (token, password, api_key, etc.) replaced with `[redacted]`
- GET /api/ghoti/approvals: real ÔÇö status filter, pending_count
- POST /api/ghoti/approvals/request: real ÔÇö creates sanitized approval record
- POST /api/ghoti/approvals/<id>/approve: real ÔÇö sets status=approved
- POST /api/ghoti/approvals/<id>/reject: real ÔÇö sets status=rejected with notes
- POST /api/ghoti/approvals/<id>/consume: real ÔÇö sets status=consumed, refuses if not approved
- Session cleanup guard: real ÔÇö cleanup-confirm requires approval_id; creates pending approval without it; validates+consumes on retry
- Duplicate pending detection: real ÔÇö reuses existing pending approval for same session
- Dashboard approvals panel: real ÔÇö Ghoti Approval Queue panel with approve/reject buttons, 3s auto-refresh
- Cleanup UI approval handling: real ÔÇö shows approval_id, stores for retry, prompts operator
- Overlay pending badge: real ÔÇö polls /api/ghoti/approvals?status=pending, highlights when pending > 0
- Operator status approvals block: real ÔÇö pending_count, enforced_on, enforced_stub_for
- Brain status note: real ÔÇö explicit "Ollama reachable at ... Models loaded: N. Not wired to drive operator. No frame understanding. No action planning."
- Active Mode regression: PASS

### What is scaffold

- Voice API: still placeholder, no real microphone
- YouTube follower: still scaffold, no browser execution
- Approval UI in cleanup: manual retry flow ÔÇö operator clicks confirm again after approval (no auto-retry)

### What is not implemented

- Real voice/STT/TTS
- Real browser automation
- Approval queue for any route other than cleanup_capture_files
- AI frame understanding
- Ollama driving operator actions

### Feature status table

| Feature | Status | Notes |
|---|---|---|
| Approval queue storage | real | JSON-backed, gitignored, bounded 200 items |
| Payload sanitization | real | Sensitive keys redacted, confirmed in validation |
| GET /api/ghoti/approvals | real | Status filter, pending_count |
| POST /approvals/request | real | Creates record, sanitizes payload |
| POST /approvals/<id>/approve | real | Sets approved, refused if not pending |
| POST /approvals/<id>/reject | real | Sets rejected with notes |
| POST /approvals/<id>/consume | real | Consumes if approved, refuses otherwise |
| Session cleanup guard wired | real | POST /api/ghoti/active/session/cleanup-confirm |
| Cleanup UI approval handling | real | Shows approval_id, data-approval-id for retry |
| Stub guard contract | documented | Comment block + requiresOperatorApproval |
| Dashboard approvals panel | real | Ghoti Approval Queue panel, approve/reject, 3s refresh |
| Overlay pending badge | real | Polls approvals, warns when pending > 0 |
| Operator status approvals block | real | pending_count, enforced_on, enforced_stub_for |
| Brain status note honest | yes | Explicit: reachable/not wired/no frame understanding/no action planning |
| Active Mode regression | PASS | 200 image/png, frame_count > 0 |

### Validation results

| Command/Check | Result |
|---|---|
| node --check server.js | PASS |
| node --check app.js | PASS |
| node --check overlay.js | PASS |
| GET /api/ghoti/approvals?status=pending | 200 OK |
| POST /approvals/request (with token) | 200 OK ÔÇö token [redacted] |
| POST /approvals/<id>/approve | 200 OK ÔÇö status=approved |
| POST /approvals/<id>/consume | 200 OK ÔÇö status=consumed |
| Consume again (double-consume) | 200 ok:false error:approval_not_approved |
| POST /approvals/request (reject test) | 200 OK |
| POST /approvals/<id>/reject | 200 OK ÔÇö status=rejected |
| Consume rejected | 200 ok:false error:approval_not_approved |
| Cleanup without approval | 200 ok:false approval_required:true |
| Cleanup with valid approval | 200 ok:true deleted_count:2 |
| Approval consumed after cleanup | confirmed status:consumed |
| latest.png preserved | EXISTS |
| frame-*.png after cleanup | 0 remaining |
| Operator status approvals block | pending_count present |
| Brain status note | Explicit/honest ÔÇö no wired/no frame understanding |
| /overlay | 200 OK |
| Active Mode regression | PASS ÔÇö frame_count>0, 200 image/png |

### Third-party repo truth table

No changes ÔÇö all reference-only, none imported or runtime-used.

### Files modified

- `01_projects/dashboard_mvp/server.js` ÔÇö approval helpers, routes, cleanup guard, operator status, brain note
- `01_projects/dashboard_mvp/public/index.html` ÔÇö Ghoti Approval Queue panel section
- `01_projects/dashboard_mvp/public/app.js` ÔÇö cleanup confirm handler, Ghoti approval queue JS
- `01_projects/dashboard_mvp/public/overlay.html` ÔÇö approvals badge row
- `01_projects/dashboard_mvp/public/overlay.css` ÔÇö approvals pending styling
- `01_projects/dashboard_mvp/public/overlay.js` ÔÇö applyApprovalsState, fetchState poll
- `14_context/ghoti_finish_line_log.md` ÔÇö this update

### Files created

None (all files were existing).

### Files intentionally not staged

- `21_repos/third_party/.gitkeep`
- `01_projects/mcp_server/test.txt`

### Runtime/generated not committed

- `01_projects/runtime_mvp/runtime_data/approvals.json` ÔÇö gitignored
- `01_projects/runtime_mvp/runtime_data/*.json` ÔÇö all gitignored
- `01_projects/dashboard_mvp/.tmp-screenshots/**` ÔÇö gitignored

### Honest estimates

| Area | Estimate |
|---|---|
| Active Mode slice | ~90% |
| Overlay/presence | ~90% ÔÇö now shows approvals badge |
| Approval queue | ~80% ÔÇö lifecycle works; only cleanup wired; UI functional |
| Voice | ~15% ÔÇö scaffold only |
| YouTube follower | ~10% ÔÇö scaffold only |
| Full Ghoti vision | ~10% ÔÇö approval substrate in place |

### Next milestone recommendation

**Milestone: Ollama Frame-Reading Read-Only Observer**

Reason: approval gates now exist. The next safest step is read-only understanding of frames ÔÇö no clicking, no typing, no browser execution. Ollama is reachable; wire it to describe a captured frame on demand. All output must be logged and displayed, never acted upon automatically. Approval required before any action is taken based on an observation.

---

## Milestone Run: Approval Queue Hardening Patch

Date: 2026-04-19
Milestone: Approval Queue Hardening Patch (N+1.1)
Branch: feat/ghoti-visible-operator-stack
Commit: e731fc5
Pushed: YES
Port: 3210

### Discovery findings

Gaps found (all 10 from the prompt confirmed present):

1. `writeApprovals()` did not use atomic temp-write + rename ÔÇö FOUND
2. Approval records did not include `expires_at_utc` ÔÇö FOUND
3. Lazy expiry sweep not implemented ÔÇö FOUND
4. `/api/ghoti/approvals/:id/consume` did not require body `{ action_type }` ÔÇö FOUND
5. Consumed approval replay returned `approval_not_approved` instead of `already_consumed` ÔÇö FOUND
6. Action mismatch protection existed only in helper, not in the public consume route ÔÇö FOUND
7. Payload sanitization missing `bearer`, `private_key`, `ssh_key` ÔÇö FOUND
8. Redaction used `[redacted]` (lowercase) ÔÇö FOUND (standardized to `[REDACTED]`)
9. Overlay approval badge was inside the 2s `fetchState()` Promise.all, not a separate poller ÔÇö FOUND
10. Finish-line log overstated approval queue at ~80% ÔÇö FOUND

### Gaps fixed

All 10 gaps fixed:

1. `writeApprovals()` now writes to `approvals.json.tmp` then `fs.renameSync` to `approvals.json`
2. `createApprovalRequest()` now sets `expires_at_utc: new Date(now + 15min).toISOString()`
3. `readApprovals()` now does lazy expiry sweep: pending records past `expires_at_utc` become `status: "expired"`, writes back only if changed. Records missing `expires_at_utc` get `legacy_no_expiry: true`
4. `POST /api/ghoti/approvals/:id/consume` now requires `{ action_type }` in body; returns `action_type_required` if absent
5. Replay now returns `already_consumed` (via `validateAndConsumeApproval`)
6. Action mismatch now returns `action_mismatch` on public consume route (via `validateAndConsumeApproval`)
7. `SENSITIVE_KEYS` regex extended to include `bearer|private_key|ssh_key`
8. All redaction values now `[REDACTED]` (uppercase)
9. `overlay.js` now has separate `async function fetchApprovalsState()` with `setInterval(fetchApprovalsState, 3000)` ÔÇö removed from `fetchState()` Promise.all
10. Finish-line log updated with honest status

### Session-binding (5e)

`validateAndConsumeApproval(approvalId, expectedActionType, expectedPayloadSubset)` implemented. Cleanup-confirm passes `{ session_id }` as `expectedPayloadSubset`. Cross-session misuse returns `payload_mismatch`. Validated with real session A approval rejected for session B.

### What remains scaffold

- Voice: placeholder only, no microphone
- YouTube follower: scaffold only
- Approval queue only enforced on `cleanup_capture_files`; stub guard contract documented for all others

### Validation results

| Check | Result |
|---|---|
| node --check server.js | PASS |
| node --check app.js | PASS |
| node --check overlay.js | PASS |
| Create approval with sensitive payload | PASS ÔÇö token/password/bearer/private_key all [REDACTED], payload_sanitized: true, expires_at_utc present |
| Missing action_type on consume | PASS ÔÇö error: action_type_required |
| Approve | PASS ÔÇö status: approved |
| Wrong action_type on consume | PASS ÔÇö error: action_mismatch |
| Correct consume | PASS ÔÇö status: consumed |
| Replay consume | PASS ÔÇö error: already_consumed |
| Reject path | PASS ÔÇö status: rejected |
| Consume rejected | PASS ÔÇö error: approval_rejected |
| Cleanup without approval | PASS ÔÇö approval_required: true |
| Cleanup with valid approval | PASS ÔÇö deleted_count: 6, latest.png preserved |
| Cleanup replay | PASS ÔÇö error: Session has already been cleaned (session-level guard, pre-approval check) |
| Cross-session payload mismatch | PASS ÔÇö error: payload_mismatch |
| Operator status approvals block | PASS ÔÇö pending_count, enforced_on, enforced_stub_for all present |
| Brain status | PASS ÔÇö Ollama reachable, 0 models, honest note |
| /overlay | 200 OK |
| Active Mode regression | PASS ÔÇö 6 frames captured, 200 image/png, stop/start clean |

### Honest status

| Area | Status |
|---|---|
| Atomic approval writes | real ÔÇö temp rename in place |
| TTL / lazy expiry | real ÔÇö expires_at_utc on create, lazy sweep on read |
| Payload sanitization | real ÔÇö [REDACTED] uppercase, bearer/private_key/ssh_key covered |
| Consume requires action_type | real ÔÇö public route enforces |
| Replay protection | real ÔÇö already_consumed |
| Action mismatch protection | real ÔÇö action_mismatch on public route |
| Payload/session binding | real ÔÇö payload_mismatch cross-session confirmed |
| Cleanup guard | real |
| Overlay separate poller | real ÔÇö fetchApprovalsState 3000ms separate from 2000ms fetchState |
| Operator status honest | yes |
| Brain status honest | yes |
| Approval queue % estimate | ~95% ÔÇö all hardening items implemented |

### Files modified

- `01_projects/dashboard_mvp/server.js` ÔÇö atomic writes, TTL, expiry sweep, extended SENSITIVE_KEYS, [REDACTED] uppercase, action_type required on consume, validateAndConsumeApproval with payload subset
- `01_projects/dashboard_mvp/public/overlay.js` ÔÇö separate fetchApprovalsState() poller
- `14_context/ghoti_finish_line_log.md` ÔÇö this update
- `14_context/ghoti_current_prompt.md` ÔÇö overwritten with hardening patch prompt (pre-existing requirement)

### Files not staged

- `21_repos/third_party/.gitkeep`
- `01_projects/mcp_server/test.txt`
- `01_projects/runtime_mvp/runtime_data/*.json` (gitignored)
- `01_projects/dashboard_mvp/.tmp-screenshots/**` (gitignored)

### Third-party repo status

Unchanged ÔÇö reference only.

### Next milestone recommendation

Recommended: **Ollama Frame-Reading Read-Only Observer** ÔÇö now that hardening passes, next safest step is wiring Ollama to describe a captured frame on demand (read-only, no actions, no auto-loop, operator-triggered, output displayed and logged only).

Steps:
1. POST /api/ghoti/active/observe-frame ÔÇö takes a session_id, reads latest frame, sends to Ollama vision model
2. Returns description as text, stored in session log, never triggers actions
3. Approval required before any downstream action
4. Display observation in overlay and dashboard

---

## Milestone Run: Presence + Voice Scaffold + Operator Status + YouTube Follower Plan

Date: 2026-04-19
Milestone: Presence + Voice Scaffold + Operator Status + YouTube Follower Plan
Branch: feat/ghoti-visible-operator-stack
Commit: c3cc8ba
Pushed: YES
Port: 3210

### What is real

- Active Mode start/stop: real ÔÇö session lifecycle, state files, 10 frames captured in regression
- Screen capture (PowerShell CopyFromScreen loop): real ÔÇö 200 image/png from `/api/ghoti/active/latest-frame`
- `/overlay` ÔåÆ serves overlay.html: real ÔÇö 200 OK confirmed
- Voice state persistence: real ÔÇö mute/unmute writes `runtime_data/voice_state.json`
- Ollama brain probe: real ÔÇö direct HTTP check to `127.0.0.1:11434/api/tags`, reachable=true (no models loaded)
- Operator status API: real ÔÇö reads live active/capture/voice state files and returns full spec JSON
- Approval gate contract: `requiresOperatorApproval()` and `buildApprovalRequiredResponse()` present as visible scaffold

### What is scaffold

- Voice API: state machine only ÔÇö no real microphone. `listening` always stays false. Honest placeholders.
- YouTube follower: stores task JSON, no browser execution
- Overlay: browser page polling 6 APIs every 2s ÔÇö not a native always-on-top window (explicitly labeled)
- `start_overlay.ps1`: opens browser to overlay URL, no hidden recording

### What is not implemented

- Real microphone STT (Whisper/Vosk/Web Speech)
- Real TTS
- Real browser automation
- YouTube transcript parsing or step execution
- Approval queue processing UI
- AI screen understanding
- Local LLM driving operator actions (Ollama reachable, not wired)
- Full autonomy

### Feature status table

| Feature | Status | Notes |
|---|---|---|
| Overlay (`/overlay`) | real | Browser-based, 200 OK, polls every 2s |
| Browser overlay notice | real | Visible "Browser overlay ÔÇö not native always-on-top" |
| Voice state API | scaffold | 5 endpoints, all 200, honest placeholders |
| Mute/unmute UI | scaffold | State persisted, no real mic |
| Listen start/stop | scaffold | listening stays false, honest note returned |
| Operator status API | real | Full spec: status/active_mode/capture/voice/brain/operator/local_only/updated_at_utc |
| Brain status API | real (live probe) | Ollama reachable=true, no models, drives_operator=false |
| YouTube follower scaffold | scaffold | GET+POST, stored runtime_data, no execution |
| Active Mode regression | PASS | 10 frames, latest-frame 200 image/png, clean stop |
| Approval gate contract | scaffold | Functions present, queue not wired |

### Third-party repo truth table

| Repo | Present | Imported | Runtime-used | Status | Next step |
|---|---|---|---|---|---|
| claw-code | Yes | No | No | Reference only | Review agent loop architecture |
| browser-use | Yes | No | No | Reference only | Integrate for browser control |
| playwright | Yes | No | No | Reference only | Evaluate for test harness |
| dora | Yes | No | No | Reference only | Review dataflow node model |
| dora-hub | Yes | No | No | Reference only | Review example nodes |
| openarm | Yes | No | No | Reference only | Review teleoperation interface |
| mithi/robotics-coursework | No (concept) | No | No | Concept reference | Not cloned |
| Kronos | Yes | No | No | Reference only | Review model architecture |
| MiroFish | Yes | No | No | Reference only | Review multi-agent simulation |

All 37+ repos under `21_repos/third_party/` are reference-only. None imported or called by runtime.

### Validation results

| Command | Result |
|---|---|
| `node --check server.js` | PASS |
| `node --check app.js` | PASS |
| `node --check overlay.js` | PASS |
| `GET /overlay` | 200 OK HTML |
| `GET /api/ghoti/operator/status` | 200 OK ÔÇö status:idle, all spec fields present |
| `GET /api/ghoti/voice/state` | 200 OK ÔÇö mode:placeholder, real_audio:false |
| `POST /api/ghoti/voice/mute` | 200 OK ÔÇö muted:true |
| `POST /api/ghoti/voice/unmute` | 200 OK ÔÇö muted:false |
| `POST /api/ghoti/voice/listen/start` | 200 OK ÔÇö listening:false, honest note |
| `POST /api/ghoti/voice/listen/stop` | 200 OK ÔÇö listening:false |
| `GET /api/ghoti/brain/status` | 200 OK ÔÇö ollama reachable:true, drives_operator:false |
| `GET /api/ghoti/youtube-follower/status` | 200 OK ÔÇö scaffold, real:false |
| `POST /api/ghoti/youtube-follower/task` | 200 OK ÔÇö task created, execution_enabled:false |
| Active Mode start ÔåÆ capture ÔåÆ 4s ÔåÆ state | 200 OK frame_count:4 |
| `GET /api/ghoti/active/latest-frame` | 200 image/png |
| Active Mode capture/stop | 200 OK frame_count:10 |
| Active Mode stop | 200 OK session stopped |
| Runtime files gitignored | CONFIRMED (4 checked) |

### Files modified

- `01_projects/dashboard_mvp/server.js` ÔÇö approval gate, voice state shape, full operator status, Ollama brain probe, YouTube follower fields
- `01_projects/dashboard_mvp/public/overlay.html` ÔÇö added browser overlay notice
- `01_projects/dashboard_mvp/public/overlay.css` ÔÇö (pre-existing from prior milestone)
- `01_projects/dashboard_mvp/public/overlay.js` ÔÇö (pre-existing from prior milestone)
- `14_context/external_repo_clone_registry.md` ÔÇö (pre-existing from prior milestone)

### Files created

- `01_projects/dashboard_mvp/start_overlay.ps1` ÔÇö overlay launcher (was untracked)
- `14_context/youtube_follower_mvp_plan.md` ÔÇö future architecture doc (was untracked)
- `14_context/ghoti_finish_line_log.md` ÔÇö this file (updated)

### Files intentionally not staged

- `21_repos/third_party/.gitkeep` ÔÇö third-party marker
- `01_projects/mcp_server/test.txt` ÔÇö test artifact

### Runtime/generated files not committed

- `01_projects/runtime_mvp/runtime_data/*.json` ÔÇö gitignored
- `01_projects/dashboard_mvp/.tmp-screenshots/**` ÔÇö gitignored

### Honest estimates

| Area | Estimate |
|---|---|
| Active Mode slice (capture/gallery/cleanup) | ~90% |
| Overlay/presence | ~85% ÔÇö browser-based, full polling, honest labeling |
| Voice | ~15% ÔÇö scaffold only, no real audio |
| YouTube follower | ~10% ÔÇö scaffold and plan only |
| Full Ghoti vision | ~8% ÔÇö early prototype |

### Next milestone recommendation

**Milestone: Real Voice Input + Approval Queue UI**

1. Wire Web Speech API in overlay for push-to-talk STT (no hidden recording)
2. Add approval queue table to dashboard with approve/reject buttons
3. Wire `requiresOperatorApproval` to actual route guards for shell/browser/cleanup actions
4. Show approval queue count in overlay
5. Test local Whisper via python-sounddevice + whisper.cpp

---

## Previous run: Ghoti Presence Overlay MVP

Date: 2026-04-19T17:00:00Z

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
 M 21_repos/third_party/.gitkeep   ÔåÉ excluded from commits
?? 01_projects/mcp_server/test.txt  ÔåÉ excluded from commits
```

## Honest product status
- Active Mode capture/gallery/archive/cleanup: **DONE** ÔÇö per-session isolation, session_id-wired gallery, cleanup confirmed and validated
- Presence overlay: **BUILT THIS RUN** ÔÇö `/overlay.html` + `overlay.js` + `overlay.css` at port 3210; shows active/capture/voice-placeholder; Start/Stop Ghoti, Start/Stop Watching, live frame thumb
- Voice input: **NOT BUILT** ÔÇö `audio_enabled: false`; vosk-api and whisper are reference clones only; no microphone code
- Mute: **PLACEHOLDER ONLY** ÔÇö overlay shows "Voice: Muted (not configured)"; no real audio state API
- Browser operator: **SCAFFOLDED BUT NOT FUNCTIONAL** ÔÇö browser-use, playwright, stagehand cloned as reference; no real browser control code in `01_projects/`
- YouTube-following: **NOT BUILT** ÔÇö no transcript extraction, no step execution
- Desktop operator: **PARTIAL** ÔÇö PowerShell bridge, recipe runner, focus/hotkey actions exist; no AI-driven decision loop
- External repo integrations: **NONE** ÔÇö all 37 cloned repos are reference-only
- GitHub push: **PENDING THIS RUN**

## External repo truth table

| Repo/concept | Present locally? | Actually used in product? | If used, where? | Next useful step |
|---|---|---|---|---|
| claw-code | Yes | No ÔÇö reference only | ÔÇö | Review agent loop architecture |
| openclaw | Yes | No ÔÇö reference only | ÔÇö | Review channels/remote-control design |
| browser-use | Yes | No ÔÇö reference only | ÔÇö | Review agent browser action patterns |
| browser-harness | Yes | No ÔÇö reference only | ÔÇö | Review CDP interface |
| browser-use-examples | Yes | No ÔÇö reference only | ÔÇö | Review example action patterns |
| browser-use-web-ui | Yes | No ÔÇö reference only | ÔÇö | Review web UI scaffolding |
| playwright | Yes | No ÔÇö reference only | ÔÇö | Evaluate for future test harness |
| playwright-official | Yes | No ÔÇö reference only | ÔÇö | Same as playwright |
| stagehand | Yes | No ÔÇö reference only | ÔÇö | Review AI browser actions |
| aider | Yes | No ÔÇö reference only | ÔÇö | Review diff/patch application |
| awesome-claude-code | Yes | No ÔÇö reference only | ÔÇö | Review ecosystem index |
| openarm | Yes | No ÔÇö reference only | ÔÇö | Review teleoperation interface |
| dora | Yes | No ÔÇö reference only | ÔÇö | Review dataflow node model |
| dora-hub | Yes | No ÔÇö reference only | ÔÇö | Review example nodes |
| python-mss | Yes | No ÔÇö reference only | ÔÇö | Evaluate for continuous frame capture |
| python-mss-examples | Yes | No ÔÇö reference only | ÔÇö | Review recording loop patterns |
| vosk-api | Yes | No ÔÇö reference only | ÔÇö | Evaluate for offline STT |
| whisper | Yes | No ÔÇö reference only | ÔÇö | Evaluate for STT integration |
| python-sounddevice | Yes | No ÔÇö reference only | ÔÇö | Evaluate for microphone input |
| unsloth | Yes | No ÔÇö reference only | ÔÇö | Review GRPO training patterns |
| Kronos | Yes | No ÔÇö reference only | ÔÇö | Review model architecture |
| Kronos-demo | Yes | No ÔÇö reference only | ÔÇö | Review demo inference |
| MiroFish | Yes | No ÔÇö reference only | ÔÇö | Review multi-agent simulation |
| mirofish-english | Yes | No ÔÇö reference only | ÔÇö | Review CLI interface |
| claw-code-android | Yes | No ÔÇö reference only | ÔÇö | Review mobile agent interface |
| open-computer-use | Yes | No ÔÇö reference only | ÔÇö | Review desktop computer-use patterns |
| open-interpreter | Yes | No ÔÇö reference only | ÔÇö | Review interpreter loop |
| openhands | Yes | No ÔÇö reference only | ÔÇö | Review agent task patterns |
| openhands-cli | Yes | No ÔÇö reference only | ÔÇö | Review CLI agent interface |
| logto | Yes | No ÔÇö reference only | ÔÇö | Review auth/identity patterns |
| n8n | Yes | No ÔÇö reference only | ÔÇö | Review workflow automation patterns |
| mcp-servers | Yes | No ÔÇö reference only | ÔÇö | Review MCP server patterns |
| windows-mcp | Yes | No ÔÇö reference only | ÔÇö | Review Windows MCP integration |
| windows-use | Yes | No ÔÇö reference only | ÔÇö | Review Windows computer-use patterns |
| career-ops | Yes | No ÔÇö reference only | ÔÇö | Personal reference |
| claude-code-official | Yes | No ÔÇö reference only | ÔÇö | Claude Code docs reference |
| cv-santiago | Yes | No ÔÇö reference only | ÔÇö | Personal reference |
| mithi/robotics-coursework | No ÔÇö concept only | No | ÔÇö | Robotics learning resources reference |

## Work chosen for this run
Built the Ghoti Presence Overlay MVP:
- `01_projects/dashboard_mvp/public/overlay.html` ÔÇö compact dark-theme overlay page
- `01_projects/dashboard_mvp/public/overlay.js` ÔÇö polls active-state + capture-state every 3s; Start/Stop Ghoti, Start/Stop Watching, live frame refresh
- `01_projects/dashboard_mvp/public/overlay.css` ÔÇö compact dark theme matching Ghoti brand
- Added "Ô¼í Overlay" link in the active-mode rail in `index.html`
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
node --check server.js           ÔåÆ OK
node --check public/app.js       ÔåÆ OK
node --check public/overlay.js   ÔåÆ OK
GET /overlay.html                ÔåÆ HTTP 200
GET /overlay.js                  ÔåÆ HTTP 200
GET /overlay.css                 ÔåÆ HTTP 200
GET /api/ghoti/active-state      ÔåÆ ok:true, active:false
GET /api/ghoti/active/capture-state ÔåÆ ok:true, capturing:false
POST /api/ghoti/active/start     ÔåÆ ok:true, session_id present
POST /api/ghoti/active/capture/start ÔåÆ ok:true
(wait 3s) capture-state          ÔåÆ capturing:true, session_id present
POST /api/ghoti/active/capture/stop ÔåÆ ok:true
POST /api/ghoti/active/stop      ÔåÆ ok:true
```

## Final result
Overlay MVP built and serving at `http://127.0.0.1:3210/overlay.html`.
All APIs reachable. All syntax checks pass.
Browser visual verification not available from CLI ÔÇö see honest note below.

## Next best step
Add voice mute state API (`GET/POST /api/ghoti/voice/state`) with muted/unmuted toggle,
update overlay to use real mute state, and add a mute button to the main dashboard Active tab.
This is the cheapest "real" step before tackling browser operator or YouTube-following.


---

## 2026-04-20 ÔÇö Ollama Frame-Reading Read-Only Observer

### Milestone
Ollama Frame-Reading Read-Only Observer

### Current UTC date
2026-04-20T07:25:42Z

### Branch
`feat/ghoti-visible-operator-stack`

### Commit hash after commit
To be recorded from git after the milestone commit is created in this run. This log entry is included inside that same commit, so the exact final hash is reported in git metadata and the release report.

### Push status
Pending at log-write time. Final push result is recorded in the release report for this run.

### Discovery
- Current git branch/head before commit: `feat/ghoti-visible-operator-stack` @ `e731fc5`
- Dashboard files used:
  - `01_projects/dashboard_mvp/server.js`
  - `01_projects/dashboard_mvp/public/index.html`
  - `01_projects/dashboard_mvp/public/app.js`
  - `01_projects/dashboard_mvp/public/overlay.html`
  - `01_projects/dashboard_mvp/public/overlay.js`
  - `01_projects/dashboard_mvp/public/styles.css`
- Ollama reachable: **yes** at `127.0.0.1:11434`
- Models found: `[]`
- Vision model selected: **none**
- Frame path method used: per-session `latest.png` under `01_projects/dashboard_mvp/.tmp-screenshots/capture_frames/<session_id>/latest.png`, resolved via existing session helpers
- Validation server port: **3212**
  - Port `3210` was occupied by a stale listener outside this session and could not be stopped due `Access denied`, so live validation used a clean local port without changing product behavior.

### What is real
- `GET /api/ghoti/brain/vision-status` returns honest Ollama/vision availability, selected model, all local models, and a note that read-only observation does not drive actions.
- `POST /api/ghoti/active/observe-frame` is real and writes observation records to ignored runtime storage.
- `GET /api/ghoti/active/observations` lists recent observations, newest first, bounded.
- Missing session, missing frame, and no-model cases are handled explicitly and stored with honest statuses.
- `GET /api/ghoti/operator/status` now exposes a real `vision` block with observation counters and timestamps.
- Dashboard Active tab now has a read-only observer panel with session input, prompt box, run button, result area, and recent observations list.
- Overlay now shows a minimal observer status indicator.
- Frame data is sent only to local Ollama at `127.0.0.1:11434` and nowhere else.

### What is scaffold
- Vision description happy path is **not validated yet** because no vision-capable Ollama model is installed locally.
- Overlay is still a browser-served overlay page, not a native always-on-top window.
- Voice remains placeholder-only.
- YouTube follower remains scaffold-only.

### What is not implemented
- No action planning from observations.
- No clicks, typing, browser execution, shell automation, or external action wiring from the observer.
- No autonomous action loop.
- No real voice/STT/TTS integration.
- No real browser/YouTube execution from observer output.

### Honest status
| Area | Status |
|---|---|
| Ollama frame observer | **Real read-only path** |
| Vision model installed locally | **No** |
| Observation storage | **Real** |
| Dashboard observer panel | **Real** |
| Overlay observer indicator | **Real** |
| Action planning | **Not implemented** |
| Autonomous actions | **Not implemented** |
| Active Mode capture/gallery/archive/cleanup | **Still working after regression validation** |
| Full Ghoti estimate | **~40%** honest total vision completion |

### External repo truth table
| Repo/concept | Truth |
|---|---|
| `claw-code` | Reference only. Not imported, not called, not runtime. |
| `mithi/robotics-coursework` | Concept/reference only. Not cloned into product runtime and not used in code. |

### Files modified
- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/index.html`
- `01_projects/dashboard_mvp/public/app.js`
- `01_projects/dashboard_mvp/public/overlay.html`
- `01_projects/dashboard_mvp/public/overlay.js`
- `01_projects/dashboard_mvp/public/styles.css`
- `14_context/ghoti_finish_line_log.md`

### Files created
- None tracked in source for this milestone.

### Runtime files not committed
- `01_projects/runtime_mvp/runtime_data/observations.json`
- `01_projects/runtime_mvp/runtime_data/active_mode_state.json`
- `01_projects/runtime_mvp/runtime_data/active_capture_sessions.json`
- `01_projects/runtime_mvp/runtime_data/screen_capture_state.json`
- `01_projects/runtime_mvp/runtime_data/approvals.json`
- `01_projects/dashboard_mvp/.tmp-screenshots/capture_frames/**`

### Files intentionally not staged
- `21_repos/third_party/.gitkeep`
- `01_projects/mcp_server/test.txt`
- all `01_projects/runtime_mvp/runtime_data/*.json`
- all `01_projects/dashboard_mvp/.tmp-screenshots/**`

### Validation commands/results
- `node --check 01_projects/dashboard_mvp/server.js` ÔåÆ OK
- `node --check 01_projects/dashboard_mvp/public/app.js` ÔåÆ OK
- `node --check 01_projects/dashboard_mvp/public/overlay.js` ÔåÆ OK
- `git check-ignore -v ...observations.json ...latest.png` ÔåÆ ignored as expected
- `curl http://127.0.0.1:11434/api/tags` ÔåÆ 200, `{"models":[]}`
- `GET /api/ghoti/brain/vision-status` ÔåÆ OK, `available:false`, `reason:no_vision_model_available`
- `GET /api/ghoti/operator/status` ÔåÆ OK, `vision` block present
- `GET /api/ghoti/active/observations` ÔåÆ OK, returns list
- `GET /overlay` ÔåÆ 200
- Active Mode regression ÔåÆ PASS on port 3212
  - start session: PASS
  - start capture: PASS
  - wait 4s: `frame_count > 0`
  - latest-frame: `200 image/png`
  - observe-frame missing session: `session_id_required`
  - observe-frame before frame: `no_frame`
  - observe-frame with frame: `no_vision_model_available` (acceptable honest path)
- Approval queue regression ÔåÆ PASS
  - create approval: PASS
  - approve: PASS
  - consume: PASS
  - replay consume: FAILS with `already_consumed` as expected
- Cleanup approval guard regression ÔåÆ PASS
  - cleanup preview: PASS
  - cleanup confirm without approval: `approval_required:true`

### Next milestone recommendation
**Recommended:** install and validate one local vision-capable Ollama model, then add a bounded ÔÇ£compare consecutive observationsÔÇØ panel that highlights visible UI changes only.

**Reason:** the read-only observer path is now real, but the happy-path description generation cannot be validated until at least one supported local vision model is available. The next safest step is still observational, not agentic.

---

## Milestone N+1.3 — Dashboard UX Polish + System Health Control Center Repair

Date: 2026-04-20
Branch: feat/ghoti-visible-operator-stack
Commit: TBD (see git log after this repair commit)
Pushed: TBD

### Reason for repair

The first N+1.3 local commit (`294a630`) was not pushed. It introduced useful UI/system-health work, but required repair because:
- `index.html` was massively rewritten and needed duplicate-ID validation.
- `ghoti_finish_line_log.md` accidentally removed prior history (540→43 lines) and was restored.
- Push was blocked, which prevented a risky unvalidated state from reaching GitHub.

### What is real

- `GET /api/ghoti/system/health` endpoint exists and returns consolidated subsystem health.
- Boot-time git hash exists.
- Ollama/vision status cache exists.
- Overlay URL now uses relative paths instead of hardcoded `127.0.0.1:3210`.
- Dashboard UI polish preserved after duplicate-ID audit and repair.
- Voice remains scaffold only.
- YouTube follower remains scaffold only.
- Browser overlay remains browser-based, not native.

### What was repaired

- Finish-line log history restored from HEAD~1 (658 lines → fully preserved).
- Duplicate ID audit completed: 6 duplicate IDs found (`handoff-source-window`, `handoff-source-candidate`, `handoff-target-candidate`, `ghoti-approval-inbox-panel`, `ghoti-actionable-task-list`, `ghoti-next-step-list`) — all removed from hidden `#legacy-compat` stubs; real visible elements preserved.
- UI validated on port 3215 (stale server on 3210 from 2026-04-19 bypassed with fallback port).

### Validation

- node --check server.js: PASS
- node --check app.js: PASS
- node --check overlay.js: PASS
- GET /: PASS (200)
- GET /overlay: PASS (200)
- GET /api/ghoti/system/health: PASS (200)
- GET /api/ghoti/operator/status: PASS (200)
- GET /api/ghoti/approvals?status=pending: PASS (200)
- GET /api/ghoti/brain/vision-status: PASS (200)
- GET /api/ghoti/brain/status: PASS (200)
- GET /api/ghoti/voice/state: PASS (200)
- GET /api/ghoti/youtube-follower/status: PASS (200)
- Approval queue regression: PASS (create, redact, consume-without-type rejected, wrong-type rejected, correct-consume, replay-rejected)
- Active Mode regression: PASS (frame_count=4, latest-frame=200, content-type=image/png, stop clean)
- Duplicate IDs: PASS — none found after repair

### Files modified

- `01_projects/dashboard_mvp/public/index.html` — removed 6 hidden duplicate-ID stubs from #legacy-compat
- `14_context/ghoti_finish_line_log.md` — restored full prior history, appended this entry

### Files intentionally not staged

- `21_repos/third_party/.gitkeep`
- `01_projects/mcp_server/test.txt`
- `01_projects/runtime_mvp/runtime_data/*.json`
- `01_projects/dashboard_mvp/.tmp-screenshots/**`
- `14_context/ghoti_finish_line_log_restored.md` (temp repair artifact)

### Next milestone recommendation

Recommended: validate the observer with a pulled local vision model (`ollama pull llava:7b`) before moving to voice/browser/desktop control.

---

## Milestone Run: Gemma/Ollama Truth + Token-Resilient Operator Foundation (N+1.4)

### Date
2026-04-20

### Branch
feat/ghoti-visible-operator-stack

### Commit hash
(set after commit below)

### Push status
(set after push)

### Audit summary
- HEAD and remote both at adea7b1 ✓
- Duplicate IDs: PASS (none found)
- Finish-line log preserved: YES (726 lines before this entry)
- Ollama reachable: YES (0 models installed)

### Model inventory truth
- Gemma available: NO (Ollama reachable, 0 models)
- Selected text model: null
- Vision model available: NO
- Gemma drives operator: false
- Action planning: false
- Autonomous actions: false

### Gemma diagnostic probe result
- Probe returns `ok:false, error:"no_gemma_model_available"` — correct honest behavior
- Probe record written to `runtime_data/model_probes.json` (gitignored)

### Capture gallery clarification added
YES — "Local Frame Gallery" note added. Clarifies: local-only screenshots, not AI screen-sharing, frame only sent to Ollama on manual trigger.

### Token-resilience truth
- state_persisted: true
- runtime_data_gitignored: true
- finish_line_log_present: true
- current_prompt_path: 14_context/ghoti_current_prompt.md
- can_resume_after_chat_limits: true
- note: Long-running autonomy is not implemented. Current resilience is checkpoint/log/prompt based.

### Validation results
- GET /: PASS (200)
- GET /overlay: PASS (200)
- GET /api/ghoti/system/health (with models + token_resilience): PASS
- GET /api/ghoti/models/status: PASS
- GET /api/ghoti/models/probes: PASS
- POST /api/ghoti/models/gemma-probe (no model): PASS (ok:false, error:no_gemma_model_available)
- Approval queue regression (create, redact, approve, wrong-type rejected, correct-consume, replay rejected): PASS
- Active Mode regression (start, capture, latest-frame 200 image/png, stop): PASS
- Duplicate IDs: PASS
- model_probes.json gitignored: CONFIRMED

### Files modified
- `01_projects/dashboard_mvp/server.js` — added model inventory status, Gemma diagnostic probe routes, extended health endpoint with models + token_resilience blocks
- `01_projects/dashboard_mvp/public/index.html` — added Local Brain Truth card, updated Observer to "diagnostic probe" wording, clarified Local Frame Gallery
- `01_projects/dashboard_mvp/public/app.js` — folded model status into health poll, added probe button handler and probe history display
- `14_context/ghoti_finish_line_log.md` — appended this entry

### Files intentionally not staged
- `21_repos/third_party/.gitkeep`
- `01_projects/mcp_server/test.txt`
- `01_projects/runtime_mvp/runtime_data/*.json`
- `01_projects/dashboard_mvp/.tmp-screenshots/**`

### Honest status

What is real:
- Active Mode capture/gallery/cleanup: ~90% real
- Approval queue hardening: ~95% real
- System health endpoint (with models + token_resilience): real
- Ollama reachability probe: real
- Model inventory endpoint: real
- Gemma diagnostic probe route: real (honest no_gemma_model_available when no model)
- Token-resilience status: real (checkpoint/log/prompt based, not daemon)
- Local Brain Truth UI card: real
- Capture gallery / Local Frame Gallery clarification: real
- Observer "diagnostic probe" relabeling: real

What remains scaffold:
- Voice: scaffold only
- YouTube follower: scaffold only
- Autonomous computer control: not implemented
- Gemma as action brain: not wired (no model installed)
- Native always-on-top overlay: not implemented

### Next milestone recommendation

Recommended: Install or restore Gemma model inventory (`ollama pull gemma3`), then re-run model diagnostic probe to validate local text model. Do not recommend LLaVA unless user explicitly asks.
