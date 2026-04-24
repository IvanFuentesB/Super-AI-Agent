# OpenClaw Local Multi-Agent Plan

Milestone: N+1.5
Date: 2026-04-24
Status: **research/prep only — not wired**

---

## Local Folders Found

| Path | Exists | Notes |
|------|--------|-------|
| `21_repos/third_party/openclaw` | YES | Full repo content |
| `21_repos/third_party/OpenClaw` | YES | Same content as above (case variant or duplicate clone) |

Both folders contain: `apps/`, `docs/`, `assets/`, `Dockerfile`, `docker-compose.yml`, `Makefile`, `README.md`, `VISION.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `LICENSE`, `CHANGELOG.md`, `SECURITY.md`, `appcast.xml`

---

## Likely Stack

- **Language:** TypeScript / JavaScript (Node.js)
- **Package manager:** npm, pnpm, or bun (all supported)
- **Setup:** `openclaw onboard` CLI command
- **Platform apps:** Android (`apps/android`), iOS (`apps/ios`), macOS (`apps/macos`), shared (`apps/shared`)
- **Infrastructure:** Docker-based gateway (`docker-compose.yml`, multiple Dockerfiles)
- **Windows:** WSL2 strongly recommended; Windows native is partial
- **Channels:** WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage, Mattermost, Matrix, Twitch, Nostr, and more
- **LLM backends:** Connects to OpenAI, local models, and others (configurable)
- **Skills system:** Internal skills for the personal assistant

---

## How It Could Connect to Ghoti Later

OpenClaw as a local AI assistant gateway could augment Ghoti's operator stack:

```
Operator
   |
   +--> Ghoti dashboard (approval queue, health, active mode)
   |       |
   |       +--> Approval gates (human confirms before action)
   |
   +--> OpenClaw gateway (messaging channels + agent dispatch)
           |
           +--> Agent: planner
           +--> Agent: coder (Claude Code)
           +--> Agent: browser operator
           +--> Agent: content researcher
           +--> Agent: store researcher
           +--> Agent: investment analyst (decision-support only)
           +--> Agent: security auditor
           +--> Agent: documentation/report builder
```

Key integration points (future, not wired):
- OpenClaw could surface Ghoti approval requests in Telegram/Slack/Discord
- Ghoti could dispatch tasks to OpenClaw agent queues
- Shared auth/session management
- No autonomous actions without human approval gate

---

## Agents We Want

| Agent | Role | Safety Gate |
|-------|------|-------------|
| Planner | Break down goals into tasks, sequence work | Human reviews plan before execution |
| Coder | Write, review, commit code via Claude Code | Human approves commit/push |
| Browser operator | Search, scrape, gather content (legal) | Human approves target sites + TOS check |
| Content researcher | Research topics, gather facts, summarize | Human reviews before publish |
| Store researcher | KaloData / market research / ad analysis | Human reviews before decisions |
| Investment analyst | Simulation and decision support only | Human decides — no autonomous trading |
| Security auditor | Code review, dependency scan, OSINT (authorized) | Human authorizes scope before run |
| Documentation builder | Generate reports, changelogs, specs | Human reviews before distribution |

---

## Why This Is NOT Wired Yet

1. OpenClaw requires proper setup: `openclaw onboard`, WSL2 on Windows, Docker running
2. Ghoti has no inter-process communication layer for agent dispatch
3. No shared auth/session token store
4. No approval gate integration between Ghoti and OpenClaw
5. Installing and running OpenClaw changes system state (Docker containers, network listeners) — requires explicit human approval and step-by-step verification
6. The folders in `21_repos/third_party/` are read-only reference intake — not live installs

---

## Required Human Approval Gates

Before any OpenClaw wiring:
1. **Explicit install approval** — operator confirms which Docker containers will run and what ports they use
2. **Network review** — confirm no unintended outbound connections
3. **Channel authorization** — operator selects which messaging channels to enable (start with zero)
4. **LLM backend approval** — operator confirms which model API keys are used (local-only preferred)
5. **Agent scope approval** — each agent type enabled individually with defined limits
6. **No autonomous posting** — all content goes through approval queue before dispatch

---

## First Safe Smoke Test Proposal

When ready (NOT this milestone):

```
Step 1: Install Docker (if not present) — confirm with operator
Step 2: cd 21_repos/third_party/openclaw && docker-compose up --no-start
Step 3: Review all container configs — read-only audit, no start
Step 4: Operator approves or rejects each container
Step 5: Start gateway only: docker-compose up gateway
Step 6: Test health endpoint: curl http://localhost:<port>/health
Step 7: No channels enabled yet — gateway only
Step 8: Document results in 14_context/openclaw_smoke_test_results.md
```

This is the minimal-footprint test. Zero messaging channels. Zero API keys. Health check only.

---

## Dashboard Concept — Polished Dark Command Center

Inspired by the user's Boss Visuals / command-center aesthetic:

```
┌─────────────────────────────────────────────────────────┐
│  GHOTI OPERATOR COMMAND CENTER                          │
│  ──────────────────────────────────────────────────── │
│                                                         │
│  [AGENT CARDS]                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Planner  │ │  Coder   │ │ Browser  │ │ Content  │  │
│  │ IDLE     │ │ IDLE     │ │ BLOCKED  │ │ IDLE     │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                         │
│  [APPROVAL QUEUE]                                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │ #001 | coder | commit src/auth.py | PENDING       │  │
│  │ #002 | browser | scrape jobs.nl   | AWAITING OK   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  [INCOME WORKFLOWS]                                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Whop clipping      → manual          │ NOT ACTIVE │  │
│  │ Faceless channels  → not automated   │ NOT ACTIVE │  │
│  │ Store research     → manual          │ NOT ACTIVE │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  [TOOLING TRUTH]                                        │
│  rustc: ✓   cargo: ✓   node: ✓   ollama: ✓            │
│  codex: ✗   bridge: manual_handoff_only                │
│  openclaw: local ref only — NOT WIRED                  │
│                                                         │
│  [SAFETY STATUS]                                        │
│  cap bypass: BLOCKED | fake engagement: BLOCKED        │
│  autonomous actions: NOT IMPLEMENTED                    │
└─────────────────────────────────────────────────────────┘
```

This concept shows:
- Agent cards with real status (IDLE / RUNNING / BLOCKED / AWAITING APPROVAL)
- Approval queue as the primary control surface
- Income workflow lanes with honest "NOT ACTIVE" state
- Tooling truth with live probe results
- Safety status always visible

This is a vision for a future milestone — not current state.
