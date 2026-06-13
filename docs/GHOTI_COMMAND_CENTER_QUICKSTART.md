# Ghoti Command Center -- 5-Minute Quickstart

**Status:** Working local MVP (supervised, deny-by-default)
**Prerequisites:** Python >= 3.11, this repo checked out. Nothing else.

---

## Summary

This is the fastest honest tour of the Ghoti Agent OS. Every command below is
real and working today: each one runs locally, writes only repo-local files
under `14_context/agent_os/` (or nothing at all), and launches no agent. The
dashboard and the CLI are two views of the same command center; use whichever
you prefer. All workflow output is `suggestion_only` - a human reviews and
runs every live step.

## 1. Open the dashboard (optional, ~1 minute)

```bash
python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard
```

The dashboard serves at `http://127.0.0.1:3210` (localhost only). Click
**Agent OS** in the left nav for the new panel: integrated status, workflow
templates, task-wave previews, and memory search.

## 2. See the integrated status

```bash
python 03_scripts/agent_os/ghoti_agent_os.py --status --json
```

One JSON snapshot: git truth, recipe availability, compact memory and context
pack state, Obsidian vault note count, handoff buses, lane locks, the Ollama
probe (never pulls models), worker mode, and the safety flags.

The launcher exposes the same snapshot:

```bash
python 03_scripts/ghoti_product_launcher.py --agent-os-status --json
```

## 3. Explore workflows and plans

```bash
# the 7 templates plus the 6-role roster
python 03_scripts/agent_os/ghoti_agent_os.py --list-workflows --json

# write a plan packet (policy-gated; lands in 14_context/agent_os/workflows/)
python 03_scripts/agent_os/ghoti_agent_os.py --plan-workflow content-video --json

# preview deterministic task waves (no role or file-ownership overlap per wave)
python 03_scripts/agent_os/ghoti_agent_os.py --task-wave coding-task --json
```

## 4. Worker suggestions and handoffs (suggestion_only)

```bash
# the worker reads memory + a template and writes a proposal; executes nothing
python 03_scripts/agent_os/ghoti_agent_os.py --worker-suggest content-video --json

# copy-paste packets for Claude, Codex, and Hermes (relay_mode: copy_paste_only)
python 03_scripts/agent_os/ghoti_agent_os.py --build-handoff --workflow coding-task --json
```

Packets land in `14_context/agent_os/handoffs/` and all carry
`Human copy-paste required: YES`. Nothing is sent anywhere.

## 5. Search memory and verify ownership

```bash
# compact path:line pointers from verified local markdown (never file bodies)
python 03_scripts/agent_os/ghoti_agent_os.py --search-memory <term> --json

# prove no two roles own the same path prefix (Rust checker when built,
# Python mirror otherwise)
python 03_scripts/agent_os/ghoti_agent_os.py --ownership-check --json
```

## 6. Self-check and full demo

```bash
# 10 self-checks: policy gate denies blocked capabilities, writes outside
# agent_os are refused, the worker has no execution primitives, and more
python 03_scripts/agent_os/ghoti_agent_os.py --check --json

# one command, end to end: status + check + search + plan + suggest + handoff
python 03_scripts/agent_os/ghoti_agent_os.py --full-demo --json
```

The full demo writes its evidence to
`14_context/agent_os/evidence/full_local_demo_<ts>.md` and a matching `.json`,
listing every step result and every artifact created.

## Command reference

| Command | What it does | Writes |
|---------|--------------|--------|
| `--status --json` | Integrated status snapshot | nothing |
| `--list-workflows --json` | 7 templates + 6 roles | nothing |
| `--plan-workflow <id> --json` | Policy-gated plan packet | `workflows/` |
| `--task-wave <id> --json` | Deterministic wave preview | nothing |
| `--worker-suggest <id> --json` | Suggestion-only proposal | `handoffs/` |
| `--build-handoff --workflow <id> --json` | Copy-paste packets | `handoffs/` |
| `--search-memory <term> --json` | path:line pointers | nothing |
| `--ownership-check --json` | Overlap verdict | `runs/` (input file) |
| `--check --json` | 10 self-checks | `runs/` (probe file) |
| `--full-demo --json` | All of the above in sequence | `evidence/` |

All write targets are under `14_context/agent_os/`.

## Known environment issue (Windows)

Windows Controlled Folder Access can block Python writes under `Documents`,
producing phantom `FileNotFoundError`s. Run gates from a scratch worktree
outside `Documents`, for example:

```bash
git worktree add --detach %TEMP%/ghoti_gate <ref>
```

Then run the commands above from that worktree.

## What this quickstart did not do

No agents launched, no accounts touched, no network calls beyond the
localhost Ollama probe, no writes outside `14_context/agent_os/`. That is the
design, not a limitation of the demo.
