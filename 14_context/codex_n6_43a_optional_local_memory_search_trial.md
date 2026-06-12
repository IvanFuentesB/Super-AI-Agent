# N+6.43A Optional Local Memory Search Trial

## Verdict

CLEAN PASS / N+6.43A OPTIONAL LOCAL MEMORY SEARCH TRIAL READY

## Branch And Dependency

- Branch: `feat/ghoti-agent-codex-n6-43a-optional-local-memory-search-trial`
- Starting dependency: `origin/feat/ghoti-agent-codex-n6-42c-obsidian-memory-view`
- Starting commit: `15e7159f4d7a29a78e7e689cf8f49b97bc76eb44`
- Implementation commit: `3f8101d5a18684ce1e7e9755a5aa5412e45af1dd`
- Worktree placeholder: `<repo>/.claude/worktrees/n6_43a_local_memory_search`
- `origin/main` was not changed.

## Outcome

N+6.43A adds a real, optional, local retrieval trial on top of the reviewed
N+6.42 memory index.

The search layer:

- indexes only the 12 sources already marked `summary_safe`
- keeps all source files read-only
- stores no raw source text
- returns repo-relative paths plus indexed and current SHA-256 hashes
- fails closed when saved-index evidence is stale
- supports a direct-scan fallback when the saved index is absent
- remains disposable and explicitly noncanonical

The engine is `deterministic_local_feature_hash_v1`: a transparent local
256-dimension feature-hash vector plus opaque exact-term fingerprints. It makes
no deep-semantic or model-embedding claim.

## Measured Retrieval Result

Sanitized fixed fixture:

- Queries: 4
- Top-k: 3
- Content search hits: 4/4
- Content search hit rate: 1.00
- Path-only baseline hits: 1/4
- Path-only baseline hit rate: 0.25
- Measured improvement: 0.75
- Measurable improvement gate: passed

The generated index is one compact JSON line and 40,911 bytes, below the
100,000-byte enforced budget. The human-facing evaluation remains formatted and
reviewable.

## Truth And Safety Boundary

- Raw sources, deterministic indexes, handoffs, and reviewed durable files
  remain authoritative.
- Search results are candidate source pointers, never claims of truth.
- Saved-index search verifies current hashes before returning results.
- Queries containing private paths, secret-like values, or oversized input are
  rejected.
- Metadata-only or unsafe sources never enter the search index.
- Removing the saved index loses no source truth and does not break N+6.42.
- No network, provider, remote embedding, model, browser, computer-use, account,
  money, posting, live-agent, or automatic truth-promotion action is available.
- The desktop write fallback is fixed-argv and stdin-data-only. It has no query,
  packet-command, shell, exec, spawn, or eval surface.

## Validation

Focused memory tests:

- N+6.42A Context Memory Map: 14 OK
- N+6.42B Shared Agent Handoffs: 16 OK
- N+6.42C Obsidian Memory View: 14 OK
- N+6.43A Optional Local Memory Search Trial: 17 OK
- Total focused memory tests: 61 OK

Search checks:

- `--check`: passed
- `--build`: passed
- `--verify`: passed; 12 source hashes current
- `--evaluate`: passed; 1.00 versus 0.25 top-k hit rate
- saved-index search: passed
- no-index direct scan: passed
- stale-index rejection: passed
- Python compile: passed using a temporary pycache location
- JSON validation: passed
- `git diff --check`: passed

Product and security checks:

- Launcher status: passed
- Context pack: passed; generated residue restored
- Repo map: passed; generated residue restored
- Public security audit: 150 checks, 0 blockers, 8 baseline warnings
- Real local path and prohibited attribution scan: no findings

Broad N+6 suite:

- 1,009 tests run
- 4 failures, 6 errors, 23 skipped
- No N+6.42A/B/C or N+6.43A failures
- The ten failures/errors are the same desktop permission-profile write issues
  previously recorded: N+6.0A evaluation output, N+6.14A browser fixture,
  N+6.19A clipboard fixture, N+6.1A routing output, two N+6.2A runtime/guide
  writes, N+6.15A status handoff, N+6.16A Hermes handoff, N+6.19A generated
  scan report, and N+6.25A status packet write.
- Full log stayed outside the repo at `<temp>/ghoti_n6_43a_full_n6.log`.

## Token And Credit Effect

Agents can now issue a short local query and receive a small ranked set of
verified source pointers instead of scanning or pasting broad memory folders.
The saved index contains no source text, stays below a strict size budget, and
can be bypassed with deterministic direct scan. Paid models remain reserved for
high-value reasoning and review, while local deterministic retrieval handles
source discovery.

## Skills Applied

- Isolated-worktree workflow kept the dirty primary checkout untouched.
- Test-driven development exposed missing paths, retrieval ranking, Windows
  write constraints, path canonicalization, and index bloat before commit.
- Token-saving audit reduced the generated index from 145,975 bytes and 4,751
  lines to 40,911 bytes and one line.
- Verification-before-completion required focused, product, security, and broad
  suite evidence before this verdict.

## What Remains Disabled

- Remote vector databases and remote embedding providers
- Local model-backed semantic embeddings
- Automatic search-result promotion into truth or agent instructions
- Indexing private, ignored, metadata-only, or unreviewed files
- Network calls, live agents, browser/computer-use, account actions, email,
  posting, money actions, auto-submit, or destructive actions

## Next Milestone

N+6.43B - Local Search Integration And Review Gate.

The next lane should add reviewed search entry points to operator-facing status
surfaces, measure how many source files and words agents avoid loading, and keep
the search layer optional, local, source-linked, disposable, and noncanonical.
