# prepare_codex_audit.ps1 — Hermes router wrapper (DRY-RUN by default).
# Assembles a Codex audit prompt from the vault rules + current task + Codex audit
# template + the last Claude run, and previews it. With -AllowWrite it writes
# 02_Agent_Handoffs/PREPARED_CODEX_AUDIT_PROMPT.md. It NEVER launches Codex.
# Safety: read sources are vault-bounded; output is a fixed vault path; no network;
# no terminal spawn; never runs arbitrary commands.

param(
    [switch]$AllowWrite
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$ScriptDir  = $PSScriptRoot
$RepoRoot   = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$VaultPath  = Join-Path $RepoRoot '14_context\agent_handoff_vault'
$HandoffDir = Join-Path $VaultPath '02_Agent_Handoffs'
$LogsDir    = Join-Path $VaultPath '04_Logs'

try {
    $srcPaths = [ordered]@{
        agent_rules     = (Join-Path $VaultPath 'AGENT_RULES.md')
        current_task    = (Join-Path $HandoffDir 'CURRENT_TASK.md')
        codex_audit     = (Join-Path $HandoffDir 'CODEX_AUDIT_PROMPT.md')
        claude_last_run = (Join-Path $LogsDir 'CLAUDE_LAST_RUN.md')
    }

    $srcExists = [ordered]@{}
    $sb = New-Object System.Text.StringBuilder
    foreach ($k in $srcPaths.Keys) {
        $p  = $srcPaths[$k]
        $ex = Test-Path -LiteralPath $p -PathType Leaf
        $srcExists[$k] = $ex
        if ($ex) {
            [void]$sb.AppendLine("## Source: $k")
            [void]$sb.AppendLine((Get-Content -LiteralPath $p -Raw -Encoding UTF8))
            [void]$sb.AppendLine('')
        }
    }
    $combined = $sb.ToString()

    $outputPath = Join-Path $HandoffDir 'PREPARED_CODEX_AUDIT_PROMPT.md'
    $wrote = $false
    $mode  = 'dry_run'
    if ($AllowWrite.IsPresent) {
        Set-Content -LiteralPath $outputPath -Value $combined -Encoding UTF8
        $wrote = $true
        $mode  = 'write'
    }

    $preview = if ($combined.Length -gt 1200) { $combined.Substring(0, 1200) } else { $combined }

    $result = [ordered]@{
        ok             = $true
        wrapper        = 'prepare_codex_audit'
        mode           = $mode
        sources        = $srcExists
        output_path    = $outputPath
        wrote          = $wrote
        preview        = $preview
        launches_codex = $false
        live_action    = $false
        local_only     = $true
    }
    $result | ConvertTo-Json -Depth 6
    exit 0
}
catch {
    [ordered]@{ ok = $false; wrapper = 'prepare_codex_audit'; error = $_.Exception.Message; launches_codex = $false; live_action = $false; local_only = $true } | ConvertTo-Json -Depth 4
    exit 1
}
