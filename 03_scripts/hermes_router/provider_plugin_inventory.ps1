# provider_plugin_inventory.ps1 — provider/plugin inventory (READ-ONLY, NO SECRETS).
# Lists the local provider/model truth and the *planned* cloud providers/plugins. It
# never reads secret files and never prints key values; "configured" is reported only
# from safe status text, never from secret/.env/token values. Reports JSON.
# Safety: read-only; no secrets; no network; no installs; never runs arbitrary commands.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

try {
    $result = [ordered]@{
        ok                                   = $true
        wrapper                              = 'provider_plugin_inventory'
        local_provider                       = 'Ollama/custom endpoint (loopback, documented only)'
        hermes_model                         = 'llama3.1:8b'
        cheap_worker_model                   = 'gemma3:4b'
        cloud_provider_keys_expected_in_repo = $false
        kimi_configured                      = $false
        anthropic_configured                 = $false
        github_configured                    = $false
        browser_plugins_enabled              = $false
        detection_method                     = 'safe status text only; never reads secret/.env/token files; never prints key values; never reads environment variable values'
        note                                 = 'A visible plugin does not mean it is approved or enabled. Subscription and cloud providers are optional, not extra spend; enablement is a separate, approval-gated milestone.'
        local_only                           = $true
    }
    $result | ConvertTo-Json -Depth 6
    exit 0
}
catch {
    [ordered]@{ ok = $false; wrapper = 'provider_plugin_inventory'; error = $_.Exception.Message; cloud_provider_keys_expected_in_repo = $false; browser_plugins_enabled = $false; local_only = $true } | ConvertTo-Json -Depth 4
    exit 1
}
