# Repo Classification Summary

Last updated: 2026-04-05

## Classification table

| Repo | Purpose | Stack role | Priority | Recommendation |
| --- | --- | --- | --- | --- |
| Claw Code | coding harness / CLI agent runtime | later experiment / reference | later | study it, do not center the stack on it yet |
| OpenHarness | open Python agent harness | candidate harness layer | later | promising, but not first install |
| awesome-design-md | design-system prompts for UI generation | side design aid | optional | useful only when building UI-heavy projects |
| OpenScreen | demo and walkthrough recorder | side utility | optional | separate productivity tool, not assistant infrastructure |
| oh-my-codex | workflow layer on top of Codex | workflow helper | later | useful if Codex becomes a central daily tool |
| sherlock | username OSINT tool | side tool only | unrelated to core stack | keep separate from assistant foundation |
| RuView | WiFi sensing / pose / vitals platform | unrelated to core assistant stack | unrelated | side project only |

## Claw Code

Local repo path:

- `C:\Users\ai_sandbox\AI_Workspace\21_repos\core\claw-code` (temporary location outside the permanent workspace root)

What the repo claims:

- top README says the active Rust workspace lives in `rust/`
- later in the same README it says the repo is Python-first
- top-level docs present the repo as a claw-native coding harness

What the tree actually shows:

- substantial `rust/` workspace with 9 crates
- substantial `src/` Python tree
- only one visible GitHub Actions workflow: `rust-ci.yml`
- top-level Python `tests/` is thin
- latest local commit is in `rust/crates/runtime/src/file_ops.rs`

Current center of gravity:

- Mixed codebase
- Active implementation center looks Rust-first right now

Why:

- latest commit is Rust
- only CI workflow is Rust-focused
- `USAGE.md` is Rust CLI oriented
- `rust/README.md` presents a concrete CLI, crates, and parity harness

Classification:

- not the foundation for this sandbox today
- useful as a reference repo and later experiment
- worth studying for ideas about harness state, permissions, events, parity tests, and tool surfaces

## OpenHarness

Verified repo source:

- https://github.com/HKUDS/OpenHarness

What it claims:

- open agent harness with tools, skills, memory, permissions, and multi-agent coordination
- Python implementation
- one-command `oh` launcher
- supports CLI integrations including OpenClaw, nanobot, Cursor, and more

Why it matters:

- it is closer to a real harness candidate than most repo theater
- it is still early and should be evaluated before trust

Classification:

- later candidate for harness layer
- not first install
- worth re-evaluating after Python, GitHub, and model runtime basics are clean

## awesome-design-md

Verified repo source:

- https://github.com/VoltAgent/awesome-design-md

Purpose:

- curated `DESIGN.md` files for AI-assisted UI generation

Classification:

- optional side repo
- useful for frontend/design-heavy projects
- not core assistant infrastructure

## OpenScreen

Verified repo source:

- https://github.com/siddharthvaddem/openscreen

Purpose:

- open-source Screen Studio alternative for demos and walkthroughs

Classification:

- optional productivity tool
- separate from the assistant stack

## oh-my-codex

Verified repo source:

- https://github.com/Yeachan-Heo/oh-my-codex

Purpose:

- workflow layer on top of Codex CLI

Classification:

- optional helper
- useful only if Codex stays central in your day-to-day workflow
- not a model runtime or harness foundation by itself

## sherlock

Verified repo source:

- https://github.com/sherlock-project/sherlock

Purpose:

- username search across social networks

Classification:

- side tool only
- unrelated to the core assistant/automation stack

## RuView

Verified repo source:

- https://github.com/ruvnet/RuView

Purpose:

- WiFi-based dense pose, presence, and vitals sensing platform

Classification:

- unrelated to the core assistant stack
- only relevant as a separate sensing project later
