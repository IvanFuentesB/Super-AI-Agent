# Ghoti LLM Council — Tooling Reference — N+3.61A

## What This Is

A local-first Karpathy-style LLM Council scaffold. Inspired by the karpathy/llm-council
architecture but implemented as a Ghoti-native Python script with no external API calls
by default and full human approval gating.

This is a scaffold, not a production council app. It demonstrates the 3-stage flow and
provides extension points for later customization.

## 3-Stage Council Flow

### Stage 1: First Opinions

Each council member independently answers the question from their assigned role perspective.
No member sees another's response at this stage.

Roles in default config:
- pragmatist — focuses on immediate, actionable recommendations
- critic — challenges assumptions, surfaces risks and edge cases
- synthesizer — integrates multiple perspectives into balance

### Stage 2: Anonymous Peer Review

All Stage 1 responses are presented as Response A, B, C (no member identity visible).
Each response is scored against ranking criteria: accuracy, clarity, safety, actionability.
A ranking summary is produced. The label-to-member mapping is stored in session metadata only.

This stage ensures that synthesis in Stage 3 is based on response quality, not authority.

### Stage 3: Chairman Synthesis

The chairman reads the anonymized ranking and all responses, then produces a final answer.
Minority opinions are preserved in the session record. The chairman does not overwrite
the Stage 2 ranking — it supplements it with a synthesized recommendation.

## Provider Modes

| Mode | Requires | Default | Description |
|------|----------|---------|-------------|
| local_demo | nothing | YES | Deterministic placeholders; proves flow without any model |
| ollama_local | Ollama + model | no | Local inference; degrades gracefully if unavailable |
| openrouter_external | config flag + env var | DISABLED | Refused stub; TODO for later authorized use |

## Safety Invariants

These flags are always present in session output and must never be removed:

- LOCAL_ONLY_BY_DEFAULT
- NO_AUTONOMOUS_ACTIONS
- HUMAN_REVIEW_REQUIRED
- EXTERNAL_CALLS_DISABLED_BY_DEFAULT

## CLI Reference

```
python 03_scripts/llm_council_runner.py --status
python 03_scripts/llm_council_runner.py --demo --dry-run
python 03_scripts/llm_council_runner.py --ask "question" --dry-run
python 03_scripts/llm_council_runner.py --ask "question" --apply
python 03_scripts/llm_council_runner.py --list-sessions
python 03_scripts/llm_council_runner.py --show-session SESSION_ID
python 03_scripts/llm_council_runner.py --from-file PATH --dry-run
python 03_scripts/llm_council_runner.py --config PATH --ask "question" --dry-run
```

## Customization Guide

### Adding Council Members

In `23_configs/llm_council.example.json`, add an entry to `council_members`:
```json
{"id": "member_d", "role": "ethicist", "model": "local_demo", "description": "..."}
```

### Changing the Chairman

Set `chairman_member` to the `id` of a council member (or any identifier for a future
external model).

### Changing Ranking Criteria

Update `ranking_criteria` list. Criteria are applied in Stage 2 peer review.

### Synthesis Policy

The chairman currently produces a free-form synthesis. Future: add a structured template
(pros/cons, recommendation, confidence, minority note).

### Disagreement Handling

When council members strongly disagree, the Stage 2 ranking surfaces this as low consensus.
The chairman synthesis preserves the minority view. Operator decides how to weight it.

### Cost Controls

- local_demo: zero cost (no model)
- ollama_local: local compute only
- openrouter_external: disabled by default; when enabled, cost depends on model/token count

### Rate Limits

Not applicable in local_demo or ollama_local mode. Future external integration should add
per-session rate limiting and token budget enforcement.

### Provider Routing

Set `default_provider_mode` in config. Current valid values:
- `local_demo`
- `ollama_local`
- `openrouter_external` (disabled stub)

## Why This Fits Ghoti

- AI council / router pattern: multiple perspectives before a single recommendation
- Human approval gates: Stage 3 output is advisory, not executed autonomously
- Local-first memory: sessions stored in 05_logs/, not sent to external services
- Provider-swappable: local_demo -> ollama_local -> future external, via config only
- No autonomous live actions: the council never posts, emails, pays, or trades
