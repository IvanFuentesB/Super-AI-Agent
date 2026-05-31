# N+6.7A - Tool/Repo Intake Static Registry (run report)

Lane: implementation specialist (Claude Code). Codex audits next; a human merges.
Date: 2026-05-31

## Branch / base

- Branch: `feat/ghoti-agent-claude-n6-7a-tool-intake-static-registry`
- Worktree: `.claude/worktrees/n6_7a_tool_intake_registry` (repo-contained, isolated)
- Base `main`: `67eb4a5` - `docs(ghoti): record n6.4b main merge gate` (N+6.4B).
- Pushed: feature branch only. `main` not touched.
- Independent branch (from `origin/main`), so it can run in parallel with N+6.6A.

## Start condition (verified)

- `origin/main` is at N+6.4B (`67eb4a5`); the foundation is present on main
  (`14_context/ghoti_current_truth.md`, `14_context/codex_n6_4b_main_merge_gate.md`,
  `14_context/agent_handoff_vault/`).
- Reference branches inspected read-only: `origin/feat/...n6-5a-...observation-harness`
  (`a71c892`), `origin/feat/...n6-6a-hermes-router-wrappers` (`0f5dd5c`), and
  `origin/plan/ghoti-n6-6-7-8-command-center-architecture` (`68c0894`). The planning
  branch's `docs/GHOTI_N6_7_TOOL_REPO_INTAKE_SPEC.md` informed the candidate set.
- No N+6.5A harness files and no N+6.6A Hermes router wrapper files were touched.

## What was built (7 files, all new)

Intake registry (`14_context/tool_intake/`):
- `tool_candidate_registry.json` - 23 candidates (8 HIGH, 9 MEDIUM, 6 BLOCKED),
  each with `status` (`candidate_only`/`blocked`), `installed:false`,
  `runtime_wired:false`, risk, safe intake method, first safe test, stop
  conditions, and allowed/forbidden-now lists; plus a top-level `global_safety`
  block and the 10-step intake pipeline.
- `tool_intake_decision_log.md` - append-only human-readable decision per candidate.
- `README_TOOL_INTAKE.md` - inspect -> classify -> sandbox -> integrate; no blind installs.

CLI (`03_scripts/`):
- `tool_intake_static_registry.py` - stdlib-only, read-only; loads + validates the
  registry and prints a JSON summary (`--json`), a tier listing (`--list`), or one
  candidate (`--candidate`). Installs/clones/fetches/runs nothing; no network.

Doc + test + report:
- `docs/GHOTI_N6_7A_TOOL_INTAKE_STATIC_REGISTRY.md`
- `01_projects/runtime_mvp/tests/test_n6_7a_tool_intake_static_registry.py`
- `14_context/claude_n6_7a_tool_intake_static_registry.md` (this report)

## Candidate summary

| Tier | Count | Examples |
|------|-------|----------|
| HIGH | 8 | Understand-Anything, MarkItDown, Graphify, UI-TARS (observation only), Browser Harness, 21st.dev / design skills, Graph MCP (read-only later), Security Checklists |
| MEDIUM | 9 | Vercel agent-browser, FigMirror, OpenVid, YOLOv12, Meta SAM, Frigate, Pi-hole, OpenWA, Postiz |
| BLOCKED | 6 | social posting, live browser/desktop control, money/payment, account login, unknown binaries, OSINT/Kali |

By status: 17 `candidate_only`, 6 `blocked`. `any_installed=false`,
`any_runtime_wired=false`.

## Safety model enforced

- **No blind installs.** No candidate is installed or wired in; the registry
  installs nothing. No external repo is cloned or run; no external code executed.
- **Read-only CLI.** The script is stdlib-only and makes no outbound network call.
  A static scan test asserts it contains no `requests`/`httpx`/`urllib`/`socket`/
  `subprocess`/`os.system`/`git clone`/`pip install`/`npm install`/`winget` token.
- **Validator invariants.** The CLI rejects any registry whose candidate declares
  `installed:true` or `runtime_wired:true`, and exits non-zero on bad JSON or a
  missing candidate (proven by tests).
- **Not enabled.** MCP, browser-use, computer-use, and Telegram are not enabled.
  No N+6.5A or N+6.6A files were touched.

## Validation (real output)

| Check | Result |
|-------|--------|
| `test_n6_7a_tool_intake_static_registry` | 19 passed |
| `unittest discover -p "test_n6_*.py"` | **49 passed** (30 pre-existing + 19 new), 0 failures |
| `--json` summary | `ok=true`, 23 candidates (8 high / 9 medium / 6 blocked), `any_installed=false`, `any_runtime_wired=false` |
| `--list` / `--candidate "MarkItDown"` | both `rc=0`, correct output |
| Missing candidate / invalid JSON / missing file | `rc=2` (non-zero) each |
| `installed:true` / `runtime_wired:true` registry | rejected, `rc=2` |
| `git diff --check` | clean |
| `public_repo_security_audit.py --run --json` | total 150, passed 143, **failed 0**, warnings 7, `safe_to_make_public=true` |
| Generated residue | none (launcher context-pack/repo-map not run); only the 7 intended files committed |

## Direct answers

- Are any candidates installed? **No** - all are `candidate_only` or `blocked`,
  `installed:false`.
- Is anything wired into the runtime? **No** - `runtime_wired:false` on every candidate.
- Did Ghoti clone or run any external repo? **No.**
- Did Ghoti install anything? **No.**
- Is MCP / browser-use / computer-use / Telegram enabled? **No.**
- Were the N+6.5A harness or N+6.6A router wrapper files touched? **No.**
- Is `main` touched? **No.**

## What is explicitly NOT enabled

- No external repo clone/install/run. No external code execution.
- No MCP. No browser/computer-use. No Telegram.
- No autonomous agent launch. No live account/API/posting/money action. No secrets.
- `main` is untouched. No N+6.5A / N+6.6A files were modified.

## What Codex should audit next

1. Every candidate is `candidate_only` or `blocked`, with `installed:false` and
   `runtime_wired:false`; the registry lists documented candidates only.
2. The CLI installs/clones/fetches/runs nothing and makes no network call.
3. The blocked tier names the dangerous boundaries (social posting, live
   browser/desktop, money, account login, unknown binary, OSINT/Kali).
4. No doc overclaims MCP/browser-use/computer-use/Telegram/autonomy.
5. The change is registry + decision log + README + CLI + doc + test only, and is
   trivially revertable.

## Verdict

IMPLEMENTED_AND_PUSHED (feature branch only). The safe, static tool/repo intake
registry exists with tests; nothing was installed, cloned, executed, wired, or
otherwise enabled.
