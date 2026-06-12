# N+6.42B Shared Agent Handoffs Evidence

## Scope

- Branch: `feat/ghoti-agent-codex-n6-42b-shared-agent-handoffs`
- Dependency branch: `feat/ghoti-agent-codex-n6-42a-context-memory-map`
- Dependency commit: `1739402a3a69364f3d7c42d31ec5fc47058b31fb`
- Implementation commit: `e392843456654f3896544f2673f196354d9252bd`
- Main remained unchanged at: `70755c89de926d4cf6a9083858287351757673ba`
- Next milestone: N+6.42C Obsidian Vault Setup

N+6.42B adds a validated shared handoff contract for Claude, Codex, Hermes, ChatGPT, and local models. Agents can publish immutable evidence packets to their own outbox and deliver hash-linked read-only pointers to another agent's inbox.

## Implemented Contract

- Required packet fields include agent, branch, task, touched files, command evidence, test results, blockers, next action, timestamp, hashes, and safety posture.
- Packet IDs are sender-owned and immutable after publication.
- Unknown top-level and safety fields are rejected.
- Private absolute paths, secret-like values, traversal paths, malformed hashes, oversized packets, and unsafe safety flags are rejected.
- Packet source and artifact hashes are verified against current repo-local files before CLI publication.
- Hash mismatches mark evidence stale.
- Commands are labeled evidence only and are never executed.
- Delivery writes a read-only pointer containing the source packet path and SHA-256 hash.
- The handoff index detects packet or delivery tampering.
- Markdown handoffs are ASCII-safe and bounded to 1,200 words.
- JSON packets are bounded to 65,536 bytes.

## Real Handoff Proof

The committed example flow was executed through the new CLI:

1. Validated current source and artifact hashes.
2. Published `codex-20260611-n6-42b-example` to the Codex outbox.
3. Delivered a read-only pointer to the Hermes inbox.
4. Rebuilt and verified the handoff index.

Current committed handoff state:

- Published packets: 1
- Inbox deliveries: 1
- Verified indexed items: 2
- Index mismatches: 0
- Executes commands: false
- Network/model/live actions used: false

## N+6.42A Hardening

N+6.42B found and fixed a cross-worktree determinism issue in the N+6.42A raw index. Filesystem checkout mtimes are no longer recorded as generated truth. Identical source content now produces identical indexes across worktrees, while the source-state SHA-256 remains the freshness authority.

## Token-Saving Effect

Main token drains addressed:

- repeated full milestone reports pasted between agents
- repeated command and test history
- broad context scans to find the latest handoff
- stale handoffs that cannot prove their source state

The packet contract replaces those drains with bounded summaries, repo-relative evidence pointers, and hashes. Capable models can load the compact packet first and open detailed sources only when required. Local models may later summarize reviewed packets, but may not promote truth or execute commands.

Expected savings are workload-dependent. The immediate structural win is that routine handoffs are capped at 1,200 Markdown words instead of requiring full conversation or terminal-history replay.

## Validation

Focused validation:

- N+6.42A tests: 13 OK
- N+6.42B tests: 15 OK
- Handoff `--check`: passed
- Handoff `--verify`: passed, 2 verified items, 0 mismatches
- Example evidence verification: passed, 3 current hashes
- Context memory `--check`: passed
- Context memory `--verify`: passed, 15 verified sources
- Context map: 213 words
- Latest state: 284 words
- Public security audit: 150 checks, 0 failed, 0 blockers, 8 warnings
- Launcher status: passed
- Context pack: passed
- Repo map: passed
- `git diff --check`: passed
- Generated context-pack and repo-map residue: restored

The full N+6 suite ran 976 tests with 4 failures, 6 errors, and 23 skips. No N+6.42A or N+6.42B test failed. The ten failures/errors are the known desktop permission-profile repo-write baseline:

- N+6.0A local model evaluation output write
- N+6.14A external-resource probe fixture write
- N+6.19A clipboard fixture write
- N+6.1A routing demo output write
- N+6.2A manual bridge runtime fixture and guide writes
- N+6.15A status handoff write
- N+6.16A Hermes handoff write
- N+6.19A generated static-scan report write
- N+6.25A inside-repo status packet write

The N+6.42B writer handles this environment through a fixed-argument, data-only Node fallback. It passes only deterministic base64 file content, never packet commands, never a shell string, and never a live action.

## Safety Verdict

FEATURE READY / LOCAL SHARED HANDOFF CONTRACT VERIFIED

No network, provider, model, account, browser, computer-use, money, posting, live-agent launch, auto-submit, or model-output-to-command capability was added. Human approval remains required for risky or live actions.

N+6.42C should generate Obsidian-friendly views over these indexes and packets without creating a second source of truth or committing private Obsidian workspace state.
