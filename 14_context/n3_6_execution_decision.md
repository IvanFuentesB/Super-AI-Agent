# N+3.6 Execution Decision Record

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Status label: decision_record / no_runtime_wiring

---

## Next Path Comparison

### A. Docker Desktop Install Gate

**Approval phrase required:** `APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX`

Pros:
- Unlocks CUA Docker/Ubuntu local container path on Windows 11 Home.
- Also unlocks AutoBrowser Docker Compose path.
- Fastest path toward real autonomous computer-use capability.
- Kasm/Ubuntu lightweight container path is a practical first smoke.

Cons:
- Admin/system install with potential reboot.
- Adds WSL2 background subsystem and Docker daemon.
- Image pulls and disk usage (several GBs).
- Background services that run at login unless configured otherwise.
- Requires careful container permissions to avoid host exposure.

Use if: the operator wants the fastest progress toward real computer-use capability.

---

### B. Screenpipe Dashboard Route

Pros:
- Lower risk than Docker install — no new system subsystem.
- Useful immediately for session visibility and retention-status display.
- Can remain read-only / status-only (no capture started).
- Reinforces that capture is operator-start only with 3-day retention.
- Dashboard route already exists; adding status panel is incremental.

Cons:
- Does not unlock actual CUA execution.
- Still requires care not to imply capture is active when it is not.

Use if: the operator wants safer useful progress while avoiding installs.

---

### C. Obsidian Vault Sync

Pros:
- Reduces repeated context cost for every future session.
- Improves handoff continuity across ChatGPT, Claude Code, and Codex.
- Low risk — plain markdown, no install needed.
- Helps every future milestone regardless of which execution path is chosen.

Cons:
- Does not unlock any autonomous execution.
- Requires discipline to keep vault notes compact.

Use if: context sprawl is becoming a significant time cost.

---

### D. AutoBrowser Docker Path

Pros:
- AutoBrowser Docker Compose path would be usable once Docker is installed.
- Provides a supervised browser-control path separate from CUA.

Cons:
- Still blocked on Docker Desktop install — same blocker as A.
- Has not been evaluated as closely as the CUA Docker path.

Use if: Docker is approved and the operator prefers a browser-control path over CUA agent.

---

### E. Gemma Model Pull

Pros:
- Enables local Ollama brain inference for the first time.
- `ollama pull gemma3:4b` is the configured default.

Cons:
- ~2.5 GB download.
- No task path currently calls the local brain automatically.

Use if: the operator wants local model inference readiness before any browser or container work.

---

## Recommendation

**If the operator's top priority is autonomous computer use:**

Choose path A. Approve Docker Desktop install, verify Docker/WSL, then plan screenshot-only CUA sandbox smoke.

**If the operator wants safer useful progress without installs:**

Choose path B (Screenpipe dashboard route) + C (Obsidian vault sync) first. Revisit Docker/CUA after install approval.

---

## Decision Required From Operator

Type exactly one of:

```
APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX
```

or

```
DO SCREENPIPE DASHBOARD + OBSIDIAN SYNC FIRST
```

No runtime wiring, install, or CUA execution will occur until one of these decisions is provided.
