# Swarm Launcher Repo Intake (N+6.24A)

Milestone: N+6.24A
Date: 2026-06-06
Status: static intake and planning only. No repo is cloned, installed, executed, or
launched. The structured data is in `swarm_launcher_repo_intake_n6_24a.json`.

## Purpose

Map real candidate repos/patterns for an eventual **swarm launcher** - a coordinator that
**launches and coordinates** Claude/Codex/local-worker agents on real tasks - and record
new backlog items. Swarms are not just the Agent Arena visualization; the target is
controlled launching, gated behind a separate, audited, human-approved milestone.

## Sourcing rules (honest intake)

- No URL is fabricated. A URL appears only when it is already verified in prior repo
  intake or is confidently known.
- Anything unverified is `source_needed: true` with `source_url: null`.
- Operator-provided repo handles (for example `am-will/swarms`, `tw93/Pake`) are kept as
  plain strings in `operator_handle` and still require verification.
- No clone, no install, no run, no API keys, no live launches, no MCP, no executable hooks.

## Swarm-launcher candidates

| Candidate | Kind | Source status | Gate |
|-----------|------|---------------|------|
| ClawTeam | swarm orchestrator | source_needed (no URL) | tier1 static inspect |
| swarms (handle `am-will/swarms`) | swarm framework | needs_verification (handle only) | tier1 static inspect |
| multiswarm-style worktree orchestrator | concept lane | source_needed | tier1 static inspect |
| ECC multi-agent / commands | pattern reference | prior intake URL (re-verify) | tier1 static inspect |
| Claude Code team / subagent patterns | pattern reference | needs_verification (doc URL) | tier1 static inspect |
| Codex skill agent-launching | pattern reference | source_needed | tier1 static inspect |
| Existing backlog coordinators | backlog reference | reuse N+6.22A entries | tier1 static inspect |

Notes:

- **ClawTeam / am-will/swarms / multiswarm:** orchestrators that run many agents. A
  well-known multi-agent "swarms" framework exists under a different owner; do **not**
  assume the operator's handle points to it. Verify owner/repo/license first.
- **ECC multi-agent / commands:** ECC = Everything Claude Code. Use the agents/commands
  subset as reference; do not install its hooks. URL from prior intake; re-verify.
- **Claude Code subagent pattern:** a coordinator spawning workers with their own
  context - the mechanism Ghoti already uses manually (one agent per task on its own
  branch/worktree). The exact official doc URL should be recorded; not fabricated here.
- **Codex skill agent-launching:** the "conductor" pattern where a skill launches workers,
  not just audits. Same risk surface as the controlled launcher.
- **Existing coordinators:** reuse `kimi_claude_swarms` and `awesome-llm-apps` from
  `tool_backlog_inventory_n6_22a.json`; do not duplicate them.

## New backlog items (this milestone)

Full fields in the JSON. Summary:

| Item | Tier | Gate | Note |
|------|------|------|------|
| Sentry Search | not priority | tier2 later | search/observability-adjacent; deferred |
| Panopticore | 2 | tier2 later | ambiguous; needs exact URL |
| cobalt.tools | 2 | blocked careful | media/content saver; saving capability gated/out of scope |
| Claude Mem | 1.5 | tier1.5 | memory layer for Claude; ties to memory vault |
| AIEngineer Coach | 2 | tier2 later | AI-engineering coaching concept |
| Quant Mind | 2 | blocked careful | finance/quant; no live trading or money movement |
| Pake | 2 | tier2 later | web-page-to-desktop-app packager (handle `tw93/Pake`) |
| ChatGPT new memory / dreaming research | 2 | tier2 later | memory consolidation research; references only |
| Zero by Vercel | 2 | tier2 later | open email client; email actions gated |
| LLM RAG AI Agents | 2 | tier1 static inspect | retrieval-augmented agent patterns |
| Ideogram | 2 | tier2 later | image-generation product; API/account gated |
| Memory Palace / PAO app | tier-1-last | tier1-last product | future build-last product; see its own lane file |

## The safe progression (why launching is gated)

`simulation -> trace ingestion -> static repo intake -> controlled launcher -> approved-window bridge -> supervised overnight loop`

- simulation: N+6.21A Agent Arena (done).
- trace ingestion: N+6.23A real local trace (done).
- **static repo intake: this milestone (planning only).**
- controlled launcher: future, human-approved, dry-run-first.
- approved-window bridge: N+6.20A paste harness (no auto-submit).
- supervised overnight loop: future, human-approved, gated.

A swarm launcher is the controlled-launcher stage turned on. Until that audited
milestone, every candidate here is study-only: no install, no clone, no execution, no
agent launch.
