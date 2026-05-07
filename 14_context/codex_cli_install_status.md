# Codex CLI Install Status — N+1.6

**Date:** 2026-04-24
**Branch:** feat/ghoti-visible-operator-stack

## Install command used

```powershell
npm i -g @openai/codex
```

## Verification

| Check | Result |
|-------|--------|
| `codex --version` | `codex-cli 0.124.0` |
| `where.exe codex` | `C:\Users\ai_sandbox\AppData\Roaming\npm\codex` |
| `npm list -g @openai/codex --depth=0` | `@openai/codex@0.124.0` |
| Works from shell | YES |

## Sign-in status

Sign-in is **pending**. Codex CLI is installed but has not been authenticated.

Safe first run (run this yourself to authenticate):

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only
codex
```

## Bridge truth

```
Claude Code ↔ Codex automatic bridge: NOT PROVEN.
Current bridge status: manual_handoff_only unless future runtime proof is added.
```

Codex CLI is an independent tool. Installing it does not create any automatic connection between Claude Code sessions and Codex. They are separate runtimes. The Ghoti dashboard includes a `queue-recipe-codex-handoff` recipe that provides a manual handoff path only.
