# Agent OS - PR #17 and Guard Branch Merge Strategy

Audit role: Codex-style integration review (executed by Claude Code).
Generated: 2026-06-12 (UTC).
Audit branch: `audit/ghoti-agent-os-pr17-and-guard-merge-strategy` (from `origin/main`).
Method: read-only inspection in throwaway worktrees, every reported number
re-verified locally (not trusted from prior reports).

---

## TL;DR verdicts

- **PR #17: `MERGE_PR17_NOW`** - clean, scoped, fully green, safe.
- **Guard branch: `GUARD_BRANCH_MERGE_AFTER_PR17`** (conditional) - technically
  green and safe, but it is a 90-file / +9,501-line bundle of many milestones,
  not a small permission kernel. Land it only after PR #17 and after three
  fixes (below). The fast alternative is `GUARD_BRANCH_CHERRY_PICK_ONLY` of the
  permission-kernel subset as a focused follow-up PR.
- **Recommended order: merge PR #17 first, then a slimmed/rebased guard.**

---

## 1. Current branch map (verified SHAs)

| Ref | SHA | Relationship |
|-----|-----|--------------|
| `origin/main` | `8861672` (`88616720a521647815510975dd38b4bc3d0f2616`) | base |
| PR #17 `feat/ghoti-agent-os-integrated-command-center-mvp` | `4f134dd` | main is its merge-base -> fast-forwardable |
| Guard `audit/ghoti-agent-codex-agent-os-guard-integrated-command-center-gate` | `d50950f` | **contains PR #17 as a linear ancestor** |
| Reported integration commit | `3bdcbe9` | confirmed present, ancestor of guard tip |
| Reported audit-report commit | `d50950f` | confirmed = guard tip |

Merge bases:
- `main` vs PR #17 = `8861672` (main tip) -> PR #17 is a clean descendant of main.
- PR #17 vs guard = `4f134dd` (PR #17 tip) -> **guard = PR #17 + 13 commits**.
- `main` vs guard = `8861672` -> guard is current with main.

**Dependency relationship:** linear stack `main -> PR #17 -> guard delta`.
There are **no parallel/divergent commits**, therefore **no merge conflicts by
construction** between PR #17 and the guard branch. The "two parallel branches"
framing is not the real situation; the guard branch already swallowed PR #17.

### What the guard branch adds on top of PR #17 (13 commits, +9,501 / -19, 90 files)

Genuinely new permission kernel (the valuable "next step"):
- `rust/agent_os_guard/` - new Rust crate, default-deny capability guard
  (7 allowed / 11 blocked caps, `approval_required` for `approved_local`).
- `03_scripts/agent_os/local_worker_trial.py` - approved-local-worker trial harness.
- `03_scripts/agent_os/agent_os_guard_bridge.py` - read-only status bridge.
- `03_scripts/agent_os/data_only_writer.py` - data-only write helper.
- Additive edits to PR #17's `ghoti_agent_os.py` (`--guard-status`, guard rows
  in `--check`/`--status`) and `local_worker.py` (routes writes through
  `data_only_writer`). Both additive, non-breaking.
- Tests: `test_n6_45a_agent_os_guard_local_worker_trial.py` (18),
  `test_command_center_..._gate.py`.

Bundled additional milestones (beyond a permission kernel):
- `03_scripts/context_memory/` - **second** memory-search/handoff/obsidian/context
  stack (`ghoti_local_memory_search.py` 518 lines, `ghoti_handoff_packet.py` 604,
  `ghoti_obsidian_memory_view.py` 490, `ghoti_context_memory_map.py` 434).
- `03_scripts/agent_command_center/` - **standalone** loopback command-center
  server with its own `static/` UI (separate from PR #17's dashboard panel).
- Large `14_context/memory/` tree (indexes, schemas, obsidian notes, handoff
  scaffolding) and n6.42a/b/c, 43a, 44a, 44b milestone docs/tests.

---

## 2. PR #17 verdict: MERGE_PR17_NOW

Re-verified on `4f134dd`:

| Check | Result |
|-------|--------|
| Full unittest discovery | 1,502 tests, 0 failures, 0 errors (1 known flaky env timeout in `test_n4_2a` under full-suite load; passes in isolation; untouched by PR #17) |
| Agent OS self-check | 10/10 |
| Full local demo | all 6 steps ok, evidence written |
| `cargo test` | green; release binary builds and is used by the ownership gate |
| Dashboard | `node --check` clean; all 9 endpoints verified live (200s; allowlist rejects unknown ids/terms with 400) |
| Public security audit | 0 failed checks, 0 blockers, `safe_to_make_public: true` |
| Whitespace | `git diff --check` clean |

Answers to the audit questions:
- **Mergeable as-is?** Yes.
- **Blockers?** None.
- **Misleading claims?** None found. "worker_executed" is not used in PR #17;
  the worker only writes suggestion files.
- **Real vs suggestion-only clearly distinguished?** Yes - status/labels mark
  `suggestion_only`, `simulation`, and `approved_local_action`; every packet
  carries `Human copy-paste required: YES` / `relay_mode: copy_paste_only`.
- **Browser/computer-use/accounts/money disabled?** Yes - no such capability is
  invoked; policy gate denies them.
- **Repo-local paths?** Yes - worker writes only under `14_context/agent_os/`;
  search returns `path:line` pointers, never file bodies.
- **Avoids committing generated/private evidence?** Yes - `14_context/agent_os/`
  generated subdirs are gitignored except READMEs.
- **Passes necessary tests?** Yes.

---

## 3. Guard branch verdict: GUARD_BRANCH_MERGE_AFTER_PR17 (with fixes) / CHERRY_PICK alternative

Re-verified on `d50950f` (not trusted from the prior report):

| Check | Reported | Verified |
|-------|----------|----------|
| Rust workspace tests | 30/30 | **30/30** (7 guard + 8 policy_checker + 15 runtime_core) |
| Agent OS self-check | 12/12 | consistent (PR #17's 10 + 2 guard records) |
| command center + guard + agent OS focused tests | 29/29 | `test_agent_os_command_center` + `test_n6_45a` = **40/40 ok** |
| n6.42-45 milestone tests | 111/111 | `test_n6_4*` discovery = **166/166 ok** (wider glob, all green) |
| public audit | 0 blockers | **0 failed / 0 blockers / safe** |
| live execution / browser / accounts / approved-local | disabled | **confirmed disabled** |

Safety review (the parts that matter most):
- **Rust guard kernel** (`rust/agent_os_guard/src/main.rs`): `default_deny: true`,
  `live_execution: false`, blocks account/browser/computer_use/money/... ,
  requires an approval token for `approved_local`. Tested. Sound.
- **Trial harness** (`local_worker_trial.py`): in `approved_local` mode it
  early-returns `approved_local_not_executed` and **never executes**; allow-path
  writes only repo-local drafts (plan/run/handoff); deny-path writes a denied
  run-record. `live_execution: False`, `model_output_as_command: False`
  everywhere. The only real execution is `cargo run` to get the guard decision
  (read-only) and a `node` write fallback (data-only). Sound.
- **Feature flags**: 4 new flags all `false`
  (`local_agent_command_center_enabled`, `..._live_launch_enabled`,
  `paperclip_live_company_launch_enabled`, `supervised_business_scenarios_enabled`).
  Deny-by-default preserved.
- **Guard bridge**: read-only, hardcodes `approved_local_execution_enabled: False`.

So the guard branch is **correct and safe**. The reasons it should not be
clicked-merged wholesale right now are strategic and hygiene, not correctness.

### Overlap / conflict analysis

- **Conflicts: none** (PR #17 is a linear ancestor of guard).
- **Duplication risk (real):**
  - PR #17 ships memory search via `local_worker.search_memory` (path:line
    pointers). Guard adds a **second** memory-search implementation under
    `03_scripts/context_memory/` + a `14_context/memory/` tree. Two memory
    subsystems is the exact "parallel surfaces become chaos" risk.
  - PR #17 ships the **dashboard "Agent OS" panel** (in `dashboard_mvp`).
    Guard adds a **standalone** command-center server under
    `03_scripts/agent_command_center/` with its own static UI. Two command
    centers.
- **Hygiene regression (real):** guard commits generated artifacts into dirs
  PR #17 marks gitignored/machine-owned:
  - `14_context/agent_os/handoffs/content-video-plan_handoff.md`
  - `14_context/agent_os/runs/content-video-plan_run.json`
  - `14_context/agent_os/trials/content-video-plan.md`
  - plus `14_context/memory/generated/*`, `14_context/agent_command_center/generated/*`.
  After PR #17 merges, these paths are gitignored on main; landing them as
  tracked files contradicts that decision and will drift.
- **Invariant softening (nit):** PR #17's `local_worker.py` imported no
  execution primitive. Guard routes its write through `data_only_writer`, which
  may spawn `node` as a write fallback. Still data-only, but the "worker imports
  no subprocess" guarantee becomes "worker's writer may spawn node to write a
  file." Document it; consider keeping a pure-python path as the default
  (it already is - node is only the OSError fallback).
- **Offline/consistency nit:** `local_worker_trial._invoke_guard` runs
  `cargo run` **without** `--locked --offline`. The repo's other cargo caller
  (`ghoti_computer_use_adapter.py`) pins `--locked --offline` against an approved
  manifest. Align for offline-safety and reproducibility.

### Cleanest integration strategy

Primary: **merge PR #17 now; then rebase the guard branch onto the new main and
split it.** Land the permission-kernel subset first as a focused follow-up PR:

```
rust/agent_os_guard/**                       (new crate + workspace member)
03_scripts/agent_os/local_worker_trial.py
03_scripts/agent_os/agent_os_guard_bridge.py
03_scripts/agent_os/data_only_writer.py
03_scripts/agent_os/ghoti_agent_os.py        (the +15 additive guard wiring)
03_scripts/agent_os/local_worker.py          (the data_only_writer routing)
01_projects/runtime_mvp/tests/test_n6_45a_agent_os_guard_local_worker_trial.py
01_projects/runtime_mvp/tests/test_command_center_agent_os_guard_integrated_command_center_gate.py
23_configs/ghoti_feature_flags.example.json  (4 new false flags)
docs/GHOTI_AGENT_OS_GUARD_AND_LOCAL_WORKER_TRIAL.md
```

Then handle the bundled milestones (`context_memory/`, `agent_command_center/`,
`14_context/memory/`) as a **separate reconciliation PR** that explicitly
decides: extend PR #17's memory search / dashboard panel, or replace them - not
both in parallel. Do not let two memory subsystems and two command centers land
silently.

Alternative if you want it all in one shot: `GUARD_BRANCH_MERGE_AFTER_PR17`
wholesale, but first (a) `git rm --cached` the generated artifacts in
gitignored dirs, (b) pin the cargo call `--locked --offline`, (c) add a
short note in the dedup doc that `context_memory/` supersedes (or is superseded
by) PR #17's search. Bigger review surface; same end state.

---

## 4. Recommended merge order

1. **Merge PR #17 into main** (`--no-ff`, no squash) - product surface.
2. Rebase guard onto new main; open **follow-up PR A = permission kernel**
   (subset above). Small, already-green, this is the real bridge to an approved
   local worker queue.
3. Open **follow-up PR B = memory/command-center reconciliation**, after
   deciding extend-vs-replace, with the committed-generated artifacts removed.

PR #17 **before** the guard branch: yes.

---

## 5. Blockers

- **PR #17 blockers: none.**
- **Guard branch blockers (before wholesale merge):**
  1. Generated artifacts committed into PR #17-gitignored dirs (handoffs/runs/
     trials + memory/generated + agent_command_center/generated). Remove from
     tracking or the hygiene decision in PR #17 is silently reverted.
  2. Duplicate memory-search + duplicate command-center surfaces not reconciled
     against PR #17. Decide extend-vs-replace before landing.
- **Guard branch nits:** `cargo run` not pinned `--locked --offline`; worker
  write path now reaches `node` via `data_only_writer` (document the softened
  invariant).

---

## 6. Tests run (this audit)

| Command (in throwaway worktrees) | Result |
|----------------------------------|--------|
| `cargo test --offline` (guard worktree) | 30/30 ok |
| `python -m unittest test_agent_os_command_center test_n6_45a_...` | 40/40 ok |
| `python -m unittest discover -p "test_n6_4*.py"` | 166/166 ok |
| `python 03_scripts/public_repo_security_audit.py --json` | 0 failed, 0 blockers, safe |
| `git merge-base --is-ancestor` (PR17 in guard; main in guard) | both ancestors confirmed |
| Source review: rust guard, trial harness, guard bridge, data_only_writer, feature flags, .gitignore vs committed files | safe; findings above |

---

## 7. Exact commands run (key ones)

```
git fetch origin --prune
git rev-parse origin/main origin/feat/...mvp origin/audit/...guard...gate
git merge-base origin/main origin/feat/...mvp
git merge-base origin/feat/...mvp origin/audit/...guard...gate
git merge-base --is-ancestor origin/feat/...mvp origin/audit/...guard...gate
git diff --stat origin/feat/...mvp..origin/audit/...guard...gate
git worktree add --detach <temp>/ggguard origin/audit/...guard...gate
git worktree add -b audit/ghoti-agent-os-pr17-and-guard-merge-strategy <temp>/ggaudit origin/main
(cd <temp>/ggguard/rust && cargo test --offline)
(cd <temp>/ggguard && PYTHONPATH=.../src python -m unittest discover -p "test_n6_4*.py")
(cd <temp>/ggguard && python 03_scripts/public_repo_security_audit.py --json)
```

Note: gates were run from `%LOCALAPPDATA%/Temp` worktrees because Windows
Controlled Folder Access blocks python/bash writes under `Documents`.

---

## 8. What the user should ask Claude next

> "Merge PR #17 into main with a `--no-ff` merge commit (no squash). Then rebase
> `audit/ghoti-agent-codex-agent-os-guard-integrated-command-center-gate` onto the
> new main and open a focused follow-up PR containing ONLY the permission kernel
> (`rust/agent_os_guard`, `local_worker_trial.py`, `agent_os_guard_bridge.py`,
> `data_only_writer.py`, the additive `ghoti_agent_os.py`/`local_worker.py`
> edits, the guard tests, the 4 false feature flags, the guard doc). In that PR:
> remove the generated artifacts committed under gitignored
> `14_context/agent_os/{handoffs,runs,trials}` and `14_context/memory/generated`,
> and pin the `cargo run` guard call to `--locked --offline`. Hold the
> `context_memory/` + `agent_command_center/` milestones for a separate
> reconciliation PR that decides extend-vs-replace against PR #17's existing
> memory search and dashboard panel."

---

## 9. Whether PR #17 should merge before the guard branch

**Yes - merge PR #17 first.** It is the smaller, fully-reviewed, conflict-free
product surface. The guard branch already contains it, so nothing is lost; this
just keeps the permission-kernel review separate from the product review and
prevents 9,500 lines of mixed milestones landing in one click.

---

## 10. What to do with this audit branch

`audit/ghoti-agent-os-pr17-and-guard-merge-strategy` carries only these two
reports. Keep it as the review artifact; close/delete after the user reads it
and the follow-up PRs are opened. It is **not** part of the product path.

---

## 11. Exact next implementation step toward the approved local worker queue

The permission kernel from the guard branch is exactly this bridge, but it stops
at `approved_local_not_executed`. The next concrete step after the kernel lands:

> Wire one approved workflow suggestion into the existing approval engine
> (`super_ai_agent.queue`): `worker-suggest` enqueues a single `ask`-risk task
> whose only allowlisted action is "write the approved draft"; the Rust guard
> decision plus a human click in the dashboard Approvals view (or a repo-local
> `APPROVED_ACTIONS.json` token) flips it from `approved_local_not_executed` to
> executing that one data-only write - nothing else. That turns the trial harness
> into the first genuinely approved (still non-destructive) local worker action.
