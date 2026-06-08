# ECC / Ruflo / am-will/swarms / ClawTeam — Trial Plan (N+6.30A)

**Milestone:** N+6.30A
**Status:** plan only — nothing here is run, installed, or enabled
**Builds on:** `ecc_claude_swarm_profile_n6_26a.md`, `am_will_swarms_deep_intake_n6_26a.md`, `clawteam_deep_intake_n6_26a.md`

## Golden Rule (unchanged from N+6.26A)

**Never test swarm launching inside the Ghoti environment or the operator's working Claude
profile.** Use an **isolated profile** (a distinct OS user profile or disposable VM/sandbox)
with no access to the Ghoti repo, no real accounts, no secrets, no `.env`, and only a
scratch repo with junk data.

---

## Section 1 — ECC (affaan-m/ecc)

### What it is
A bundle of Claude Code commands, agents, skills, and hooks, MIT-licensed. ECC =
**E**verything **C**laude **C**ode. Adds governance/scanning patterns, AGENTS.md-style
rules, and a curated set of slash commands.

### Why useful for Ghoti
- Governance patterns (AGENTS.md, CLAUDE.md, RULES.md structure) already adopted by Ghoti.
- Security-scanner patterns complement `03_scripts/public_repo_security_audit.py`.
- Skill installation model is the right reference for adding Ghoti-native skills.
- **No live agent launching** in the governance/skill layer — safer than launchers.

### Trial plan (separate profile only)
1. In isolated profile: `git clone https://github.com/affaan-m/ecc` → read LICENSE, README,
   and all `SKILL.md` / command files before doing anything else.
2. Note every hook registered and what it runs (`~/.claude/settings.json` diff).
3. Test one skill (governance scan) on a junk repo with no real data.
4. Record: any unexpected network calls, file writes, or auto-commits.
5. Bring back only notes; never bring the executable bundle into Ghoti.

### What to adapt for Ghoti (patterns only)
- Copy the **SKILL.md format** for Ghoti-native skills.
- Copy the **governance rule structure** (already partially done in CLAUDE.md / AGENTS.md).
- Do not copy hooks, install scripts, or any executable from ECC.

### Risks
- Executable hooks wired during install touch whatever profile they land in.
- Any hook that auto-commits or pushes would affect the active repo.
- Isolation is not optional; it is the safety guarantee.

---

## Section 2 — Ruflo / Claude Flow

### Status: DEFER indefinitely
**Do not install. Do not trial. Do not use patterns from live code.**

Supply-chain history documented in `repo_intake_reports/ruflo_n6_12a.md`:
- Obfuscated malicious npm pre-install across v3.1.0-alpha.55..v3.5.2.
- MCP prompt-injection (Issue #1375): tool descriptions covertly instructed the model.
- Remediated SQL injection.

The **four safe patterns** (role-labeled agents, coordinator/worker separation, shared
local memory, declared-skill registration) have already been re-expressed from scratch in
N+6.12A's `03_scripts/external_adapters/ruflo_adapter_contract.py` with `RUFLO_SWARM_ENABLED = False`.

**Rule:** Ghoti never installs Ruflo. Any future use of Ruflo-inspired ideas uses
Ghoti-native code only.

---

## Section 3 — am-will/swarms

### What it is
Multi-agent orchestration **skills** for Claude Code and Codex. Operates through the
official skills + subagents mechanisms; no separate server required.

Key skills:
- `super-swarm` — top-level orchestration.
- `swarm-planner` — works best in Plan Mode (uses "Request User Input" tool).
- `parallel-task` — parses a plan file; delegates tasks in a rolling pool of up to
  15 concurrent subagents.

### Why useful for Ghoti
The skills-based approach is exactly Ghoti's preferred path: no heavyweight launcher,
no separate process, orchestration through officially supported mechanisms. The
wave + rolling-pool execution model maps cleanly onto Ghoti's milestone approval gates.

### What to capture
- How `swarm-planner` generates and structures the plan file.
- How `parallel-task` assigns ownership (does it use worktrees? file locks?).
- Whether it can commit / push / hit the network without human approval.
- Exact token cost of a 3-agent dry-run on a 10-file scratch repo.

### Trial plan (separate profile only)
1. Verify license (no top-level LICENSE found in N+6.27A inspection).
2. In isolated profile: install the skills following the README.
3. Run `swarm-planner` in Plan Mode on a junk plan (3 tasks, scratch repo).
4. Inspect the generated plan file before proceeding.
5. Run `parallel-task` on the plan with `max_agents: 3` (not 15) on the scratch repo.
6. Record: agent count, token cost, whether it auto-commits.
7. Bring back notes + plan file format only.

### What to adapt for Ghoti
- **Wave-based execution model** → map onto Ghoti approval gates (one human approval per wave).
- **Rolling pool pattern** → bounded concurrency with `max_parallel` in `ghoti_swarm_launcher.py`.
- **Plan file format** → extend `14_context/swarm_launcher/swarm_plan_schema.json`.

---

## Section 4 — affaan-m/claude-swarm

### What it is
Multi-agent orchestration with a terminal UI. Provides dependency-graph task decomposition,
file conflict detection, budget enforcement, quality gate (auditor role), and status/replay
for visualization.

### What to capture
- Whether it auto-commits or auto-pushes.
- How it handles file ownership conflicts (does it use worktrees?).
- Terminal UI shape → useful reference for Ghoti's Agent Arena.
- Budget enforcement mechanism → reference for Ghoti's future spend limit.

### Trial plan (separate profile only)
1. In isolated profile: `git clone https://github.com/affaan-m/claude-swarm` → read
   LICENSE, README, and source before doing anything.
2. Run on a 2-agent scratch plan (planner + builder, junk repo only).
3. Record: any auto-commit, any network call, any file outside the scratch repo.
4. Bring back only notes.

### What to adapt for Ghoti (already partially done in N+6.27A)
- Dependency graph → `swarm_plan_schema.json` `dependencies` field.
- File conflict detection → `ghoti_swarm_launcher.py` overlap detection.
- Budget enforcement → future `gates.budget_limit` field.
- Auditor role → `ghoti_swarm_launcher.py` default role set.

---

## Section 5 — ClawTeam (HKUDS/ClawTeam)

### Status: Needs full sandbox trial before any Ghoti consideration

**What it is:** One-command goal → orchestrated agent team. Local JSON state under
`~/.clawteam/`. Reported: multi-user workflows, Web UI, P2P transport, team templates.
CLI-agent-agnostic (Claude Code, Codex, Cursor compatible).

### Why caution
- "Full automation" is its explicit goal — exactly the blast-radius risk.
- Verify: does it auto-commit? auto-push? call external services?
- P2P transport means potentially network-outbound by default.
- Web UI adds a local server surface.

### Trial plan (separate profile only)
1. Read full README and source structure before any command.
2. Inspect what `~/.clawteam/` state looks like after init.
3. Run the simplest goal on a 2-agent scratch plan, junk repo, no real accounts.
4. Check what happens to git state after a run (any commits?).
5. Inspect P2P transport: does it call external nodes?
6. Bring back only notes.

### What to adapt for Ghoti
- Local-JSON-state coordination model → reference for Ghoti's own agent_lanes state.
- Team template concept → extend `14_context/agent_lanes/` lane definitions.
- **Never bring the ClawTeam binary or executable into Ghoti.**

---

## Safe Trial Order (full sequence)

Run in isolated throwaway profile, least risky → most risky:

1. **Subagents (built-in)** — already verified; continue.
2. **Skills (built-in)** — add one SKILL.md from ECC patterns; verify load.
3. **ECC governance scan skill** — in isolated profile; junk repo.
4. **am-will/swarms swarm-planner** — Plan Mode; junk repo; record plan file format.
5. **am-will/swarms parallel-task** — max 3 agents; junk repo; record cost.
6. **affaan-m/claude-swarm** — 2-agent; junk repo; record auto-commit behavior.
7. **ClawTeam** — simplest goal; junk repo; inspect state + network.
8. _(Ruflo: never)_

**Never trial agent teams, dynamic workflows, or background agents in Ghoti.** Trial
those in the isolated profile only and bring notes back.
