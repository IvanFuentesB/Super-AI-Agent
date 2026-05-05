# N+3.44b Next Sequence Lock

Status: sequence recommendation.
Date: 2026-05-05

## Gate Result

Controlled parallel is allowed for a tiny pilot after this audit commit is pushed.

This does not approve uncontrolled parallel execution. It only approves the first branch-isolated, lock-declared, no-live-action pilot.

## Next Step

The user may run a Claude lane and a Codex lane in parallel only using lane locks and separate branches.

Recommended next Claude:

```text
N+3.45A - Agent Lane Dashboard Read Card
```

Recommended next Codex:

```text
N+3.45B - External Tool Routing Source-Check Pack
```

Recommended Gemma:

```text
N+3.45C - Compact Summary Draft Dry-Run Only
```

Recommended ChatGPT:

```text
Prepare both prompts and oversee merge strategy.
```

## Required Ordering

1. Create or dry-run lane locks before work.
2. Use separate branches.
3. Ensure no overlapping write paths.
4. Run each lane's validation.
5. Merge one branch at a time.
6. Update state docs from one designated owner after merges.

## No External Tool Integrations Yet

Do not connect or run:

- JobSpy
- Firecrawl
- Glif
- Chrome DevTools MCP
- OpenClaw
- Paperclip
- Ruflo
- CUA
- agentcy-agents
- SalesMaxAI
- connector accounts
- live accounts

These remain source-check/research-gated.

## If The Pilot Fails

Stop parallel work and run a focused recovery milestone:

```text
N+3.45R - Agent Lane Pilot Recovery And Lock Hardening
```

Likely fixes:

- validate all path-list fields in `agent_lane_status.py`
- add a release-lock/status convenience command
- align dashboard paths in shared-file lock policy
- strengthen merge checklist with branch comparison commands

## Future Milestone Recommendation

After a successful pilot:

```text
N+3.46 - Agent Lane Dashboard Read View Audit And Parallel Pilot Retrospective
```

Then consider source/integration planning for OpenClaw, Paperclip, Ruflo, CUA, JobSpy, and content/channel tooling.
