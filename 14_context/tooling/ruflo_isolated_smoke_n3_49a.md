# Ruflo Isolated Smoke Inspection — N+3.49A

Generated: 2026-05-06
Branch: feat/ghoti-agent-claude-n3-49-local-orchestrator-ruflo-smoke
Deliverable: N+3.49A-E
Method: Read-only inspection via `ghoti_local_orchestrator.py --ruflo-check`

---

## Inspection Results

### Path

```
21_repos/third_party/evals/ruflo/
```

Exists: YES (read-only reference intake)

### Git HEAD

```
01070ed
```

### Package Identity

```json
{
  "name": "claude-flow",
  "version": "3.5.80"
}
```

Aliases: `claude-flow`, `ruflo` (umbrella), `@claude-flow/cli`

### npm Scripts Present

```
dev, build, build:ts, test, test:ui, test:security, lint,
security:audit, security:fix, security:test,
v3:domains, v3:swarm, v3:security
```

### Lifecycle Scripts

**NONE** — no `preinstall`, `postinstall`, or `prepare` scripts detected.

Safe to install with: `npm install --ignore-scripts` (inside ruflo dir only).

### node_modules Status

NOT INSTALLED — clean directory, no npm deps present.

### Wiring to Ghoti Runtime

NOT WIRED. Ruflo is in `21_repos/third_party/evals/` (read-only intake).
No import paths, no subprocess calls to ruflo from any Ghoti script.

---

## Safety Assessment

| Check | Result |
|---|---|
| No lifecycle scripts | PASS |
| node_modules absent | PASS |
| No Ghoti runtime wiring | PASS |
| Read-only intake directory | PASS |
| No credentials or secrets | PASS |

**Verdict: Safe for isolated `npm install --ignore-scripts` if user approves.**

---

## Next Steps (Require User Approval)

1. `cd 21_repos/third_party/evals/ruflo && npm install --ignore-scripts`
2. Inspect installed modules, run `npx claude-flow@v3alpha doctor` (read-only)
3. Do NOT wire ruflo to Ghoti runtime without a dedicated safety review session

---

## Ruflo Capability Summary (from CLAUDE.md)

- 6,000+ commits, 314 MCP tools, 16 agent roles + custom types
- 4-step intelligence pipeline: RETRIEVE → JUDGE → DISTILL → CONSOLIDATE
- HNSW search: 150x–12,500x faster than linear
- Dual-mode orchestration: Claude Code + Codex workers in parallel
- Lifecycle hooks: 17 hooks + 12 background workers

**Use case for Ghoti**: Ruflo could serve as the swarm orchestration layer for
multi-agent Ghoti tasks. Current Ghoti capability for this: ~60%. Ruflo wiring
would push toward ~80% if safety gate is satisfied.
