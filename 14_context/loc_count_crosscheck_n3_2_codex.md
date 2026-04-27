# LOC Count Crosscheck - N+3.2 Codex

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Status label: tracked_file_crosscheck / no_runtime_changes / not_runtime_wired

## Summary

Codex counted git-tracked text files only.

| Metric | Count |
|---|---:|
| Total files counted | 386 |
| Total lines counted | 53,605 |

Claude's existing report at `14_context/ghoti_code_line_count_report.md` reports:

| Metric | Count |
|---|---:|
| Git-tracked text files counted | 386 |
| Total lines | 53,631 |

Difference: Codex counted 26 fewer lines. The file count matches. The small line-count difference appears consistent with a changed tracked tree and/or different newline counting behavior between the two scripts. Codex did not edit Claude's report.

## Lines By Extension / Language

| Extension / language | Files | Lines |
|---|---:|---:|
| Markdown `.md` | 202 | 14,597 |
| Python `.py` | 34 | 13,494 |
| JavaScript `.js` | 4 | 12,279 |
| PowerShell `.ps1` | 10 | 7,489 |
| JSON `.json` | 47 | 2,426 |
| HTML `.html` | 3 | 1,599 |
| CSS `.css` | 2 | 1,443 |
| `.gitignore` | 1 | 96 |
| `.gitkeep` | 78 | 77 |
| YAML `.yaml` | 2 | 66 |
| JSONL `.jsonl` | 1 | 23 |
| TOML `.toml` | 1 | 16 |
| No extension | 1 | 0 |

## Top 20 Largest Tracked Text Files

| Rank | Lines | File |
|---:|---:|---|
| 1 | 6,155 | `01_projects/dashboard_mvp/public/app.js` |
| 2 | 5,786 | `01_projects/dashboard_mvp/server.js` |
| 3 | 3,596 | `14_context/ghoti_finish_line_log.md` |
| 4 | 3,146 | `01_projects/runtime_mvp/src/super_ai_agent/queue.py` |
| 5 | 3,059 | `01_projects/runtime_mvp/src/super_ai_agent/cli.py` |
| 6 | 2,376 | `01_projects/desktop_playground/desktop_bridge_actions.ps1` |
| 7 | 2,202 | `03_scripts/check_runtime_mvp.ps1` |
| 8 | 1,776 | `03_scripts/check_dashboard_mvp.ps1` |
| 9 | 1,385 | `01_projects/dashboard_mvp/public/index.html` |
| 10 | 1,066 | `01_projects/dashboard_mvp/public/styles.css` |
| 11 | 841 | `01_projects/runtime_mvp/src/super_ai_agent/operator_loop.py` |
| 12 | 693 | `01_projects/mcp_server/server.py` |
| 13 | 582 | `01_projects/desktop_playground/check_desktop_playground.ps1` |
| 14 | 542 | `01_projects/runtime_mvp/src/super_ai_agent/action_intent.py` |
| 15 | 539 | `01_projects/runtime_mvp/src/super_ai_agent/relay_loop.py` |
| 16 | 513 | `01_projects/runtime_mvp/src/super_ai_agent/multi_agent_mvp.py` |
| 17 | 383 | `01_projects/runtime_mvp/src/super_ai_agent/storage.py` |
| 18 | 377 | `01_projects/dashboard_mvp/public/overlay.css` |
| 19 | 374 | `13_prompts/codex_skills/ghoti-business-research-safe/SKILL.md` |
| 20 | 371 | `01_projects/runtime_mvp/src/super_ai_agent/action_demo.py` |

## Exact Command / Script Used

PowerShell script:

```powershell
$files = git ls-files
$binaryExt = @(
  ".png",".jpg",".jpeg",".gif",".webp",".ico",".pdf",".docx",".zip",".7z",
  ".exe",".dll",".pyd",".so",".dylib",".mp4",".mov",".avi",".wav",".mp3",
  ".safetensors",".onnx",".bin",".db",".sqlite",".sqlite3"
)
$excludeRegex = @(
  "^21_repos/third_party/evals/",
  "^output/",
  "^node_modules/",
  "/__pycache__/",
  "^__pycache__/",
  "^C:/tmp/",
  "^C:\\tmp\\"
)

$rows = foreach ($f in $files) {
  $path = $f -replace "\\","/"
  $ext = [System.IO.Path]::GetExtension($f).ToLowerInvariant()
  if ($binaryExt -contains $ext) { continue }
  $skip = $false
  foreach ($rx in $excludeRegex) {
    if ($path -match $rx) { $skip = $true; break }
  }
  if ($skip) { continue }
  if (-not (Test-Path -LiteralPath $f -PathType Leaf)) { continue }
  try {
    $lineCount = (Get-Content -LiteralPath $f -ErrorAction Stop | Measure-Object -Line).Lines
  } catch {
    continue
  }
  [pscustomobject]@{
    File = $f
    Ext = if ($ext) { $ext } else { "[no extension]" }
    Lines = $lineCount
  }
}

$rows | Measure-Object Lines -Sum
$rows | Group-Object Ext | ForEach-Object {
  [pscustomobject]@{
    Ext = $_.Name
    Files = $_.Count
    Lines = ($_.Group | Measure-Object Lines -Sum).Sum
  }
} | Sort-Object Lines -Descending
$rows | Sort-Object Lines -Descending | Select-Object -First 20
```

## Exclusions

- `21_repos/third_party/evals/`
- `output/`
- CV/docx and other binary files
- images and media binaries
- `node_modules`
- `__pycache__`
- `C:\tmp` build outputs

## Warning / Interpretation

- This is a crosscheck, not the canonical report.
- Claude's LOC report and Codex's crosscheck agree on file count and are within 0.05% on total lines.
- If exact reproducibility matters, the project should adopt one committed LOC script and one newline-counting rule.
