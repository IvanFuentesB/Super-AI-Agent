# telegram_status_bot_plan.ps1 — Telegram status-bot plan (PLANNING ONLY).
# Describes the planned Phase-2 Telegram *status* bot: the read-only first commands,
# the forbidden commands, and the token-storage rule. Reports JSON. Nothing is live.
# Safety: planning only; no network; no token; no bot; never runs arbitrary commands.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

try {
    $result = [ordered]@{
        ok                      = $true
        wrapper                 = 'telegram_status_bot_plan'
        status_bot_phase        = 'planned_only'
        allowed_first_commands  = @('/status', '/current_task', '/latest_claude', '/latest_codex', '/help')
        forbidden_commands      = @('/run', '/send', '/delete', '/login', '/post', '/buy', '/trade')
        token_storage_rule      = 'never in repo, never in Obsidian, never in prompts'
        setup_steps_summary     = @(
            '1. A human creates a bot token out-of-band; the token is never placed in the repo, in Obsidian, or in any prompt.',
            '2. The token is supplied at run time only (for example a local environment variable) and is never committed.',
            '3. The bot answers status-only commands: /status, /current_task, /latest_claude, /latest_codex, /help.',
            '4. No /run, /send, /delete, /login, /post, /buy, or /trade command is implemented.',
            '5. Live enablement requires explicit human approval in a separate milestone.'
        )
        network_used            = $false
        token_present           = $false
        enabled                 = $false
        requires_human_approval = $true
        local_only              = $true
    }
    $result | ConvertTo-Json -Depth 6
    exit 0
}
catch {
    [ordered]@{ ok = $false; wrapper = 'telegram_status_bot_plan'; error = $_.Exception.Message; enabled = $false; requires_human_approval = $true; local_only = $true } | ConvertTo-Json -Depth 4
    exit 1
}
