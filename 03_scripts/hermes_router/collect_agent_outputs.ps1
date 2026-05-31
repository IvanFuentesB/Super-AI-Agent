# collect_agent_outputs.ps1 — Hermes router wrapper (READ-ONLY).
# Summarizes the agent output logs in the vault (Claude last run, Codex last audit,
# Hermes coordinator summary) so a human can decide the next step. Reports JSON.
# Safety: read-only; vault-bounded; no LLM call; no network; no launch; never runs
# arbitrary commands.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$ScriptDir = $PSScriptRoot
$RepoRoot  = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$VaultPath = Join-Path $RepoRoot '14_context\agent_handoff_vault'
$LogsDir   = Join-Path $VaultPath '04_Logs'

try {
    $targets = [ordered]@{
        claude_last_run            = (Join-Path $LogsDir 'CLAUDE_LAST_RUN.md')
        codex_last_audit           = (Join-Path $LogsDir 'CODEX_LAST_AUDIT.md')
        hermes_coordinator_summary = (Join-Path $LogsDir 'HERMES_COORDINATOR_SUMMARY.md')
    }

    $logs = [ordered]@{}
    foreach ($k in $targets.Keys) {
        $p  = $targets[$k]
        $ex = Test-Path -LiteralPath $p -PathType Leaf
        $entry = [ordered]@{ exists = $ex; path = $p }
        if ($ex) {
            $item  = Get-Item -LiteralPath $p
            $lines = @(Get-Content -LiteralPath $p -Encoding UTF8)
            $entry['line_count']    = $lines.Count
            $entry['size_bytes']    = $item.Length
            $entry['last_modified'] = $item.LastWriteTimeUtc.ToString('o')
            $entry['preview']       = (($lines | Select-Object -First 12) -join "`n")
        }
        $logs[$k] = $entry
    }

    $result = [ordered]@{
        ok                            = $true
        wrapper                       = 'collect_agent_outputs'
        repo_root                     = $RepoRoot
        logs                          = $logs
        recommended_human_next_action = 'Review the present logs. If the audit verdict is CLEAN PASS, a human may merge; otherwise route the named fixes back to Claude. No live action is taken by this wrapper.'
        llm_used                      = $false
        network_used                  = $false
        live_action                   = $false
        local_only                    = $true
    }
    $result | ConvertTo-Json -Depth 6
    exit 0
}
catch {
    [ordered]@{ ok = $false; wrapper = 'collect_agent_outputs'; error = $_.Exception.Message; live_action = $false; local_only = $true } | ConvertTo-Json -Depth 4
    exit 1
}
