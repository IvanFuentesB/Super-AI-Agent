# N+3.38 Next Sequence Recommendation

Status: Codex recommendation only.
Date: 2026-05-01

## Repo truth used

- Branch observed: `feat/ghoti-visible-operator-stack`.
- Local HEAD observed: `00b1f68 docs(ghoti): document Claude MCP read-only bridge`.
- Origin HEAD observed from local refs/log: `00b1f68`.
- N+3.18 is finished and pushed at `e25a24c`.
- N+3.36 MCP report exists and records `ghoti-local` as connected, stdio-based, and read-only.
- N+3.37 docs exist at `232a85f`.

## Immediate recommendation

Because N+3.36 is already pushed in repo truth, there is no known unpushed N+3.36 commit to push first.

If Claude Code credits are available, the next implementation should be:

1. N+3.29 Claude - Weekly Money Review Artifact Generator.
2. N+3.30 Claude - Weekly Money Review Dashboard Read Card.
3. N+3.31 Claude - Manual Queue Draft Intake Helper.
4. N+3.32 Claude - Manual Queue Read View + Operator Work Session Planner.
5. N+3.34 Claude - Obsidian Vault + Compact Memory Scaffolding.

## Codex lane

Codex should continue doing:

- source-checks
- audits
- safety reviews
- implementation prompts
- backlog organization
- source-vs-claim comparisons

Codex should not start installing or wiring external tools while Claude implementation sequence is waiting.

## Obsidian/memory timing

Obsidian N+3.34 scaffolding should happen soon because memory compression is vital infrastructure. However, the cleanest sequence is still to implement N+3.29 first unless the user explicitly prioritizes memory before Money OS weekly review.

Reason:

- N+3.29 creates weekly review artifacts that become high-value memory inputs.
- N+3.34 then compresses those artifacts into durable/compact memory.

## External tooling timing

External tools such as AgentsView, Webclaw, Ruflo, Open Higgsfield, Viewmax, Paperclip, OpenClaw, n8n, Paseo, Bulwark, and many MCP servers should remain research/sandbox-only until:

- Money OS local artifacts are stable.
- Obsidian/compact memory is stable.
- Each tool has a source audit.
- Each tool has a risk gate.
- The operator explicitly approves installation, account connection, or paid use.

## Do not do next

- Do not install free-claude-code or unlocked Claude Code repos.
- Do not install or connect OBLITERATUS.
- Do not connect scraping/OSINT tools to runtime.
- Do not add live posting, selling, payment, outreach, or account automation.
- Do not bypass subscriptions, caps, auth, captchas, or platform rules.
- Do not spend money autonomously.

## Exact next Claude recommendation

Implement N+3.29 - Weekly Money Review Artifact Generator, using local files only, artifact-only outputs, no queue mutation, no live actions, and validation/commit/push.

## Exact next Codex recommendation

If Claude is unavailable, Codex should either do one narrow source audit for the highest-priority external candidates, or stop planning and wait for implementation capacity.
