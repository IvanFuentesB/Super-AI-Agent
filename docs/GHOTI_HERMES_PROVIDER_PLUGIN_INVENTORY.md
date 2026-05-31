# Ghoti / Hermes Provider & Plugin Inventory

Status: **read-only inventory**. This lists the local provider/model truth and the
*planned* cloud providers and plugins. It reads **no secret files** and prints **no key
values**. No provider auth is configured by this milestone.

## Local-first truth (already owned)

- **Local provider:** Ollama / custom endpoint on loopback (documented only).
- **Hermes model:** `llama3.1:8b` (the local coordinator).
- **Cheap worker model:** `gemma3:4b` (the local summary worker).

The local-first stack runs on already-owned hardware.

## Planned / optional cloud providers and plugins

These are **inventory only** and are **not configured** and **not enabled**:

| Provider / plugin | Configured | Note |
|-------------------|-----------|------|
| Kimi | false | optional, approval-gated |
| Anthropic (Claude) | false | optional, approval-gated |
| GitHub | false | optional, approval-gated |
| Browser plugins | false | not enabled |

`cloud_provider_keys_expected_in_repo: false`. Provider keys are never kept in the repo.

## Two rules that govern this inventory

1. **A visible plugin does not mean it is approved or enabled.** Seeing a provider or
   plugin in a UI or a list is not approval; enablement is a separate, approval-gated step.
2. **Subscription and cloud providers are optional, not extra spend.** The local-first
   stack already runs on owned hardware; any paid provider is opt-in, approval-gated, and
   never required to operate Ghoti.

## Secret rule

No secret/.env/token/cookie/auth file is read or stored. Configuration is reported only
from safe status text, never from key values. Secrets are never stored in the repo, in
Obsidian, or in prompts.
