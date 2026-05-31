# hermes_router_status.ps1 — Hermes router wrapper (READ-ONLY).
# Reports the state of the Hermes router foundation: which soul/status/policy files
# and wrappers exist, and the standing safety flags. Reports JSON.
# Safety: read-only; no network; no launch; never runs arbitrary commands.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$ScriptDir = $PSScriptRoot
$RepoRoot  = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$VaultPath = Join-Path $RepoRoot '14_context\agent_handoff_vault'
$LogsDir   = Join-Path $VaultPath '04_Logs'

try {
    $wrapperNames = @(
        'read_current_task.ps1',
        'write_handoff_note.ps1',
        'prepare_claude_prompt.ps1',
        'prepare_codex_audit.ps1',
        'collect_agent_outputs.ps1',
        'run_gemma_summary.ps1',
        'hermes_router_status.ps1'
    )
    $present = @()
    $missing = @()
    foreach ($w in $wrapperNames) {
        if (Test-Path -LiteralPath (Join-Path $ScriptDir $w) -PathType Leaf) { $present += $w } else { $missing += $w }
    }

    $result = [ordered]@{
        ok                                  = $true
        wrapper                             = 'hermes_router_status'
        repo_root                           = $RepoRoot
        vault_exists                        = (Test-Path -LiteralPath $VaultPath -PathType Container)
        soul_exists                         = (Test-Path -LiteralPath (Join-Path $VaultPath 'HERMES_SOUL.md') -PathType Leaf)
        current_status_exists               = (Test-Path -LiteralPath (Join-Path $VaultPath 'HERMES_CURRENT_STATUS.md') -PathType Leaf)
        router_policy_exists                = (Test-Path -LiteralPath (Join-Path $VaultPath 'HERMES_ROUTER_POLICY.md') -PathType Leaf)
        coordinator_summary_exists          = (Test-Path -LiteralPath (Join-Path $LogsDir 'HERMES_COORDINATOR_SUMMARY.md') -PathType Leaf)
        wrappers_present                    = $present
        wrappers_present_count              = $present.Count
        wrappers_missing                    = $missing
        wrappers_missing_count              = $missing.Count
        dry_run_default                     = $true
        live_launch_enabled                 = $false
        browser_use_enabled                 = $false
        computer_use_enabled                = $false
        telegram_enabled                    = $false
        mcp_enabled                         = $false
        arbitrary_command_execution_enabled = $false
        local_only                          = $true
        next_safe_step                      = 'Let Codex audit the N+6.6A wrapper foundation, then a human decides merge.'
    }
    $result | ConvertTo-Json -Depth 6
    exit 0
}
catch {
    [ordered]@{ ok = $false; wrapper = 'hermes_router_status'; error = $_.Exception.Message; live_launch_enabled = $false; local_only = $true } | ConvertTo-Json -Depth 4
    exit 1
}
