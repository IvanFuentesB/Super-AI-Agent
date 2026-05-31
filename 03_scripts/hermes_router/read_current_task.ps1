# read_current_task.ps1 — Hermes router wrapper (READ-ONLY).
# Reads the current classified task from the Obsidian vault and reports it as JSON.
# Safety: read-only; repo-root + vault bounded; no writes; no network; no launch;
# never runs arbitrary commands.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$ScriptDir = $PSScriptRoot
$RepoRoot  = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$VaultPath = Join-Path $RepoRoot '14_context\agent_handoff_vault'
$TaskPath  = Join-Path $VaultPath '02_Agent_Handoffs\CURRENT_TASK.md'

try {
    $exists = Test-Path -LiteralPath $TaskPath -PathType Leaf
    $preview = ''
    if ($exists) {
        $lines = @(Get-Content -LiteralPath $TaskPath -TotalCount 24 -Encoding UTF8)
        $preview = ($lines -join "`n")
    }

    $result = [ordered]@{
        ok                  = $true
        wrapper             = 'read_current_task'
        repo_root           = $RepoRoot
        vault_path          = $VaultPath
        current_task_path   = $TaskPath
        task_exists         = $exists
        task_preview        = $preview
        allowed_actions_now = @('read_files', 'summarize', 'prepare_prompt')
        live_action         = $false
        local_only          = $true
    }
    $result | ConvertTo-Json -Depth 6
    exit 0
}
catch {
    [ordered]@{ ok = $false; wrapper = 'read_current_task'; error = $_.Exception.Message; live_action = $false; local_only = $true } | ConvertTo-Json -Depth 4
    exit 1
}
