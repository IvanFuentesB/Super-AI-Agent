# Ghoti N+6.43A Optional Local Memory Search Trial

## Purpose

N+6.43A tests whether a small local retrieval layer improves discovery of
reviewed Ghoti memory without replacing deterministic indexes or source truth.

This is a real search trial, but not a remote vector database or model-backed
semantic embedding system. It uses a transparent deterministic feature-hash
vector over sources already approved as `summary_safe` by
`14_context/memory/index/raw_index.json`.

## Truth Boundary

- Raw and durable source files remain authoritative.
- The context map, latest state, handoffs, and Obsidian pages remain usable when
  the search index is absent.
- Search results are candidate source pointers, not claims of truth.
- Every result includes the indexed SHA-256, current SHA-256, and verification
  status.
- A stale source or raw index makes saved-index search fail closed.
- No result is promoted automatically into current state or agent instructions.

## Trial Engine

`deterministic_local_feature_hash_v1` maps normalized content terms into a
256-dimension sparse vector. The generated index stores vectors and source
metadata only. It does not store source text.

The engine is useful for proving the retrieval contract and measuring content
discovery against a path-only baseline. It does not claim deep semantic
understanding. A future local embedding model may replace the trial engine only
after a separate safety, privacy, quality, and resource audit.

## Retrieval Evaluation

The sanitized fixture asks four source-discovery questions whose answer terms
do not appear in the expected file paths. The trial compares:

1. Content-vector retrieval from reviewed safe sources.
2. A path-only lookup baseline.

The evaluation passes only when content retrieval reaches the fixed minimum hit
rate and beats the path-only baseline.

## Safety And Privacy

- The retrieval engine is local-only and Python-standard-library-only.
- If this desktop profile blocks Python file writes, `--build` uses the same
  fixed-argv, stdin-data-only Node writer pattern as the existing memory tools.
  It has no query, command, shell, exec, spawn, or eval surface.
- No network, provider, API credential, or paid dependency.
- No private or ignored files.
- No source marked metadata-only or unsafe enters the search index.
- No source text is copied into the index.
- No browser, computer-use, account, money, posting, or live-agent action.
- No model-output-to-command loop.
- Queries containing private paths or secret-like values are rejected.
- Generated search files are disposable and noncanonical.

## Files

- `03_scripts/context_memory/ghoti_local_memory_search.py`
- `23_configs/context_memory_search.example.json`
- `14_context/memory/search/README.md`
- `14_context/memory/search/fixtures/sanitized_search_eval.json`
- `14_context/memory/search/generated/local_search_index.json`
- `14_context/memory/search/generated/evaluation_result.json`
- `01_projects/runtime_mvp/tests/test_n6_43a_local_memory_search.py`

## Done Criteria

- Content retrieval measurably beats path-only lookup on the sanitized fixture.
- Results include repo-relative source paths and current verified hashes.
- Saved-index search fails closed on stale evidence.
- Direct-scan fallback works without a saved search index.
- N+6.42 deterministic memory remains independently usable.
- Public security and focused memory tests pass.

## Next Milestone

N+6.43B should integrate reviewed search entry points into operator-facing
status surfaces and audit whether retrieval actually reduces agent context
loading. It must keep search optional, local, source-linked, and noncanonical.
