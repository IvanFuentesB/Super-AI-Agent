# Repo Inspiration / Attribution Report (N+6.27A)

Milestone: N+6.27A
Date: 2026-06-06
Status: repo-backed, dry-run only. Structured data: `repo_inspiration_manifest_n6_27a.json`.

The Ghoti dry-run swarm launcher is **original code** that re-expresses public design
patterns from inspected repos. **No third-party code is vendored or committed.** The repos
were shallow-cloned into the **gitignored** sandbox `21_repos/third_party_runtime_sandbox/`
for **read-only LICENSE/README inspection only** - not installed, not executed, contents
never committed.

## What was inspected (read-only)

| Repo | License | Verified | What we read |
|------|---------|----------|--------------|
| `am-will/swarms` | no top-level LICENSE file | no | README.md, skills/ names |
| `HKUDS/ClawTeam` | MIT (c) 2025 HKUDS | yes | LICENSE, README.md, top-level |
| `affaan-m/claude-swarm` | MIT (c) 2026 Affaan Mustafa | yes | LICENSE, README.md |
| `affaan-m/ecc` | MIT (c) 2026 Affaan Mustafa | yes | LICENSE, top-level |

## What was adapted (patterns, not code)

- **am-will/swarms** -> explicit per-task dependencies that drive **parallel waves**; the
  orchestrator that plans also coordinates; each worker is told exactly which files it owns.
  (License unverified -> **patterns only, no code reuse**.)
- **affaan-m/claude-swarm** -> decompose into a dependency graph; **file conflict
  detection** (our overlap detection); **budget enforcement**; a quality gate (auditor);
  status/replay shaped for visualization (Agent Arena).
- **HKUDS/ClawTeam** -> one-command goal to an orchestrated team; named roles;
  CLI-agent-agnostic membership; local, file-based state.
- **affaan-m/ecc** -> the AGENTS.md/CLAUDE.md/RULES.md governance structure and
  security-scanner patterns (Ghoti already has equivalents). ECC = Everything Claude Code.

## What was NOT done

- No third-party code copied into committed source.
- No repo installed; no dependencies installed; no scripts run; nothing executed.
- No repo contents committed (the sandbox is gitignored).
- No hooks enabled; no agents launched.

## Rust toolchain status

No inspected repo had a `Cargo.toml`. **Rust is not required and was not installed.** The
Ghoti launcher is pure Python standard library.

## License posture

Three repos are MIT (ClawTeam, claude-swarm, ecc); one (am-will/swarms) had no top-level
LICENSE file, so it is treated as **patterns-only with no code reuse** until the operator
confirms its license. Because Ghoti re-expressed patterns rather than copying snippets, no
copyright notice needs to travel with the launcher in this milestone; any future small
snippet reuse from an MIT repo would carry its notice.
