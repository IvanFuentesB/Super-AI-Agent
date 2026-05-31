# Karpathy Guidelines — Ghoti Intake

Milestone: N+6.4A
Date: 2026-05-31
Source: external "karpathy-guidelines" skill - behavioral guardrails derived
from Andrej Karpathy's observations on common LLM coding pitfalls. Adopted as
guidance-only (see `ghoti_skill_registry.md`). No code from the skill is wired
into a runtime.

These four principles apply to every Ghoti coding task, especially Claude Code's
implementation lane.

## Principle 1 — Think Before Coding

State assumptions explicitly. If intent is unclear or multiple valid readings
exist, surface them instead of silently guessing. If a simpler approach exists,
say so. Avoid the anti-pattern of implementing the wrong interpretation at length.

## Principle 2 — Simplicity First

Write the minimum code that solves the stated problem. No speculative features,
no abstractions for single-use code, no unrequested configurability, no error
handling for impossible cases. If it can be smaller without losing correctness,
make it smaller.

## Principle 3 — Surgical Changes

Touch only what the task requires. Do not "improve" adjacent code, comments, or
formatting that is not broken. Match the existing style. Remove only the orphans
your own change created; mention pre-existing dead code rather than deleting it.

## Principle 4 — Goal-Driven Execution

Turn imperative tasks into verifiable goals before coding. Prefer
"write a test that reproduces the bug, then make it pass" over "fix the bug."
For multi-step work, state a short plan with a verification check per step, then
loop until verified.

## Quick self-check before delivering

- Did I state assumptions or ask when uncertain?
- Is this the simplest solution that satisfies the request?
- Does every changed line trace to the request?
- Did I define a verifiable success criterion?

## Ghoti adaptation notes

- These guidelines bias toward caution over speed; for trivial one-line fixes,
  use judgment.
- In Ghoti they reinforce existing rules: minimal necessary changes, one task
  per branch, and validation before commit.
- They do not grant new permissions and do not enable any automation.
