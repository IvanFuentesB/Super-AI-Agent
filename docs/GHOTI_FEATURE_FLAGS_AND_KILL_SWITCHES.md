# Ghoti Feature Flags and Kill Switches

## Why feature flags

Ghoti grows by adding capabilities that range from harmless (read a status file) to risky
(launch an agent, post to an account, move money). Feature flags let us land the **code**
for a capability without making the capability **live**. Nothing becomes active just
because the code exists in the repo; a human must flip a flag in a runtime file that lives
outside the repo.

## The global kill switch

`global_kill_switch` is a single flag that overrides every risky feature. When it is true,
risky actions are paused regardless of any other flag. The Telegram status bot honors it
directly: with the kill switch on, the bot pauses status actions and only answers `/help`
and `/flags`. The kill switch is the fastest way to stop everything without editing code
or killing processes one by one.

## Per-feature flags

Every risky feature has its own flag, and **every risky flag defaults false**. The only
flag that defaults true is the read-only status command toggle
(`telegram_status_commands_enabled`), because answering read-only status is not a risky
action. Current flags (see `23_configs/ghoti_feature_flags.example.json`):

- `global_kill_switch` (false) - overrides all risky features
- `telegram_status_bot_enabled` (false) - operator opt-in to run the status bot
- `telegram_status_commands_enabled` (true) - read-only status replies
- `telegram_run_commands_enabled` (false) - never run commands via Telegram
- `telegram_send_commands_enabled` (false) - never auto-send via Telegram
- `mcp_enabled`, `mcp_filesystem_read_only_enabled` (false)
- `live_agent_launch_enabled`, `claude_launch_enabled`, `codex_launch_enabled` (false)
- `browser_computer_use_enabled` (false)
- `email_draft_agent_enabled`, `whatsapp_draft_agent_enabled`, `auto_send_enabled` (false)
- `external_repo_install_enabled` (false)
- `affiliate_program_enabled` (false)
- `dashboard_local_analytics_enabled` (false)
- `docker_runtime_enabled`, `vps_runtime_enabled` (false)

## Rollback

Because a feature only goes live behind a flag, rollback is "set the flag back to false."
No code revert, no redeploy. The running bot reloads flags every poll cycle, so a flag
change takes effect on the next cycle. This makes every risky feature reversible.

## Safe rollout

1. Land the code with its flag defaulting false.
2. Add tests that prove the feature stays inert while the flag is false.
3. A human enables the flag in the outside-repo runtime file on one machine.
4. Observe. If anything is wrong, flip the flag (or the kill switch) back to false.
5. Only widen the rollout after an audited milestone.

## How to add a feature behind a flag

- Add the flag to `ghoti_feature_flags.example.json` with a **false** default.
- Gate the new behavior on the flag (and on `global_kill_switch` being false).
- Add a test that the behavior is inert when the flag is false.
- Document the flag here.

## How to remove a feature

- Set the flag false everywhere and confirm nothing depends on it being true.
- Remove the gated code and the flag in the same change.
- Remove or update the tests and this doc.

## Never merge a risky feature default-on

A pull request that adds a risky capability with its flag defaulting **true** must not be
merged. Risky defaults belong to a deliberate, audited rollout - never to the default
example shipped in the repo.
