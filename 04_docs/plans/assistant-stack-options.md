# Assistant Stack Options

Last updated: 2026-04-05

## Constraints and verified facts

- This machine has 32 GB RAM and an RTX 4060 Laptop GPU with about 8 GB VRAM.
- Python is not usable yet in this sandbox account.
- Ollama is not installed yet.
- GitHub and Notion integrations are not connected yet.

## Verified model source

Google's official Gemma docs currently list Gemma 4 variants for Ollama as:

- `gemma4:e2b`
- `gemma4:e4b`
- `gemma4:26b`
- `gemma4:31b`

Verified source:

- https://ai.google.dev/gemma/docs/integrations/ollama

## Option A: Lowest-risk practical path

Core tools:

- Ollama
- Continue
- PowerShell scripts
- Git
- local markdown docs under this workspace

Model/runtime:

- Gemma 4 E2B or E4B in Ollama

What gets installed first:

- Python fix
- PowerShell 7
- `uv`
- `gh`
- Ollama
- Continue

What stays manual:

- browser changes
- GitHub auth-sensitive actions
- system-wide config changes
- model switching and benchmark interpretation

What gets automated later:

- workspace snapshots
- repo status reports
- audit logging
- benchmark runs

Risks:

- low complexity
- lower ceiling than larger harness stacks

Why it fits this machine:

- realistic on 8 GB VRAM
- easy to reason about
- low maintenance

## Option B: Balanced local-first stack

Core tools:

- Option A tools
- Aider
- llama.cpp
- Playwright later if browser automation is needed

Model/runtime:

- Gemma 4 E4B as the first local default
- optional Gemma 4 26B experiments later

What gets installed first:

- Option A stack
- then Aider
- then llama.cpp

What stays manual:

- high-risk system changes
- browser profile and account state
- approval gates for destructive commands

What gets automated later:

- code-assist runs
- prompt/eval loops
- repo health checks
- benchmark recording

Risks:

- more moving parts
- more maintenance than Option A

Why it fits this machine:

- still practical
- adds flexibility without forcing a heavy orchestration layer too early

## Option C: Ambitious future-proof stack

Core tools:

- Option B tools
- OpenHarness as a harness candidate
- OpenClaw only as a later evaluation
- Docker and WSL2 if the stack genuinely needs them

Model/runtime:

- local small/mid-size Gemma 4 variants
- cloud fallback for heavy reasoning

What gets installed first:

- only after the Option A/B foundation is clean

What stays manual:

- sensitive approvals
- system-level profile changes
- final merge/publish decisions

What gets automated later:

- harness experiments
- controlled sub-agent workflows
- more formal eval loops

Risks:

- easiest path to tool sprawl
- highest setup and maintenance cost
- more places for silent breakage

Why it fits this machine:

- possible, but only if built in phases

## Repo stance

- Claw Code: study and borrow ideas, do not center now
- OpenHarness: more credible future harness candidate than most hype repos, but still later
- oh-my-codex: useful if Codex becomes the daily driver, not the core runtime
- OpenClaw: interesting later, not the first foundation

Root note:

- `AI_Managed_Only` is the permanent workspace root
- `AI_Workspace` is temporary only

## Recommendation

Start with Option A.

Move to Option B after the sandbox basics are fixed.

Keep Option C as a deliberate later phase, not the starting point.
