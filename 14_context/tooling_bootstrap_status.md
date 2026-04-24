# Tooling Bootstrap Status

Milestone: N+1.5 Safe Tooling Bootstrap + Bridge Proof + OpenClaw Prep
Date: 2026-04-24
Branch: feat/ghoti-visible-operator-stack

---

## Safe Installed Now

| Tool | Version / Path | Notes |
|------|---------------|-------|
| Rust (rustup) | 1.29.0 via winget | Installed this milestone. Binaries at `~/.cargo/bin/`. Not yet in bash PATH; use full Windows path or Windows terminal. |
| Node.js | v22.16.0 | Already present |
| npm | 10.9.2 | Already present |
| corepack | 0.32.0 | Already present |
| pnpm | 10.33.0 | Already present (via corepack) |
| Python | 3.13.12 | Already present |
| uv | 0.11.3 | Already present |
| Ollama | 0.21.2 | Already present |
| GitHub CLI (gh) | 2.89.0 | Already present |
| Claude CLI | found at npm/claude | Already present |
| git | system | Already present |

---

## Missing Now

| Tool | Notes |
|------|-------|
| codex CLI | Not found; `where codex` returns nothing |
| Claude skills folder | `~/.claude/skills/` does not exist |
| rustc/cargo in PATH | Binaries exist at `~/.cargo/bin/` but bash PATH not refreshed; use Windows terminal or full path |

---

## Checked Only (Not Installed)

| Tool | Check Result |
|------|-------------|
| OpenClaw | Folders present: `21_repos/third_party/openclaw` AND `21_repos/third_party/OpenClaw` (same content). Not wired, not installed into runtime. |
| Claude skills repos | Not found at `~/.claude/skills/`. Check Anthropic GitHub separately. |
| Docker | Not checked this milestone |
| Gemma models | Ollama installed; no Gemma model pull authorized this milestone |
| Postiz | External service; not installed |
| Scrapling | Not installed; future legal research reference |
| TensorTrade | Not installed; paper trading/simulation reference only |
| KaloData / Atlas AI | External services; not installed |
| Arcads / Seedance / Higgsfield | External services; not installed |
| Chrome DevTools MCP | Not installed; future reference |
| Sentinel MCP / security MCPs | Not installed; future reference |
| Figma/design tooling | Not installed locally |
| Trellis.2 | Not installed; Windows feasibility TBD |
| LightningPixel/Moldy | Not installed; future reference |
| cloth.mjs | Not installed; future reference |
| understand-anything | Not installed; future reference |
| SpiderFoot | Not installed; future legal/authorized-use reference |
| Metagoofil | Not installed; future reference |
| Hudson Rock / IntelX / WiGLE | External services; not installed |
| Anubis / Shannon repos | Not installed; future reference |

---

## Deferred / Blocked

| Item | Status |
|------|--------|
| Ollama model pulls (LLaVA, Gemma, etc.) | Deferred — not this milestone; explicit confirmation required |
| OpenClaw install / wiring | Deferred — future research only, needs WSL2 + explicit setup |
| Codex CLI install | Deferred — check-only this milestone |
| Claude Code cap/quota bypass | **Blocked permanently** |
| Phone farm automation | **Blocked permanently** |
| Fake engagement | **Blocked permanently** |
| Autonomous real-money trading/investing | **Blocked permanently** |
| Permit/legal filing automation | **Blocked permanently** |
| Weapon/guided rocket implementation | **Blocked permanently** |
| Autonomous computer control | **Blocked** — not implemented, approval gates intact |

---

## Rust Status

- **Installed this milestone:** YES
- **Method:** `winget install --id Rustlang.Rustup -e` (version 1.29.0)
- **Binaries available:** `~/.cargo/bin/rustc.exe`, `~/.cargo/bin/cargo.exe`
- **In bash PATH:** NO (Windows bash session does not auto-refresh PATH)
- **To use in Windows terminal:** `rustc --version` should work after new shell session
- **To use in bash:** `~/.cargo/bin/rustc.exe --version`
- **Next step:** Verify `rustc --version` in a fresh Windows terminal before any Rust project work

---

## OpenClaw Status

- **Local folders:** FOUND — both `21_repos/third_party/openclaw` and `21_repos/third_party/OpenClaw` exist (identical content)
- **What it is:** Personal AI assistant framework — connects to messaging channels (WhatsApp, Telegram, Slack, Discord, etc.), runs locally, multi-platform
- **Stack:** TypeScript/Node.js monorepo, Docker-based setup, apps for Android/iOS/macOS/shared
- **Preferred setup path:** `openclaw onboard` via CLI (WSL2 strongly recommended on Windows)
- **Wired to Ghoti:** NO
- **Not installed/running:** Correct — this is read-only reference in `21_repos/third_party/`
- **Plan:** See `14_context/openclaw_local_multi_agent_plan.md`

---

## Anthropic Skills Status

- **`~/.claude/skills/` folder:** NOT FOUND
- **`.claude/skills/` in project:** Present as untracked directory (not committed content)
- **Anthropic GitHub skills repos:** Not cloned or verified this milestone
- **Action needed:** Manual check of Anthropic GitHub for official skills repos

---

## Money / Content Tooling Status

| Tool | Status |
|------|--------|
| Postiz | Not installed — future social scheduling reference |
| Arcads | External service — not installed |
| Seedance 2.0 | External service — not installed |
| Higgsfield | External service — not installed |
| Whop clipping | Manual workflow only — not automated |
| Faceless channel automation | Not automated — research direction only |
| Shopify AI toolkit | Not installed — future reference |

---

## OSINT / Security Status

| Tool | Status |
|------|--------|
| SpiderFoot | Not installed — future authorized-use reference |
| Metagoofil | Not installed — future reference |
| Hudson Rock | External service — future reference |
| IntelX | External service — future reference |
| WiGLE | External/web service — future reference |
| Scrapling | Not installed — future legal scraping reference |
| Shannon repo | Not installed — future security reference |
| Anubis | Not installed — future defense reference |
| Chrome DevTools MCP | Not installed — future reference |
| Sentinel MCP v2 | Not installed — future reference |

All OSINT/scraping workflows require legal review and explicit authorization before any use.

---

## Production Web Architecture Reminders

Any serious web product deployed at scale requires all of the following:

| Layer | Component |
|-------|-----------|
| Edge | Load balancer (nginx, HAProxy, AWS ALB, Cloudflare) |
| CDN | Static asset delivery + DDoS mitigation |
| App server | API server / application layer |
| Database | Primary DB (Postgres, MySQL) + read replicas |
| Cache | Redis / Memcached for session and hot data |
| Object storage | S3 / R2 / GCS for media, uploads, backups |
| Background jobs | Queue (BullMQ, SQS, Celery) + worker processes |
| Auth / sessions | JWT or session tokens, OAuth2, MFA |
| Secrets / env | Vault, Doppler, AWS Secrets Manager — never commit secrets |
| Monitoring / logging | Grafana + Prometheus, Datadog, Sentry, structured logs |
| Rate limits / abuse | Per-IP and per-user throttling, bot detection |
| Backups / migrations | Automated DB backups, tested restore, schema versioning |
| CI/CD | GitHub Actions / GitLab CI — automated lint, test, deploy |
| Security headers | CSP, HSTS, X-Frame-Options, input validation, OWASP top 10 |

Nothing in Ghoti's current dashboard MVP has these production layers. This reminder is here to prevent premature "production" claims.
