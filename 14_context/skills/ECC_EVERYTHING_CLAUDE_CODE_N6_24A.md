# ECC = Everything Claude Code (N+6.24A)

Milestone: N+6.24A
Date: 2026-06-06
Status: static intake / guidance-only. No ECC code is vendored, installed, cloned, or
executed here. Builds on `ecc_inspired_agent_setup_n6_19a.md`.

## What ECC is (and is not)

- **ECC = "Everything Claude Code"**: a curated bundle for Claude Code - a collection of
  **commands, agents/subagents, skills, hooks, and security-scanner patterns** meant to
  supercharge a Claude Code setup.
- **ECC is NOT elliptic curve cryptography.** In this repo "ECC" always means Everything
  Claude Code.
- **Recorded source (re-verify):** prior intake (`ecc_inspired_agent_setup_n6_19a.md`)
  records the ECC reference repository as `https://github.com/affaan-m/ecc` (noted there
  as MIT-licensed, statically inspected, no code vendored). Confidence is medium; the
  operator should re-confirm the exact repo/license before any deeper intake. No new URL
  is fabricated here.

## What ECC contains (conceptual, from the four building blocks)

- **Commands:** many slash-style prompt templates for common Claude Code workflows.
- **Agents/subagents:** predefined roles for fan-out/parallel work.
- **Skills:** packaged instructions/knowledge the model can load.
- **Hooks:** event-triggered automation (lint/validate/format/guard) - the executable,
  highest-risk part.
- **Security scanner patterns:** regex/blocklist patterns to catch secrets and unsafe
  code (Ghoti already runs an equivalent in `public_repo_security_audit.py`).

## Why Ghoti adapts ECC instead of full-installing it

Ghoti's safety model is "adapt the ideas, gate the execution":

1. **Hooks execute code.** A full ECC install can wire hooks that run on tool/lifecycle
   events. In the operator's real profile those could paste into apps, push branches,
   install packages, or take live actions - exactly what Ghoti's approval gates forbid.
2. **Auto-submit / live actions.** ECC bundles aim for speed; Ghoti requires no
   auto-submit and human approval for every outbound or risky action.
3. **Unaudited surface.** A bundle pulls in many commands/agents/hooks at once; Ghoti
   intakes one capability at a time, statically inspected, behind a named milestone.
4. **Profile blast radius.** Installing into the working Claude profile changes the same
   environment that operates Ghoti. Ghoti keeps that environment minimal and predictable.

So Ghoti **re-expresses ECC patterns** (agent profiles, command templates,
hook-as-validator ideas, scanner patterns) as **guidance-only** records and builds its
own audited equivalents, rather than installing the bundle.

## How full ECC *could* be tested safely (separate Claude profile)

If the operator wants to exercise real ECC end-to-end, do it in an **isolated profile**,
never in the Ghoti environment:

1. Create a **separate, throwaway Claude Code profile/config** (a distinct OS user profile
   or a disposable VM/sandbox), with **no access** to the Ghoti repo, the operator's real
   accounts, or any secrets/`.env`.
2. Install ECC **there only**, against a **scratch repo** with junk data.
3. Exercise its commands/agents and let its **hooks** fire in that sandbox; observe what
   each hook actually executes.
4. Keep all credentials out; allow no outbound account/API/posting/money actions.
5. Capture findings as **static notes** and bring only the notes back into Ghoti
   (`14_context/skills/`), not the executable bundle.
6. Promote any single ECC idea into Ghoti only through a separate, audited, human-approved
   milestone (guidance-only first, runtime-wired never by default).

This isolates ECC's executable hooks from the operator's real machine while still letting
the ideas be evaluated honestly.

## ECC in the swarm path

ECC's **agents/subagents** and **commands** are directly relevant to the controlled
swarm launcher: they are reference patterns for "spawn a worker, give it a command,
collect output." Those references are tracked in
`../tool_intake/swarm_launcher_repo_intake_n6_24a.md`. They stay **planning-only** until
the controlled-launcher milestone is approved.
