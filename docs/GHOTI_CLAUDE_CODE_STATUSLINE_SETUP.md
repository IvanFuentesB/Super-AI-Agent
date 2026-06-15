# Ghoti Claude Code Statusline Setup

## Verified source and verdict

- Source: `https://github.com/sirmalloc/ccstatusline`
- Revision inspected: `2159379a3af4dedd700af8d999f4eaed1a055b5e`
- Package/version inspected: `ccstatusline` `2.2.21`
- License: MIT
- Classification: package-managed manual setup candidate

`ccstatusline` can show model, branch/status, context use, token counts,
session/weekly usage, reset timers, and thinking effort. Optional widgets can
query Claude usage state for extra-usage information. It cannot promise a
universal exact "credits left" value, so Ghoti must not label it that way.

## Why installation remains manual

The TUI can write Claude Code `settings.json`, install a global package, manage
hooks, inspect `.claude.json`, and optionally call the usage API. The project
backs up settings, but Ghoti still requires the human to inspect and approve the
change. This branch does not install it or modify user/global Claude settings.

## Safe manual setup

1. Inspect existing Claude Code settings and make an additional human-owned
   backup.
2. Review the pinned source/version above and the current release before use.
3. Use the project's pinned-install flow rather than an always-latest command.
4. Start with local signals only: model, Git branch/status, context bar, token
   counts, and thinking effort.
5. Keep account email, usage API, extra-usage, custom commands, hook management,
   and font installation disabled until separately approved.
6. Verify the displayed values against Claude Code's own status/usage surfaces.

The committed example config deliberately records `installed:false`,
`usage_api_enabled:false`, and `exact_credits_supported:false`.
