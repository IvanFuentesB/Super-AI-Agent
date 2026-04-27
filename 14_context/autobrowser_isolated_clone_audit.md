# AutoBrowser Isolated Clone Audit

Status label: `isolated_clone_audit / no_install / no_runtime_wiring`
Date: 2026-04-26
Branch: `feat/ghoti-visible-operator-stack`
Milestone: N+2.9
Auditor: Claude Code (Sonnet 4.6)

---

## Clone Truth

- Clone path: `21_repos/third_party/evals/auto-browser`
- Source URL: https://github.com/LvcidPsyche/auto-browser
- Clone command: `git clone --depth 1 https://github.com/LvcidPsyche/auto-browser.git`
- Commit hash cloned: `e646a48` — "Merge pull request #23 from LvcidPsyche/codex/clear-final-path-alerts"
- Package version: v1.0.2
- docker compose up run: NO
- npm/pip install run: NO
- daemons or MCP servers started: NO
- Auth profiles configured: NO
- Staged in git: NO (third-party eval area; intentionally excluded)

---

## Why It Matters for Ghoti

AutoBrowser is a supervised browser control plane with human takeover, approval gates, and audit trails built in. It directly maps to Ghoti's need for a browser/operator layer that can:
- Execute browser actions on behalf of the operator
- Allow a human to take over when automation fails
- Maintain approval gates before consequential actions
- Keep audit trails of all actions
- Reuse saved auth profiles for accounts the operator has already authenticated

This is the most directly aligned tool for a supervised browser operator layer in Ghoti.

---

## License

- License: MIT
- Copyright: 2026 Jake Dillashaw
- Commercial-use: permitted
- AGPL implications: none
- Attribution required: yes (copyright notice)

---

## Human Takeover / Approvals / Audit Trails / Auth Profile Claims

From README.md (v1.0.2):

- **Human takeover**: noVNC exposes the live browser session at `http://127.0.0.1:6080/vnc.html` — a human can visually take over the same active session when automation fails. Confirmed in docker-compose.yml (port 6080 bound to 127.0.0.1).
- **Approvals**: README lists "approval gates" as part of the 1.0 platform surface.
- **Audit trails**: README explicitly lists "audit events" and "Witness receipts" in the operator safety column.
- **PII scrubbing**: listed as a built-in safety feature.
- **Auth profiles**: README claims "Login once, reuse later — Save named auth profiles and reopen fresh sessions that are already signed in." Auth profiles persist login state so the browser re-opens already authenticated.
- **Operator identity headers**: listed in the operator safety column.
- **Compliance templates**: `COMPLIANCE_TEMPLATE` env var in docker-compose.yml.
- **Protection profiles**: listed in README.

None of these claims have been verified by runtime test — this is a read-only audit.

---

## Runtime Requirements

- **Docker Compose required**: YES — the entire stack runs via `docker compose up --build`
- **Services**: 2 Docker services
  - `browser-node`: Playwright-backed browser, noVNC (VNC server), 2GB shared memory (`shm_size: 2gb`)
  - `controller`: Python/FastAPI API server that drives browser-node
- **Playwright**: used inside Docker (not installed on host)
- **Python/FastAPI**: inside Docker only (FastAPI + Starlette, rate-limit hardening per v1.0.2 notes)
- **Ports bound to 127.0.0.1**:
  - `6080` — noVNC (visual takeover)
  - `5900` — VNC (raw)
  - `8000` — API + dashboard (controller service, inferred from README)
  - `9223` — Playwright WebSocket (internal between services)
- **Optional**: `.env` file for `API_BEARER_TOKEN`, `LOG_LEVEL`, custom ports

---

## Account / Auth Risk

- No external accounts required for running the stack itself
- Auth profiles store browser session cookies/state for sites the user has authenticated to — these are local to the Docker volume (`./data/browser-profile`)
- API bearer token: optional, for securing the REST API
- No cloud service required
- Data stays local unless a tunnel is explicitly configured (reverse-ssh optional service in repo)
- `COMPLIANCE_TEMPLATE` suggests multi-tenant or regulated-use support — not needed for Ghoti single-operator use

---

## Data / Privacy Risk

- Browser session data (cookies, downloads, profile) stored in `./data/` Docker volume — local only
- PII scrubbing is claimed as a built-in feature
- Audit event logs stored locally
- VNC exposes a live visual feed of the browser — access is local by default (127.0.0.1)
- Reverse-SSH tunnel service exists in the repo but is optional and not started by default
- Risk is low for single-operator local use; escalates if tunnel is enabled or ports are exposed to a network

---

## Windows Feasibility

- Requires Docker Desktop on Windows
- 2GB shared memory (`shm_size: 2gb`) — Docker Desktop must allocate enough memory
- No native Windows binary or PowerShell alternative shown
- noVNC (port 6080) accessible via browser after Docker starts — no additional Windows software needed
- Assessment: feasible with Docker Desktop installed and approved; needs operator to confirm Docker Desktop is present

---

## Relationship to Existing Playwright Route Validation

- Ghoti's existing Playwright reference clone is in `21_repos/third_party/playwright/` (reference only, not wired)
- AutoBrowser uses Playwright internally as the browser engine inside Docker
- Ghoti's existing dashboard route validation skill (`13_prompts/codex_skills/`) uses Playwright for endpoint checking
- AutoBrowser would replace or augment raw Playwright with: human takeover, approval gates, auth profiles, and an MCP transport layer
- They are complementary: raw Playwright for test/validation; AutoBrowser for supervised operator workflows

---

## Verdict

**isolated install candidate** — Docker Compose approval required before first run.

AutoBrowser is the most directly aligned tool for Ghoti's supervised browser/operator layer. Its stated design philosophy (human-in-the-loop, approval gates, no stealth/CAPTCHA, local-first) matches Ghoti's safety requirements. The runtime claims need verification by actually running the stack, but the source and README are consistent and honest about limitations.

Risk is low IF: Docker is used as specified, ports stay bound to 127.0.0.1, reverse-SSH tunnel is not enabled, and auth profiles contain only operator-approved sessions.

---

## Exact Next Safe Step

If operator confirms Docker Desktop is installed and approves:
```
cd 21_repos/third_party/evals/auto-browser
docker compose up --build
```

Then verify:
- `http://127.0.0.1:8000/docs` — API docs load
- `http://127.0.0.1:8000/dashboard` — dashboard loads
- `http://127.0.0.1:6080/vnc.html?autoconnect=true&resize=scale` — noVNC loads

Do NOT configure auth profiles or connect real accounts until the operator reviews the running dashboard and approves further.
