# local_worker_status.ps1 — local worker status (READ-ONLY / PLANNING).
# Reports the planned local-worker setup (Gemma summary worker, llama coordinator,
# queue, scheduled jobs, 24/7 mode). Everything live is disabled. Reports JSON.
# Safety: read-only; no network; no scheduler; no daemon; never runs arbitrary commands.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$ScriptDir = $PSScriptRoot
$RepoRoot  = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$VaultPath = Join-Path $RepoRoot '14_context\agent_handoff_vault'

try {
    # llama is the documented Hermes coordinator model truth iff the soul file says so.
    $soulExists = Test-Path -LiteralPath (Join-Path $VaultPath 'HERMES_SOUL.md') -PathType Leaf

    $result = [ordered]@{
        ok                             = $true
        wrapper                        = 'local_worker_status'
        local_workers_planned          = $true
        gemma_summary_worker_enabled   = $false
        llama_coordinator_enabled      = [bool]$soulExists
        llama_coordinator_meaning      = 'documented Hermes coordinator model (llama3.1:8b), not a running 24/7 process'
        queue_enabled                  = $false
        scheduled_jobs_enabled         = $false
        twenty_four_seven_mode_enabled = $false
        network_used                   = $false
        local_only                     = $true
        next_safe_step                 = 'Phase 4 designs a local Gemma summary worker over queue files with scheduled summaries; it stays disabled until a human approves it. No live account action.'
    }
    $result | ConvertTo-Json -Depth 6
    exit 0
}
catch {
    [ordered]@{ ok = $false; wrapper = 'local_worker_status'; error = $_.Exception.Message; twenty_four_seven_mode_enabled = $false; queue_enabled = $false; local_only = $true } | ConvertTo-Json -Depth 4
    exit 1
}
