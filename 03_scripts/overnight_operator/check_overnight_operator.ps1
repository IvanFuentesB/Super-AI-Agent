$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$required = @(
  "03_scripts/overnight_operator/ghoti_prompt_packet_builder.py",
  "03_scripts/overnight_operator/ghoti_operator_queue.py",
  "03_scripts/overnight_operator/ghoti_repo_execution_sandbox.py",
  "03_scripts/overnight_operator/ecc_agent_setup_inspector.py",
  "03_scripts/overnight_operator/ghoti_clipboard_relay.ps1",
  "14_context/overnight_operator/allowlists/allowed_repos_n6_19a.json",
  "14_context/overnight_operator/allowlists/allowed_commands_n6_19a.json",
  "23_configs/overnight_operator.example.json"
)

$missing = @()
foreach ($rel in $required) {
  if (-not (Test-Path -LiteralPath (Join-Path $repoRoot.Path $rel))) {
    $missing += $rel
  }
}

$flags = Get-Content -LiteralPath (Join-Path $repoRoot.Path "23_configs/ghoti_feature_flags.example.json") -Raw | ConvertFrom-Json
$flagNames = @(
  "overnight_operator_enabled",
  "clipboard_relay_enabled",
  "clipboard_paste_enabled",
  "approved_window_paste_enabled",
  "auto_submit_enabled",
  "external_repo_execution_enabled",
  "ecc_integration_enabled",
  "gbrain_integration_enabled",
  "markitdown_sandbox_enabled",
  "documenso_overleaf_docs_lane_enabled",
  "unattended_mode_enabled",
  "overnight_auto_merge_enabled"
)
$falseFlags = @()
foreach ($name in $flagNames) {
  if ($flags.$name -eq $false) { $falseFlags += $name }
}

[ordered]@{
  ok = ($missing.Count -eq 0 -and $falseFlags.Count -eq $flagNames.Count)
  milestone = "N+6.19A"
  wrapper = "check_overnight_operator"
  missing = $missing
  risky_flags_default_false = ($falseFlags.Count -eq $flagNames.Count)
  feature_flags_checked = $flagNames
  safety = [ordered]@{
    no_live_agent_launch = $true
    no_mcp_setup = $true
    no_live_browser = $true
    no_os_click_type = $true
    no_auto_submit = $true
    no_main_push_from_operator = $true
  }
} | ConvertTo-Json -Depth 6
