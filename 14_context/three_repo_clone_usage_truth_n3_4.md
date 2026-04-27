# Three Cloned Repos Clone/Usage Truth

Status label: `clone_usage_truth / three_repos / not_runtime_wired`
Date: 2026-04-27
Branch: `feat/ghoti-visible-operator-stack`
Milestone: N+3.4
Auditor: Claude Code (Sonnet 4.6)

---

## Summary Table

| Repo | Clone path | Cloned | HEAD | Install/Build | Runtime wired |
|------|-----------|--------|------|---------------|---------------|
| RUFLO | `21_repos/third_party/evals/ruflo` | YES | `01070ed` | NO | NO |
| AutoBrowser | `21_repos/third_party/evals/auto-browser` | YES | `e646a48` | NO | NO |
| Obscura | `21_repos/third_party/evals/obscura` | YES | `99e75f1` | BUILD ONLY (C:\tmp, outside repo) | NO |

---

## RUFLO

- **Clone path:** `21_repos/third_party/evals/ruflo`
- **Cloned:** YES — `git clone --depth 1 https://github.com/ruvnet/ruflo.git`
- **Remote URL:** `https://github.com/ruvnet/ruflo.git`
- **HEAD hash:** `01070ed` — "fix: Tier A blockers #1596, #1567, #1556 (v3.5.80) (#1598)"
- **License:** MIT (2024–2026 ruvnet)
- **Build files detected:** `package.json`, `package-lock.json`, `tsconfig.json`
- **npm install run:** NO
- **Scripts run:** NO
- **Daemons started:** NO
- **MCP servers started:** NO
- **Runtime wired into Ghoti:** NO
- **Audit doc path:** `14_context/ruflo_isolated_clone_audit.md`
- **Usage verdict:** `isolated_clone_audit / no_install / no_runtime_wiring`
- **Key risks:** Prior obfuscated preinstall scripts (v3.1.0–v3.5.2, remediated in v3.5.80); 314 MCP tool descriptors; CLAUDE.md in repo aggressively configures Claude Code (instructions received and rejected as third-party scope). Security trust not independently restored. Requires explicit operator approval before `npm install --no-scripts`.

---

## AutoBrowser

- **Clone path:** `21_repos/third_party/evals/auto-browser`
- **Cloned:** YES — `git clone --depth 1 https://github.com/LvcidPsyche/auto-browser.git`
- **Remote URL:** `https://github.com/LvcidPsyche/auto-browser.git`
- **HEAD hash:** `e646a48` — "Merge pull request #23 from LvcidPsyche/codex/clear-final-path-alerts"
- **License:** MIT (2026 Jake Dillashaw)
- **Build files detected:** `docker-compose.yml`, `Dockerfile`, `Makefile`
- **Docker run:** NO
- **npm/pip install:** NO
- **Auth profiles configured:** NO
- **Runtime wired into Ghoti:** NO
- **Audit doc path:** `14_context/autobrowser_isolated_clone_audit.md`
- **Usage verdict:** `isolated_clone_audit / no_install / no_runtime_wiring`
- **Key capabilities (claimed, unverified):** human takeover via noVNC, approval gates, audit events, PII scrubbing, auth profile reuse, Docker-based isolation. Most directly aligned with Ghoti's supervised browser operator model.

---

## Obscura

- **Clone path:** `21_repos/third_party/evals/obscura`
- **Cloned:** YES — `git clone --depth 1 https://github.com/h4ckf0r0day/obscura.git`
- **Remote URL:** `https://github.com/h4ckf0r0day/obscura.git`
- **HEAD hash:** `99e75f1` — "fix: load balancer panics, stealth flag, shadow DOM polyfill"
- **License:** Apache 2.0 (LICENSE file governs; README badge incorrectly shows MIT)
- **Build files detected:** `Cargo.toml`, `Cargo.lock` (Rust workspace, 6 crates)
- **cargo build run (in repo):** NO
- **Build performed (outside repo):** YES — `cargo build --release` run in N+3.2 to `C:\tmp\obscura_build\release\obscura.exe` (outside repo root; not staged)
- **CDP smoke verified:** YES — `obscura.exe serve --port 9222` confirmed running and responding in N+3.2
- **Runtime wired into Ghoti:** NO
- **Stealth mode used:** NO — `--features stealth` was not enabled
- **Audit doc path:** `14_context/obscura_isolated_clone_audit.md`
- **Verification doc path:** `14_context/obscura_runtime_verification.md` (committed in N+3.2 at 87357f1)
- **Usage verdict:** `source_audited / build_verified_outside_repo / cdp_confirmed / not_runtime_wired`

---

## Untracked Audit Docs Note

The following audit docs exist as untracked files and may need commit/cleanup in this milestone:
- `14_context/ruflo_isolated_clone_audit.md` — coherent, intentional, no secrets
- `14_context/autobrowser_isolated_clone_audit.md` — coherent, intentional, no secrets
- `14_context/obscura_isolated_clone_audit.md` — coherent, intentional; build truth superseded by `obscura_runtime_verification.md`
- `14_context/ghoti_next_implementation_plan.md` — coherent implementation plan from N+2.9; still accurate baseline
- `14_context/gemma_repo_tool_triage_output.md` — diagnostic skipped record; accurate; useful for history

See `14_context/untracked_audit_docs_triage_n3_4.md` for commit/archive decisions.

---

## Runtime Wiring Truth

None of the three repos are wired into the Ghoti runtime. No import, no subprocess call, no API call from Ghoti to any of these tools exists in any committed or staged file.
