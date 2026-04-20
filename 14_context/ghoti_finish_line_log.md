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

- Approval queue storage: real — JSON-backed at `runtime_data/approvals.json`, gitignored
- Payload sanitization: real — sensitive keys (token, password, api_key, etc.) replaced with `[redacted]`
- GET /api/ghoti/approvals: real — status filter, pending_count
- POST /api/ghoti/approvals/request: real — creates sanitized approval record
- POST /api/ghoti/approvals/<id>/approve: real — sets status=approved
- POST /api/ghoti/approvals/<id>/reject: real — sets status=rejected with notes
- POST /api/ghoti/approvals/<id>/consume: real — sets status=consumed, refuses if not approved
- Session cleanup guard: real — cleanup-confirm requires approval_id; creates pending approval without it; validates+consumes on retry
- Duplicate pending detection: real — reuses existing pending approval for same session
- Dashboard approvals panel: real — Ghoti Approval Queue panel with approve/reject buttons, 3s auto-refresh
- Cleanup UI approval handling: real — shows approval_id, stores for retry, prompts operator
- Overlay pending badge: real — polls /api/ghoti/approvals?status=pending, highlights when pending > 0
- Operator status approvals block: real — pending_count, enforced_on, enforced_stub_for
- Brain status note: real — explicit "Ollama reachable at ... Models loaded: N. Not wired to drive operator. No frame understanding. No action planning."
- Active Mode regression: PASS

### What is scaffold

- Voice API: still placeholder, no real microphone
- YouTube follower: still scaffold, no browser execution
- Approval UI in cleanup: manual retry flow — operator clicks confirm again after approval (no auto-retry)

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
| POST /approvals/request (with token) | 200 OK — token [redacted] |
| POST /approvals/<id>/approve | 200 OK — status=approved |
| POST /approvals/<id>/consume | 200 OK — status=consumed |
| Consume again (double-consume) | 200 ok:false error:approval_not_approved |
| POST /approvals/request (reject test) | 200 OK |
| POST /approvals/<id>/reject | 200 OK — status=rejected |
| Consume rejected | 200 ok:false error:approval_not_approved |
| Cleanup without approval | 200 ok:false approval_required:true |
| Cleanup with valid approval | 200 ok:true deleted_count:2 |
| Approval consumed after cleanup | confirmed status:consumed |
| latest.png preserved | EXISTS |
| frame-*.png after cleanup | 0 remaining |
| Operator status approvals block | pending_count present |
| Brain status note | Explicit/honest — no wired/no frame understanding |
| /overlay | 200 OK |
| Active Mode regression | PASS — frame_count>0, 200 image/png |

### Third-party repo truth table

No changes — all reference-only, none imported or runtime-used.

### Files modified

- `01_projects/dashboard_mvp/server.js` — approval helpers, routes, cleanup guard, operator status, brain note
- `01_projects/dashboard_mvp/public/index.html` — Ghoti Approval Queue panel section
- `01_projects/dashboard_mvp/public/app.js` — cleanup confirm handler, Ghoti approval queue JS
- `01_projects/dashboard_mvp/public/overlay.html` — approvals badge row
- `01_projects/dashboard_mvp/public/overlay.css` — approvals pending styling
- `01_projects/dashboard_mvp/public/overlay.js` — applyApprovalsState, fetchState poll
- `14_context/ghoti_finish_line_log.md` — this update

### Files created

None (all files were existing).

### Files intentionally not staged

- `21_repos/third_party/.gitkeep`
- `01_projects/mcp_server/test.txt`

### Runtime/generated not committed

- `01_projects/runtime_mvp/runtime_data/approvals.json` — gitignored
- `01_projects/runtime_mvp/runtime_data/*.json` — all gitignored
- `01_projects/dashboard_mvp/.tmp-screenshots/**` — gitignored

### Honest estimates

| Area | Estimate |
|---|---|
| Active Mode slice | ~90% |
| Overlay/presence | ~90% — now shows approvals badge |
| Approval queue | ~80% — lifecycle works; only cleanup wired; UI functional |
| Voice | ~15% — scaffold only |
| YouTube follower | ~10% — scaffold only |
| Full Ghoti vision | ~10% — approval substrate in place |

### Next milestone recommendation

**Milestone: Ollama Frame-Reading Read-Only Observer**

Reason: approval gates now exist. The next safest step is read-only understanding of frames — no clicking, no typing, no browser execution. Ollama is reachable; wire it to describe a captured frame on demand. All output must be logged and displayed, never acted upon automatically. Approval required before any action is taken based on an observation.

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

1. `writeApprovals()` did not use atomic temp-write + rename — FOUND
2. Approval records did not include `expires_at_utc` — FOUND
3. Lazy expiry sweep not implemented — FOUND
4. `/api/ghoti/approvals/:id/consume` did not require body `{ action_type }` — FOUND
5. Consumed approval replay returned `approval_not_approved` instead of `already_consumed` — FOUND
6. Action mismatch protection existed only in helper, not in the public consume route — FOUND
7. Payload sanitization missing `bearer`, `private_key`, `ssh_key` — FOUND
8. Redaction used `[redacted]` (lowercase) — FOUND (standardized to `[REDACTED]`)
9. Overlay approval badge was inside the 2s `fetchState()` Promise.all, not a separate poller — FOUND
10. Finish-line log overstated approval queue at ~80% — FOUND

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
9. `overlay.js` now has separate `async function fetchApprovalsState()` with `setInterval(fetchApprovalsState, 3000)` — removed from `fetchState()` Promise.all
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
| Create approval with sensitive payload | PASS — token/password/bearer/private_key all [REDACTED], payload_sanitized: true, expires_at_utc present |
| Missing action_type on consume | PASS — error: action_type_required |
| Approve | PASS — status: approved |
| Wrong action_type on consume | PASS — error: action_mismatch |
| Correct consume | PASS — status: consumed |
| Replay consume | PASS — error: already_consumed |
| Reject path | PASS — status: rejected |
| Consume rejected | PASS — error: approval_rejected |
| Cleanup without approval | PASS — approval_required: true |
| Cleanup with valid approval | PASS — deleted_count: 6, latest.png preserved |
| Cleanup replay | PASS — error: Session has already been cleaned (session-level guard, pre-approval check) |
| Cross-session payload mismatch | PASS — error: payload_mismatch |
| Operator status approvals block | PASS — pending_count, enforced_on, enforced_stub_for all present |
| Brain status | PASS — Ollama reachable, 0 models, honest note |
| /overlay | 200 OK |
| Active Mode regression | PASS — 6 frames captured, 200 image/png, stop/start clean |

### Honest status

| Area | Status |
|---|---|
| Atomic approval writes | real — temp rename in place |
| TTL / lazy expiry | real — expires_at_utc on create, lazy sweep on read |
| Payload sanitization | real — [REDACTED] uppercase, bearer/private_key/ssh_key covered |
| Consume requires action_type | real — public route enforces |
| Replay protection | real — already_consumed |
| Action mismatch protection | real — action_mismatch on public route |
| Payload/session binding | real — payload_mismatch cross-session confirmed |
| Cleanup guard | real |
| Overlay separate poller | real — fetchApprovalsState 3000ms separate from 2000ms fetchState |
| Operator status honest | yes |
| Brain status honest | yes |
| Approval queue % estimate | ~95% — all hardening items implemented |

### Files modified

- `01_projects/dashboard_mvp/server.js` — atomic writes, TTL, expiry sweep, extended SENSITIVE_KEYS, [REDACTED] uppercase, action_type required on consume, validateAndConsumeApproval with payload subset
- `01_projects/dashboard_mvp/public/overlay.js` — separate fetchApprovalsState() poller
- `14_context/ghoti_finish_line_log.md` — this update
- `14_context/ghoti_current_prompt.md` — overwritten with hardening patch prompt (pre-existing requirement)

### Files not staged

- `21_repos/third_party/.gitkeep`
- `01_projects/mcp_server/test.txt`
- `01_projects/runtime_mvp/runtime_data/*.json` (gitignored)
- `01_projects/dashboard_mvp/.tmp-screenshots/**` (gitignored)

### Third-party repo status

Unchanged — reference only.

### Next milestone recommendation

Recommended: **Ollama Frame-Reading Read-Only Observer** — now that hardening passes, next safest step is wiring Ollama to describe a captured frame on demand (read-only, no actions, no auto-loop, operator-triggered, output displayed and logged only).

Steps:
1. POST /api/ghoti/active/observe-frame — takes a session_id, reads latest frame, sends to Ollama vision model
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

- Active Mode start/stop: real — session lifecycle, state files, 10 frames captured in regression
- Screen capture (PowerShell CopyFromScreen loop): real — 200 image/png from `/api/ghoti/active/latest-frame`
- `/overlay` → serves overlay.html: real — 200 OK confirmed
- Voice state persistence: real — mute/unmute writes `runtime_data/voice_state.json`
- Ollama brain probe: real — direct HTTP check to `127.0.0.1:11434/api/tags`, reachable=true (no models loaded)
- Operator status API: real — reads live active/capture/voice state files and returns full spec JSON
- Approval gate contract: `requiresOperatorApproval()` and `buildApprovalRequiredResponse()` present as visible scaffold

### What is scaffold

- Voice API: state machine only — no real microphone. `listening` always stays false. Honest placeholders.
- YouTube follower: stores task JSON, no browser execution
- Overlay: browser page polling 6 APIs every 2s — not a native always-on-top window (explicitly labeled)
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
| Browser overlay notice | real | Visible "Browser overlay — not native always-on-top" |
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
| `GET /api/ghoti/operator/status` | 200 OK — status:idle, all spec fields present |
| `GET /api/ghoti/voice/state` | 200 OK — mode:placeholder, real_audio:false |
| `POST /api/ghoti/voice/mute` | 200 OK — muted:true |
| `POST /api/ghoti/voice/unmute` | 200 OK — muted:false |
| `POST /api/ghoti/voice/listen/start` | 200 OK — listening:false, honest note |
| `POST /api/ghoti/voice/listen/stop` | 200 OK — listening:false |
| `GET /api/ghoti/brain/status` | 200 OK — ollama reachable:true, drives_operator:false |
| `GET /api/ghoti/youtube-follower/status` | 200 OK — scaffold, real:false |
| `POST /api/ghoti/youtube-follower/task` | 200 OK — task created, execution_enabled:false |
| Active Mode start → capture → 4s → state | 200 OK frame_count:4 |
| `GET /api/ghoti/active/latest-frame` | 200 image/png |
| Active Mode capture/stop | 200 OK frame_count:10 |
| Active Mode stop | 200 OK session stopped |
| Runtime files gitignored | CONFIRMED (4 checked) |

### Files modified

- `01_projects/dashboard_mvp/server.js` — approval gate, voice state shape, full operator status, Ollama brain probe, YouTube follower fields
- `01_projects/dashboard_mvp/public/overlay.html` — added browser overlay notice
- `01_projects/dashboard_mvp/public/overlay.css` — (pre-existing from prior milestone)
- `01_projects/dashboard_mvp/public/overlay.js` — (pre-existing from prior milestone)
- `14_context/external_repo_clone_registry.md` — (pre-existing from prior milestone)

### Files created

- `01_projects/dashboard_mvp/start_overlay.ps1` — overlay launcher (was untracked)
- `14_context/youtube_follower_mvp_plan.md` — future architecture doc (was untracked)
- `14_context/ghoti_finish_line_log.md` — this file (updated)

### Files intentionally not staged

- `21_repos/third_party/.gitkeep` — third-party marker
- `01_projects/mcp_server/test.txt` — test artifact

### Runtime/generated files not committed

- `01_projects/runtime_mvp/runtime_data/*.json` — gitignored
- `01_projects/dashboard_mvp/.tmp-screenshots/**` — gitignored

### Honest estimates

| Area | Estimate |
|---|---|
| Active Mode slice (capture/gallery/cleanup) | ~90% |
| Overlay/presence | ~85% — browser-based, full polling, honest labeling |
| Voice | ~15% — scaffold only, no real audio |
| YouTube follower | ~10% — scaffold and plan only |
| Full Ghoti vision | ~8% — early prototype |

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


---

## 2026-04-20 — Ollama Frame-Reading Read-Only Observer

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
- `node --check 01_projects/dashboard_mvp/server.js` → OK
- `node --check 01_projects/dashboard_mvp/public/app.js` → OK
- `node --check 01_projects/dashboard_mvp/public/overlay.js` → OK
- `git check-ignore -v ...observations.json ...latest.png` → ignored as expected
- `curl http://127.0.0.1:11434/api/tags` → 200, `{"models":[]}`
- `GET /api/ghoti/brain/vision-status` → OK, `available:false`, `reason:no_vision_model_available`
- `GET /api/ghoti/operator/status` → OK, `vision` block present
- `GET /api/ghoti/active/observations` → OK, returns list
- `GET /overlay` → 200
- Active Mode regression → PASS on port 3212
  - start session: PASS
  - start capture: PASS
  - wait 4s: `frame_count > 0`
  - latest-frame: `200 image/png`
  - observe-frame missing session: `session_id_required`
  - observe-frame before frame: `no_frame`
  - observe-frame with frame: `no_vision_model_available` (acceptable honest path)
- Approval queue regression → PASS
  - create approval: PASS
  - approve: PASS
  - consume: PASS
  - replay consume: FAILS with `already_consumed` as expected
- Cleanup approval guard regression → PASS
  - cleanup preview: PASS
  - cleanup confirm without approval: `approval_required:true`

### Next milestone recommendation
**Recommended:** install and validate one local vision-capable Ollama model, then add a bounded “compare consecutive observations” panel that highlights visible UI changes only.

**Reason:** the read-only observer path is now real, but the happy-path description generation cannot be validated until at least one supported local vision model is available. The next safest step is still observational, not agentic.
