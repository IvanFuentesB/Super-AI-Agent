# N+6.42A Context Memory Map Evidence

## Scope

- Branch: `feat/ghoti-agent-codex-n6-42a-context-memory-map`
- Starting main: `70755c89de926d4cf6a9083858287351757673ba`
- Feature commit: `9f3f4055008996482aebf47833601bb086a34b2a`
- Next milestone: N+6.42B Shared Agent Handoff Inbox/Outbox

N+6.42A adds a deterministic, repo-local context memory map over a reviewed allowlist of existing durable files. It does not migrate, delete, or overwrite source memory. Generated outputs are compact navigation layers, not canonical truth.

## Outputs

- `14_context/memory/index/raw_index.json`
- `14_context/memory/generated/context_map.md`
- `14_context/memory/generated/latest_state.md`
- `14_context/memory/schemas/raw_index.schema.json`

The current index covers 15 reviewed sources. Its source-state SHA-256 is:

`69aec46b66da6e93bbf2426ae4853bc527a780e97e61ef492a9ecb09f5c4e13c`

Every indexed record uses a repo-relative path and SHA-256 hash. Unsafe content is represented as metadata-only and is not copied into generated summaries. Excerpts are labeled review-required rather than current or canonical truth.

## Safety

- Local only: true
- Source files read only: true
- Network used: false
- Model/provider used: false
- Live actions enabled: false
- Secrets or private absolute paths added: none
- Model-output-to-command path: none
- Raw source deletion or overwrite path: none

The generator restricts writes to `14_context/memory`. In this Codex desktop permission profile, Python cannot create or replace repo files directly, so the implementation uses the repo's existing fixed-argument Node write fallback. The fallback receives only deterministic base64 content, does not invoke a shell, and cannot run arbitrary commands.

## Validation

Focused and adjacent checks:

- N+6.42A tests: 13 OK
- N+6.30A tests: 36 OK
- N+6.38A tests: 61 OK
- Context memory `--check`: passed
- Context memory `--write`: passed
- Context memory `--verify`: passed with no mismatches
- Launcher status: passed
- Context pack: passed
- Repo map: passed
- Public security audit: 150 checks, 0 failed, 0 blockers, 8 warnings
- Public security audit `safe_to_make_public`: true
- `git diff --check`: passed
- `git show --check --stat`: passed
- Generated validation residue: restored

The full N+6 suite ran 961 tests with 5 failures, 6 errors, and 23 skips. None are N+6.42A failures. The 11 failures/errors are pre-existing or environmental repo-write failures under this Codex desktop permission profile:

- N+6.0A local model evaluation run-file write
- N+6.14A target fixture write
- N+6.19A clipboard relay dry-run fixture
- N+6.1A routing demo output write
- N+6.2A Hermes manual bridge guide and dashboard fixture writes
- N+6.10C inherited-head attribution check before the clean feature commit; the post-commit public audit passes
- N+6.15A handoff write
- N+6.16A Hermes handoff write
- N+6.19A static-scan generated output
- N+6.25A inside-repo write

`py_compile` also could not create `03_scripts/context_memory/__pycache__` under this desktop permission profile. The module imports successfully and all N+6.42A tests pass.

## Result

N+6.42A is feature-ready and safe to push for review. It gives future agents a small source-linked startup map while preserving reviewed durable files as truth. N+6.42B should add validated, append-only agent handoff inbox/outbox packets without command execution or live-agent launch.
