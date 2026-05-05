# N+3.44 Parallel Task Split Recommendation

Status: Codex recommendation only.
Date: 2026-05-05

## Current Readiness

N+3.43 lane scaffolding is missing, so the split below is a future pilot recommendation only.

Do not run multiple writing agents in parallel until lane locks exist.

## Recommended Split After N+3.43

### Claude Lane

Lane:

```text
implementation-only
```

Best next small task after locks:

```text
A. Agent Lane Dashboard Read Card
```

Scope:

- read lane lock/status files
- show active locks
- show stale status beacons
- show branch and write scope
- read-only dashboard card
- no mutation buttons
- no external agents launched

Why:

- low-risk
- validates lane files visibly
- helps humans coordinate future parallel work

### Codex Lane

Lane:

```text
audit/source-check/docs-only
```

Best next task:

```text
B. Source-check OpenClaw/Paperclip/Ruflo/CUA/JobSpy
```

Scope:

- official/source research
- risk matrix
- install/connect verdicts
- sandbox requirements
- approval gates
- no installs/clones/runs

Why:

- independent from Claude dashboard work
- no shared runtime files
- helps choose future integrations safely

### Gemma Lane

Lane:

```text
local summary/compression only
```

Best next task:

```text
C. Compress N+3.18-N+3.43 into compact_memory drafts
```

Scope:

- use local docs only
- produce draft artifacts
- no canonical overwrite
- mark unknowns
- preserve source paths

Why:

- reduces Claude/Codex prompt size
- supports memory durability
- cheap local work

### ChatGPT Lane

Lane:

```text
strategy and prompts only
```

Best next task:

```text
D. Prepare next prompt set
```

Scope:

- plan next milestone prompts
- clarify priorities
- create prompt variants
- no repo truth claims without local audit

Why:

- keeps strategy moving without touching repo files

## Candidate Task Options

### Option A: Claude Implements Read-Only Agent Lane Dashboard Card

Priority: soon after N+3.43.

Requirements:

- N+3.43 lane files exist and parse.
- dashboard route/card reads only.
- no launch/execute buttons.
- no external agents.

### Option B: Codex Source-Checks OpenClaw/Paperclip/Ruflo/CUA/JobSpy

Priority: soon after N+3.43 or alongside Option A only if locks exist.

Requirements:

- Codex branch only.
- docs only.
- source links.
- no installs, clones, runs, scraping, connectors, accounts.

### Option C: Gemma Compresses N+3.18-N+3.43 Into Compact Memory Drafts

Priority: soon, but after lane lock scaffolding.

Requirements:

- draft output only.
- human/Codex review before canonical promotion.
- no invented commit hashes, validation, revenue, or tool status.

### Option D: ChatGPT Prepares Next Prompt Set

Priority: anytime.

Requirements:

- use latest Codex audit summaries.
- avoid claiming repo state without local source.
- keep approval gates in prompts.

## Recommended First Split

After N+3.43 exists:

1. Claude: Agent Lane Dashboard Read Card.
2. Codex: narrow source-check pack for OpenClaw/Paperclip/Ruflo/CUA/JobSpy.
3. Gemma: draft compact memory compression artifact.
4. ChatGPT: next prompt set.

But merge only one branch at a time.
