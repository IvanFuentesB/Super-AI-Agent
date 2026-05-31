# Hermes Integration Status (read-only foundation)

Status: **Phase 1 - read-only / status-only foundation.** No tokens, no live
integrations. This note mirrors `hermes_integration_status.ps1`.

## Standing flags (all live capability disabled)

| Flag | Value |
|------|-------|
| telegram_planned | true |
| telegram_enabled | false |
| mcp_planned | true |
| mcp_enabled | false |
| provider_keys_required | false |
| browser_use_enabled | false |
| computer_use_enabled | false |
| live_agent_launch_enabled | false |
| email_whatsapp_enabled | false |
| arbitrary_command_execution_enabled | false |
| secrets_in_repo | false |
| local_only | true |

## Foundation present

- `HERMES_SOUL.md` and `HERMES_ROUTER_POLICY.md` exist in the vault.
- The seven N+6.6A router wrappers exist; Hermes runs **approved wrappers only** and
  **never runs arbitrary commands**.
- Five new read-only/planning scripts report JSON status for the planned integrations.

## Secret rule

**Secrets are never stored in the repo, in Obsidian, or in prompts.** Any future token,
key, or credential is supplied at run time only and is never committed.

## Next safe step

Codex audits this read-only foundation; a human approves Phase 2 (a status-only Telegram
bot) before any token exists.
