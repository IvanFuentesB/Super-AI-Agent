# Codex N+3.51 - Next Sequence Lock

Milestone: N+3.51

Date: 2026-05-06

## Current Sequence Truth

Main is at:

```text
e7e946a merge(ghoti): land N+3.49A local orchestrator and Ruflo smoke
```

N+3.49A is merged and pushed.

The system has:

- local agent lane locks,
- prompt bus,
- local worker router,
- local orchestrator,
- Obsidian vault files,
- compact memory files,
- Ruflo cloned for evaluation,
- Ollama installed,
- strict safety gates.

The system does not yet have:

- automatic Claude/Codex control,
- dashboard bridge card,
- real prompt context pack generation,
- Gemma compression worker,
- Ruflo installed,
- Ruflo help/version smoke,
- merge readiness assistant,
- automated Obsidian memory refresh.

## Recommended Next Claude Code Milestone

Next Claude should run:

```text
N+3.51A - Bridge Dashboard + Prompt Bus Apply + Gemma Compression + Ruflo Isolated Install Gate
```

Branch:

```text
feat/ghoti-agent-claude-n3-51-bridge-dashboard-gemma-ruflo
```

Primary goals:

1. Add a read-only local bridge dashboard route/card.
2. Add prompt context pack generation.
3. Add Gemma/Ollama draft compression worker.
4. Add Ruflo isolated install gate runner.
5. Improve Obsidian open/check helper.
6. Improve course/certificate router keywords.
7. Keep everything dry-run-first and local-only.

## Recommended Next Codex Milestone

After Claude pushes N+3.51A:

```text
N+3.51B - Audit Bridge Dashboard, Gemma Worker, Ruflo Install Gate, And Merge Readiness
```

Codex should:

- inspect Claude branch diff,
- validate Python AST,
- validate dashboard JS,
- run dry-run helpers,
- run read-only checks,
- verify no live actions,
- verify no package install unless explicitly documented,
- verify no `node_modules` staged,
- prepare merge plan.

## Ruflo Sequence

Ruflo should not jump straight to swarm/runtime use.

Safe sequence:

1. N+3.51A adds install gate.
2. N+3.51B audits install gate.
3. Operator approves isolated install if desired.
4. N+3.52A runs only:
   - `npm ci --ignore-scripts` in Ruflo dir,
   - local help/version command,
   - no swarm,
   - no MCP,
   - no repo writes outside logs.
5. N+3.52B audits help/version output.
6. Only later consider local-only plan generation.

Forbidden until later:

- `v3:swarm`,
- MCP activation,
- Claude hook activation,
- global install,
- browser/desktop/account control,
- any live action.

## Gemma Sequence

Gemma should become useful without becoming trusted authority.

Safe sequence:

1. Add draft compression worker.
2. If model missing, worker writes clear warning and outbox prompt instead of pulling.
3. If model present, worker may call local Ollama only with explicit apply command.
4. Output drafts to logs/outbox.
5. Human/Codex/Claude review promotes useful content into compact memory.
6. No automatic canonical overwrite.

## Obsidian Sequence

The vault exists, but the app is not verified as visible to the current sandbox user.

Safe sequence:

1. Improve helper install/path checks.
2. Print exact manual open fallback.
3. Keep dashboard refresh read-only.
4. Only open Obsidian with explicit operator command.
5. Do not auto-launch app from dashboard refresh.

## Project Percentage Lock

Current estimate: 74%.

After N+3.51A if implemented cleanly:

- 84-87% if Gemma model remains unavailable but worker/gates/dashboard exist.
- 86-89% if Gemma model is available and compression smoke passes.

Do not claim 90% until:

- merge assistant exists,
- first Ruflo isolated help/version smoke is audited,
- dashboard actually shows bridge status,
- prompt packs reduce real copy-paste,
- Gemma produces usable drafts or a safe no-model fallback.

## What Must Not Happen Next

Do not:

- run uncontrolled parallel agents,
- install Ruflo globally,
- launch Ruflo swarms,
- connect Ruflo MCP,
- connect external account tools,
- run browser automation against live accounts,
- scrape,
- send email,
- post content,
- pay or subscribe,
- apply to jobs,
- enter giveaways,
- use credentials,
- treat Gemma output as truth,
- let dashboard buttons mutate state,
- stage unrelated local dirt.

## Exact Operator Commands

No operator command is required before the next Claude run.

Optional manual visibility checks only:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only
python 03_scripts/ghoti_local_orchestrator.py --status
python 03_scripts/ghoti_local_orchestrator.py --ruflo-check
python 03_scripts/ghoti_local_orchestrator.py --gemma-check
```

Do not run Ruflo install until the N+3.51A install gate exists and Codex audits it.
