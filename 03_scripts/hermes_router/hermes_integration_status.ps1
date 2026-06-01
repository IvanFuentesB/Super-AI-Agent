# hermes_integration_status.ps1 — Hermes integration status (READ-ONLY).
# Reports the Hermes full-integration setup foundation: which soul/policy files and
# router wrappers exist, plus the standing "not enabled" safety flags for the planned
# Telegram / MCP / provider / launch / email-WhatsApp integrations. Reports JSON.
# Safety: read-only; no network; no launch; no installs; never runs arbitrary commands.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$ScriptDir = $PSScriptRoot
$RepoRoot  = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$VaultPath = Join-Path $RepoRoot '14_context\agent_handoff_vault'
$IntegPath = Join-Path $RepoRoot '14_context\hermes_integrations'

try {
    $soulPath   = Join-Path $VaultPath 'HERMES_SOUL.md'
    $policyPath = Join-Path $VaultPath 'HERMES_ROUTER_POLICY.md'

    $wrapperNames = @(
        'read_current_task.ps1',
        'write_handoff_note.ps1',
        'prepare_claude_prompt.ps1',
        'prepare_codex_audit.ps1',
        'collect_agent_outputs.ps1',
        'run_gemma_summary.ps1',
        'hermes_router_status.ps1'
    )
    $wrappersPresent = $true
    foreach ($w in $wrapperNames) {
        if (-not (Test-Path -LiteralPath (Join-Path $ScriptDir $w) -PathType Leaf)) { $wrappersPresent = $false }
    }

    $result = [ordered]@{
        ok                                  = $true
        wrapper                             = 'hermes_integration_status'
        repo_root                           = $RepoRoot
        main_expected_status                = 'N+6.7C on main; this is a read-only/status-only integration foundation.'
        hermes_soul_exists                  = (Test-Path -LiteralPath $soulPath -PathType Leaf)
        hermes_router_policy_exists         = (Test-Path -LiteralPath $policyPath -PathType Leaf)
        wrappers_present                    = $wrappersPresent
        integrations_dir_exists             = (Test-Path -LiteralPath $IntegPath -PathType Container)
        telegram_planned                    = $true
        telegram_enabled                    = $false
        mcp_planned                         = $true
        mcp_enabled                         = $false
        provider_keys_required              = $false
        browser_use_enabled                 = $false
        computer_use_enabled                = $false
        live_agent_launch_enabled           = $false
        email_whatsapp_enabled              = $false
        arbitrary_command_execution_enabled = $false
        secrets_in_repo                     = $false
        local_only                          = $true
        next_safe_step                      = 'Codex audits this read-only foundation; a human approves Phase 2 (a status-only Telegram bot) before any token exists.'
    }
    $result | ConvertTo-Json -Depth 6
    exit 0
}
catch {
    [ordered]@{ ok = $false; wrapper = 'hermes_integration_status'; error = $_.Exception.Message; telegram_enabled = $false; mcp_enabled = $false; live_agent_launch_enabled = $false; local_only = $true } | ConvertTo-Json -Depth 4
    exit 1
}
