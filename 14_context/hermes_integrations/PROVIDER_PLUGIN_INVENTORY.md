# Provider & Plugin Inventory (read-only)

Status: **read-only inventory**. No provider auth is configured; no secret is read or
stored. This note mirrors `provider_plugin_inventory.ps1`.

## Local-first truth

- **Local provider:** Ollama / custom endpoint on loopback (documented only).
- **Hermes model:** `llama3.1:8b`. **Cheap worker model:** `gemma3:4b`.

## Optional / planned (not configured, not enabled)

- Kimi - `kimi_configured: false`
- Anthropic (Claude) - `anthropic_configured: false`
- GitHub - `github_configured: false`
- Browser plugins - `browser_plugins_enabled: false`

`cloud_provider_keys_expected_in_repo: false`.

## Rules

- **A visible plugin does not mean it is approved or enabled.** Enablement is separate and
  approval-gated.
- **Subscription and cloud providers are optional, not extra spend.** The local-first
  stack runs on already-owned hardware; any paid provider is opt-in and never required.

## Secret rule

Detection is from safe status text only; the script never reads secret/.env/token files,
never prints key values, and never reads environment variable values. Secrets are never
stored in the repo, in Obsidian, or in prompts.
