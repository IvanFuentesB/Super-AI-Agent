# ECC Intended Use vs Ghoti Adaptation

A side-by-side so it stays clear why Ghoti uses ECC ("everything-claude-code") ideas
but not ECC itself.

| Aspect | ECC intended use | Ghoti adaptation |
|--------|------------------|------------------|
| Install | Full plugin + hooks installed | Not installed; ideas re-expressed in Ghoti's own scripts |
| Hooks | Lifecycle hooks run scripts automatically | Validators run on demand, read-only, never auto-executed |
| Node scripts | Run as part of the workflow | Never run |
| Agent roles | Provided by the framework | Kept as Ghoti lanes (one-agent-per-task) |
| Skills / commands | Framework skill registry | Ghoti project skills + N+6.19A prompt-packet templates |
| Security scanner | Executable scanner | Extend the existing read-only repo audit |
| Token optimization | Framework features | Compact status/handoff files + short auto-loaded `AGENTS.md` |

## Why Ghoti does not install ECC

- ECC ships many executable hooks/scripts; automatic execution conflicts with Ghoti's
  supervised, approval-gated posture.
- Stacking a plugin install plus a manual install risks duplicate, surprising
  behavior.
- Ghoti stays local-first: no automatic outbound calls, no account access, no live
  control from an installed framework.

## Rule of thumb

Inspect ECC, take the *idea*, write it ourselves behind a feature flag, and keep every
hook a read-only validator. The global Codex `AGENTS.md` and the global Codex skills
(`safe-repo-intake`, `codex-merge-gate`, `agent-swarm-simulator`, `token-saving-audit`)
live outside this repo; this repo's `AGENTS.md` is the in-repo, version-controlled set
of rules.
