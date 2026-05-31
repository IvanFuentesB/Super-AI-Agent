# run_gemma_summary.ps1 — Hermes router wrapper (DRY-RUN ONLY).
# Describes the local Gemma summary that Hermes WOULD request. It does not require
# Ollama, does not fail if Gemma is unavailable, and does NOT contact any endpoint.
# The local model call is intentionally not implemented in N+6.6A.
# Safety: no network; no model download; no package install; no secrets; read-only;
# never runs arbitrary commands.

param(
    [string]$InputPath = '',
    [switch]$AllowLocalModel
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$ScriptDir = $PSScriptRoot
$RepoRoot  = Split-Path -Parent (Split-Path -Parent $ScriptDir)

try {
    $hasInput   = -not [string]::IsNullOrWhiteSpace($InputPath)
    $inputExists = $false
    if ($hasInput) { $inputExists = Test-Path -LiteralPath $InputPath -PathType Leaf }
    $wouldSummarize = if ($hasInput) { $InputPath } else { '(no input path provided; dry-run describes the intended summary only)' }

    $result = [ordered]@{
        ok                            = $true
        wrapper                       = 'run_gemma_summary'
        mode                          = 'dry_run'
        model                         = 'gemma3:4b'
        endpoint                      = 'http://127.0.0.1:11434/v1'
        would_summarize               = $wouldSummarize
        input_exists                  = $inputExists
        allow_local_model             = $AllowLocalModel.IsPresent
        local_model_call_implemented  = $false
        model_downloaded              = $false
        network_used                  = $false
        live_action                   = $false
        local_only                    = $true
        note                          = 'Local model call is intentionally NOT implemented in N+6.6A. This wrapper only describes the intended summary. The endpoint is loopback and is never contacted.'
    }
    $result | ConvertTo-Json -Depth 6
    exit 0
}
catch {
    [ordered]@{ ok = $false; wrapper = 'run_gemma_summary'; error = $_.Exception.Message; network_used = $false; live_action = $false; local_only = $true } | ConvertTo-Json -Depth 4
    exit 1
}
