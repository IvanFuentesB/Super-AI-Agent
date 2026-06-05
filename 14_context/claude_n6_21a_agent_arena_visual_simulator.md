# Ghoti N+6.21A — Agent Arena Visual Simulator (Report)

## Summary

N+6.21A ships the first **visual simulator** where the user can watch Ghoti
agents/swarms work - as a simulation, before any live overnight automation. It reuses
the N+6.18A operator dashboard pattern (a Python standard-library server bound to the
loopback interface, serving a static page plus read-only GET JSON endpoints) and
renders a sample simulation: agent cards for the six roles, a queue/timeline, task
states, branch/worktree per agent, simulated token/cost estimates, handoff files, and
a replay trace.

```
powershell -ExecutionPolicy Bypass -File 03_scripts/agent_arena/start_agent_arena.ps1
# then open http://127.0.0.1:8766/
```

## Verdict

IMPLEMENTED_AND_PUSHED. (Amended to fix the Codex loopback-only blocker - see below.)

## Loopback-only fix (Codex N+6.21A blocker)

Codex BLOCKED the first cut because `ghoti_agent_arena.py` exposed an external-bind
escape hatch (`--allow-nonlocal-host` / the `allow_nonlocal_host` parameter). It is
removed entirely:

- The `--allow-nonlocal-host` CLI flag and the `allow_nonlocal_host` parameter are
  **deleted**; `serve()` takes only `host` and `port`.
- Host handling is now `_normalize_loopback(host)`: it returns `127.0.0.1` for
  `127.0.0.1`/`localhost`, `::1` for `::1`, and **None (refuse) for everything else** -
  `0.0.0.0`, other `127.x.x.x`, hostnames, and public IPs. There is no opt-in.
- `serve()` refuses any non-loopback host (`ok:false`, `external_bind_possible:false`,
  exit code 2) **before** binding, and binds only the normalized loopback address.
- `--check` now reports `no_external_bind_capability:true` and
  `loopback_only_enforced:true`. New tests prove `0.0.0.0` (and other externals) are
  refused, that `serve` has no `allow_nonlocal_host` parameter, and that the source
  carries no `allow_nonlocal` token. The schema and doc truth claims were corrected.

## Branch / worktree / base / dependency

- Branch: `feat/ghoti-agent-claude-n6-21a-agent-arena-visual-simulator`
- Commit message: `feat(ghoti): add agent arena visual simulator`
- Worktree: `C:\Users\ai_sandbox\Documents\AI_Managed_Only\.claude\worktrees\n6_21a_agent_arena_visual_simulator`
- Base `origin/main`: `e126fb2` ("docs(ghoti): record n6.20b approved-window paste merge gate")

**Dependency / sync:** the branch was first created from `origin/main 733bd8e`. During
this lane **N+6.20B was merged to main** (`662126c` feat -> `35c07bc` merge ->
`e126fb2` merge-gate). The branch was then **fast-forwarded cleanly onto
`origin/main e126fb2`** (`733bd8e` is an ancestor; no rebase conflicts, no history
rewrite) while preserving all already-written Agent Arena work. The Agent Arena is
net-new and reuses the **N+6.18A operator dashboard pattern** (already on main), not
the N+6.20A harness; there are **no duplicate files** (no `agent_arena` existed on
main). Validation was re-run after the sync.

## Skills / plugins

- **Detected (Claude Code):** project `ghoti-status`, `goal`, `prompt-bus`,
  `ultraplan`; `anthropic-skills:*`; built-ins (`verify`, `code-review`,
  `security-review`, ...). ECC/everything-claude-code is **not** an installed Claude
  Code plugin here.
- **Used:** `ghoti-status` (git state / lane locks - no N6 conflict) and
  `anthropic-skills:karpathy-guidelines` (surgical, minimal, simple; drove reusing the
  proven N+6.18A pattern and dropping subprocess entirely so the arena is even safer).
- **Ignored:** UI/UX-framework, doc-format, and live-action skills (irrelevant; would
  breach the simulation-only rule).

## Files

New files (12):

- `docs/GHOTI_N6_21A_AGENT_ARENA_VISUAL_SIMULATOR.md`
- `14_context/agent_arena/README.md`
- `14_context/agent_arena/sample_simulation.json`
- `14_context/agent_arena/agent_arena_schema.json`
- `03_scripts/agent_arena/ghoti_agent_arena.py`
- `03_scripts/agent_arena/check_agent_arena.ps1`
- `03_scripts/agent_arena/start_agent_arena.ps1`
- `03_scripts/agent_arena/static/index.html`
- `03_scripts/agent_arena/static/app.js`
- `03_scripts/agent_arena/static/styles.css`
- `01_projects/runtime_mvp/tests/test_n6_21a_agent_arena_visual_simulator.py`
- `14_context/claude_n6_21a_agent_arena_visual_simulator.md` (this report)

No config edit was needed; the arena reads the existing flags and treats absent
arena flags as `false`.

## Useful commands

```
python 03_scripts/agent_arena/ghoti_agent_arena.py --check --json
python 03_scripts/agent_arena/ghoti_agent_arena.py --simulation-json
powershell -ExecutionPolicy Bypass -File 03_scripts/agent_arena/check_agent_arena.ps1
powershell -ExecutionPolicy Bypass -File 03_scripts/agent_arena/start_agent_arena.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File 03_scripts/agent_arena/start_agent_arena.ps1
```

## Dashboard URL

<http://127.0.0.1:8766/> (loopback only).

## Validation

- `python ... test_n6_21a_...py` → **29 tests, 29 pass** (including 5 new tests that
  prove external binds are impossible after the loopback-only fix).
- Full n6 suite (`unittest discover -p "test_n6_*.py"`) → **365 tests**; the only
  non-pass results are pre-existing/environmental in files this lane did not touch: the
  known `test_n6_14a` broken-PATH-`python`-shim check, and a flaky `test_n6_15a`
  `--use-gemma-if-available` status-brain timeout that only appears when the local
  gemma/ollama model is loaded (it did not recur on the post-fix run). Neither is an
  N+6.21A regression; the N+6.21A tests are 29/29.
- `ghoti_agent_arena.py --check --json` → `ok: true`; `--simulation-json` →
  `live_execution: false`, six agents covering all five states. PowerShell
  `check_agent_arena.ps1` → `ok: true` (`only_status_commands_flag_enabled` true);
  `start_agent_arena.ps1 -DryRun` → simulation-only, opens nothing, starts nothing.
- Live smoke (real `--serve` on `127.0.0.1:8766`, plus an in-process loopback server in
  the tests) → all GET endpoints `200 ok`, unknown path `404`, `POST /api/simulation`
  rejected (`501`), `live_execution: false`, server stopped cleanly.
- `public_repo_security_audit.py --run --json` → `failed_checks: 0`,
  `safe_to_make_public: true`.
- `ghoti_product_launcher.py --status / --context-pack / --repo-map --json` → all
  `ok: true`.
- `git diff --check` → clean.
- Generated residue restored (the context-pack / repo-map output and the N+6.16A
  status-bridge log produced during the suite); only the 12 new files remain.

## What remains disabled

Live agent launch, Claude/Codex/Hermes automation, auto-submit, command execution,
process start/stop, runtime-config mutation, merge/push, unattended swarm, MCP, live
browser/computer-use, OS input, account login, email/WhatsApp, Docker, and external
API are all disabled. The arena binds `127.0.0.1` only, exposes no POST route, makes no
subprocess call, and reads no secret. `live_execution` is forced `false` in every
payload. The arena feature flags are absent/`false`; only
`telegram_status_commands_enabled` is true globally.

## Future Tool Intake v2

N+6.22A must run a **Tool Intake v2** pass that classifies the newly added backlog into
six lanes:

- **coding brain / code graph**
- **agent skills / swarms**
- **automation / money**
- **documents / content**
- **apps / products**
- **APIs / model routing**

Explicit **Tier 1** items to classify and triage in N+6.22A:

- Paperclip
- Understand-Anything
- Ruflo
- gstack
- Obsidian-skills
- Stop / Stop skill
- dynamic code graph / Git Nexus / CodeGraph
- n8n / Composio / Apify / Firecrawl / Browserbase
- MarkItDown / StirlingPDF / Surya OCR / Tesseract
- Kimi + Claude swarms research

Each item stays **source-needed / static-inspect-first**: no install, no execution, and
no live action until it passes the N+6.19A allowlisted sandbox gates. The Agent Arena
can later visualize these candidates as **simulated** swarms before any live run.

## Codex audit target branch

`audit/ghoti-agent-codex-n6-21a-agent-arena-visual-simulator`
