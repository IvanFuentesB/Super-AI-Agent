# Feature Flags and Kill Switches (N+6.10C)

This note mirrors `docs/GHOTI_FEATURE_FLAGS_AND_KILL_SWITCHES.md` and the example
`23_configs/ghoti_feature_flags.example.json`.

## Principle

Every risky feature has a flag. **Every risky flag defaults false.** A single
`global_kill_switch` overrides every risky feature. No command becomes live just because
the code exists in the repo - a human flips a flag in a runtime file outside the repo.
Features stay reversible: set the flag back to false and the behavior stops on the next
poll cycle.

## The one true-by-default flag

Only `telegram_status_commands_enabled` defaults true, because read-only status replies
are not a risky action. Everything else (Telegram run/send, MCP, agent launch, browser /
computer-use, email/WhatsApp drafts, auto-send, external repo install, affiliate program,
dashboard analytics, Docker, VPS) defaults false.

## Kill switch behavior

With `global_kill_switch: true`, the status bot pauses all status actions and only answers
`/help` and `/flags`. It is the fastest way to stop everything without editing code or
killing processes individually.

## Never default-on

A risky capability must never be merged with its flag defaulting true. Risky rollout is
deliberate, audited, and per-machine - never the shipped default.
