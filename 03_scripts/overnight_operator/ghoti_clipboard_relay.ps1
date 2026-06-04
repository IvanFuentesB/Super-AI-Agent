param(
  [Parameter(Mandatory=$true)]
  [string]$InputFile,
  [switch]$DryRun,
  [switch]$Copy
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$inputPath = Resolve-Path -LiteralPath $InputFile

if (-not $inputPath.Path.StartsWith($repoRoot.Path)) {
  throw "InputFile must be inside the Ghoti repo"
}

$text = Get-Content -LiteralPath $inputPath.Path -Raw
$result = [ordered]@{
  ok = $true
  milestone = "N+6.19A"
  tool = "ghoti_clipboard_relay"
  input_file = (Resolve-Path -LiteralPath $inputPath.Path -Relative)
  chars = $text.Length
  dry_run = [bool]$DryRun
  copied_to_clipboard = $false
  pasted_into_app = $false
  auto_submitted = $false
  os_click_type_used = $false
  safety = [ordered]@{
    local_only = $true
    reads_secret_values = $false
    paste_enabled = $false
    auto_submit_enabled = $false
    app_window_control = $false
  }
}

if ($Copy -and -not $DryRun) {
  Set-Clipboard -Value $text
  $result.copied_to_clipboard = $true
}

$result | ConvertTo-Json -Depth 6
