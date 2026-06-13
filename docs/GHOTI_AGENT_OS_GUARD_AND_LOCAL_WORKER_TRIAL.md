# Ghoti Agent OS Guard and Local Worker Trial

## Purpose

This milestone adds a small, coherent Agent OS foundation:

1. A Rust default-deny guard validates a proposed local worker request.
2. A Python harness asks the real guard for a decision.
3. Only `simulation` and `suggestion` modes may render harmless repo-local
   plans, run records, and handoffs.

The result is suggestion-only. It performs no browser control, no computer-use,
no account action, no sending or posting, no purchase, and no live agent
launch.

## Agent OS Integration Path

The run record and compact handoff are the shared memory boundary for Claude,
Codex, and Hermes. Each agent can inspect the same repo-relative evidence
without copying a large chat transcript. Hermes or a local model may summarize
the artifacts; Claude may build a separately scoped change; Codex may audit
the guard decision and evidence. The human remains the final authority.

Future swarms can propose multiple non-overlapping worker requests, but every
request must pass this guard before a launcher considers it. Future computer-use
requires additional observation, approval, target, and action
gates; it is not enabled by this milestone.

## Trust Boundary

The Rust binary reads one JSON request and prints one deterministic JSON
decision. It does not launch processes, use the network, or write files.
It validates known actions, capabilities, relative paths, locked paths,
runtime limits, and approval presence.

The Python harness invokes only the fixed repo-owned Rust guard command with an
argument list and timeout. It never treats model output as a command. A guard
allow decision permits only a local plan-rendering function. Its write helper
matches the repo's existing data-only fallback: if Python cannot write directly,
it passes base64-encoded artifact data to a fixed Node writer with no shell or
user-controlled command surface.

`approved_local` is part of the policy contract so future milestones can test
approval presence. The current harness still refuses to execute that mode.

## Commands

```powershell
$env:CARGO_TARGET_DIR = "$env:TEMP\ghoti_agent_os_guard_target"
cargo run --manifest-path rust/Cargo.toml --bin agent_os_guard -- --check --json
cargo run --manifest-path rust/Cargo.toml --bin agent_os_guard -- --request 14_context/agent_os/requests/example_worker_request.json --json
python 03_scripts/agent_os/local_worker_trial.py --check --json
python 03_scripts/agent_os/local_worker_trial.py --workflow content-video-plan --mode suggestion --json
```

## Allowed Local Trial Workflows

- coding task plan
- content/video plan
- business research plan
- email draft plan for human review
- automation plan

These create planning artifacts only. They do not execute the plan.

## Default-Deny Rules

- Unknown actions, modes, and capabilities are denied.
- Browser, computer-use, accounts, payments, purchases, posting, mass
  messaging, MCP, secrets, and external writes are denied.
- Absolute paths, parent traversal, and outputs outside
  `14_context/agent_os/` are denied.
- Locked-path overlap is denied.
- Runtime requests must stay between 1 and 120 seconds.
- Approval values are never echoed into decisions or run records.

## Token Discipline

The compact request, decision, run record, and handoff contracts avoid loading
large historical reports for every worker trial. The handoff points to the
full artifact instead of repeating it. Future local models may summarize these
artifacts, but their model output must remain data, never a command.

## What Is Not Enabled

No live workers, recursive self-training, autonomous money actions, browser
automation, OS input, account access, email sending, content posting, payment,
purchase, MCP setup, or live swarm launch is enabled.

## Next Safe Step

Connect the fixed guard and harness interfaces to the integrated command-center
branch, then add a read-only command-center view that displays guard decisions, trial
artifacts, and handoff pointers. Keep any future approved local execution
behind a separate audited milestone and explicit human approval.
