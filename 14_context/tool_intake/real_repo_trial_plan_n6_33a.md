# Real Repo Trial Plan (N+6.33A)

**Milestone:** N+6.33A
**Status:** plan only — nothing here is installed, run, or enabled by this milestone
**Builds on:** `cua_ui_tars_computer_use_trial_plan_n6_30a.md`,
`ecc_ruflo_swarm_trial_plan_n6_30a.md`, `am_will_swarms_deep_intake_n6_26a.md`,
`claude_swarm_surfaces_n6_26a.md`

## Golden rule (unchanged)

**Never trial a real computer-use engine or swarm launcher inside the Ghoti
environment or the operator's working Claude profile.** Use an isolated profile
(distinct OS user / disposable VM / sandbox) with no Ghoti repo access, no real
accounts, no secrets, no `.env`, and only a scratch repo with junk data.

The N+6.33A bridge does not change this. It adds a *second policy gate* in front
of any future engine, so a plan must clear both the adapter and the policy
checker before it could ever be handed to a real engine in a later audited
milestone.

---

## Ordered trial sequence

The order is deliberate: cheapest/safest isolation first, install-script-heavy
and multi-agent tools last.

### 1. CUA — first isolated computer-use engine trial

- **Repo:** `https://github.com/trycua/cua` (MIT). Static-inspected in N+6.12A.
- **Why first:** it already matches the adapter's action-intent contract
  (declared type/target/value, sandbox boundary, capability declaration,
  approval gate). The N+6.33A dual gate maps cleanly onto it.
- **Trial (isolated profile only):**
  1. Clone into the scratch profile; read `LICENSE`, `README`, the sandbox docs.
  2. Run CUA's own sandbox demo against a **local fixture** only — no external
     URL, no account, no real OS target outside the sandbox.
  3. Capture a CUA action-intent payload; feed it through
     `ghoti_computer_use_adapter.py --plan <p> --rust-bridge` and confirm the
     dual gate `accepted`/blocked decision matches expectations.
  4. Do **not** enable Docker/QEMU/KASM, real OS input, or remote desktop.
- **Promotion gate:** a separate audited milestone, human approval, dual-gate
  green, sandbox-only target.

### 2. am-will/swarms OR claude-swarm — first Claude swarm trial

- **Repos:** `https://github.com/am-will/swarms`,
  `https://github.com/parruda/claude-swarm` (see N+6.26A intakes for surfaces).
- **Why before Ruflo/ECC:** these are the most direct Claude-swarm references
  and have the smallest install surface for a read-only coordinator/worker trial.
- **Trial (isolated profile only):**
  1. Clone into scratch profile; read `LICENSE`, `README`, the launch entrypoint.
  2. Map the coordinator/worker plan shape onto the policy checker's plan shape
     (`dry_run`, `live_launch`, `requires_human_approval`, `capabilities`).
  3. Run a **dry-run / plan-render only** pass — no real agent launch, no
     network, no accounts.
  4. Confirm `ghoti_policy_checker --input <plan.json>` denies any plan with
     `live_launch: true` or a blocked capability.
- **Promotion gate:** separate audited milestone; live launching stays out of the
  Ghoti environment permanently.

### 3. Ruflo — later, after install-script review

- **Repo:** `https://github.com/...ruflo` (MIT; see N+6.30A trial plan).
- **Why later:** Ruflo carries install scripts that must be read line-by-line
  before any execution. Defer until after CUA and the swarm trial are understood.
- **Trial:** read every install/setup script first; only then, in the isolated
  profile, run the coordinator/worker plan **render** with no live launch.

### 4. ECC — only in a separate Claude profile first

- **Repo:** `https://github.com/affaan-m/ecc` (MIT; "Everything Claude Code").
- **Why last / separate profile:** ECC ships hooks, skills, and slash commands.
  Hooks must never be enabled in the operator's working profile.
- **Trial:** clone into a **separate** Claude profile; review hooks/skills as
  text only. Do **not** enable hooks. Governance/scanner patterns may inform
  Ghoti, but no ECC code is copied into this repo.

---

## DeepSeek provider-routing plan

**Status:** research-only lane (extends `model_provider_lane_n6_22a.md`). No API
keys, no live calls in this milestone.

- **Intent:** route **cheap background summaries** and wide low-stakes passes to a
  cheap long-context provider (DeepSeek, newest / V4-like); reserve premium
  (Claude) for high-stakes synthesis and final answers.
- **Pattern:** the existing `apis_model_routing` lane — DeepSeek for breadth,
  Claude for depth — guarded by the Rust policy checker for any plan that would
  carry an action.
- **Hard guards:**
  - **No secrets / private content** is sent to any external provider until the
    operator explicitly approves, in the same turn, for a specific task.
  - No API keys committed; routing config stays research-only / placeholder.
  - Background summaries operate on **non-sensitive, repo-local** text only by
    default; anything touching credentials, health, accounts, or private paths
    is blocked until approved.
  - Source repo for the specific DeepSeek model/routing code is
    `needs_verification` (org page `github.com/deepseek-ai` known); no URL is
    guessed here.
- **Next step (future milestone):** a dry-run router that picks a provider per
  task tier and logs the choice, with zero live calls until keys are approved.

---

## Safety invariants (all candidates)

- Plan-only. No install, no launch, no live computer-use, no Docker, no hooks.
- Isolated profile / scratch repo for any actual trial — never the Ghoti repo.
- The N+6.33A dual gate (adapter + policy checker) must be green before any plan
  could be promoted toward a real engine, and promotion always needs a separate
  audited milestone plus human approval.
- No third-party code is committed to this repo; repos are referenced by URL.
- No secrets, tokens, cookies, or private paths in any committed file.
