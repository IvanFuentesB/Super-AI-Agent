# Codex: AGENTS.md vs Codex Skills (N+6.24A)

Milestone: N+6.24A
Date: 2026-06-06
Status: guidance-only static notes. Codex stays manual and audit-only for Ghoti; nothing
here auto-wires Codex into a runtime.

Codex (the auditor lane) has its own equivalents of the four building blocks. The two
most important to get right are `AGENTS.md` and Codex skills, because they are easy to
conflate.

## AGENTS.md

- **What:** a repo-level instructions file Codex reads to understand the project - the
  Codex-facing counterpart of `CLAUDE.md`. It states conventions, how to build/test, and
  the rules of the road.
- **Nature:** **guidance/config, not executable.** It tells the agent how to behave; it
  runs nothing by itself.
- **Ghoti use:** an `AGENTS.md` was added in N+6.20A as the Codex-facing rule surface. It
  encodes the same safety model (no live actions, no secret reads, audit-not-implement).
- **Scope:** repo-wide guidance. A nested `AGENTS.md` can refine rules for a subtree.

## Codex skills

- **What:** reusable capabilities/prompts Codex can apply (the Codex analogue of a skill).
  Less standardized than Claude's `SKILL.md`; treat as a prompt/recipe layer.
- **Nature:** instructions/recipes; like skills elsewhere, a skill is not new permissions.
- **Ghoti use:** the audit recipe in `codex_working_rules.md` plus
  `docs/CODEX_AUDIT_WORKFLOW.md` are Ghoti's effective "Codex skill": compare branch vs
  `main`, read the real diff, re-run validation, flag overclaims, record a verdict.

## AGENTS.md vs Codex skills (the distinction)

| | AGENTS.md | Codex skill |
|---|---|---|
| Role | project rules/config Codex reads | a reusable recipe/prompt Codex applies |
| Granularity | repo or subtree | a specific task pattern (for example "audit a PR") |
| Analogy | `CLAUDE.md` | a `SKILL.md` |
| Executes code? | no | no (it is instructions) |
| Ghoti status | present (N+6.20A), guidance | audit workflow, manual |

## The Codex skill agent-launching pattern (the swarm angle)

The forward-looking idea the operator flagged: a **Codex skill that can launch/coordinate
other agents**, not just review. In that pattern a skill encodes "spin up a worker on
this sub-task, collect its output, gate it" - i.e. Codex (or a coordinator) acts as a
swarm conductor.

For Ghoti this is **planned and gated**:

- Today Codex is audit-only and **does not** implement, merge, launch, or coordinate live
  agents.
- An agent-launching skill is the same risk surface as the controlled-launcher stage in
  the safe progression; it requires a separate, audited, human-approved milestone and a
  dry-run-first design (print the command it would run, then stop).
- The candidate references for this pattern are recorded in
  `../tool_intake/swarm_launcher_repo_intake_n6_24a.md` with `source_needed: true` where
  no verified source exists. No source is fabricated.

## Hard limits (unchanged)

Codex does not merge to `main`, does not enable automation, does not install repos, does
not run live actions, and does not read or write secrets/`.env`/tokens/cookies. The
handoff to and from Codex is manual.
