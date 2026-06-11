# Ghoti Optional Local Memory Search

This folder contains a disposable search aid for the reviewed Ghoti memory
index. It is not canonical truth and does not replace raw sources, the context
map, latest state, handoff packets, or Obsidian views.

The N+6.43A trial uses deterministic local feature hashing. It makes no semantic
embedding claim, calls no model or provider, stores no source text, and returns
only repo-relative source pointers with current SHA-256 verification.

## Commands

```powershell
python 03_scripts/context_memory/ghoti_local_memory_search.py --check --json
python 03_scripts/context_memory/ghoti_local_memory_search.py --build --json
python 03_scripts/context_memory/ghoti_local_memory_search.py --verify --json
python 03_scripts/context_memory/ghoti_local_memory_search.py --evaluate --json
python 03_scripts/context_memory/ghoti_local_memory_search.py --search "human approval" --json
python 03_scripts/context_memory/ghoti_local_memory_search.py --search "human approval" --no-index --json
```

## Safety

- Only sources already marked `summary_safe` in `raw_index.json` are indexed.
- The generated JSON index is disposable and stores vectors, paths, and hashes,
  never raw source text.
- A stale source hash makes saved-index search fail closed.
- Every result is a candidate source that requires verification.
- Removing the saved index leaves deterministic memory and direct-scan fallback
  usable.
- The fixed data-only Node writer fallback exists only for desktop profiles
  that block Python file writes; it cannot execute queries or packet content.
- No network, model, provider, account, command, or live action is available.
