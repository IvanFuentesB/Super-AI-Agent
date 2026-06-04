# ECC-Inspired Ghoti Agent Setup

Attribution: informed by static inspection of the MIT-licensed ECC repository at `https://github.com/affaan-m/ecc`. No ECC code is vendored here.

## Ghoti Agent Roles

- Strategy brain: ChatGPT, architecture and prompt planning.
- Implementation lane: Claude Code, feature work.
- Audit lane: Codex, merge gates and safety verification.
- Coordinator: Hermes, local switchboard and handoff reader, manual bridge only.
- Local worker: Gemma, cheap summaries, classification, compression.
- Memory: Obsidian and Ghoti status brain.
- Final approval: human operator.

## Local Skill Record

Every imported skill idea must record:

- source repo
- license
- summary
- allowed use
- blocked use
- install status
- runtime wiring status
- audit date

## Hooks Policy

Hooks may become local validators and report writers. They must not execute code, paste into apps, push branches, install packages, or trigger live agent actions without a later audited milestone.
