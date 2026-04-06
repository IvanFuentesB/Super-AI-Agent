# Browser Playground

Small local Playwright playground for deterministic browser-control smoke checks.

## What It Does

- opens a local demo page
- clicks one visible button
- verifies the page state changes
- captures a screenshot artifact

## How To Run

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only\01_projects\browser_playground
npm install --package-lock=false
npm run install-browsers
npm run smoke
```

## Artifact

The smoke script should produce:

- `01_projects/browser_playground/artifacts/smoke-click.png`

## What It Does Not Do Yet

- no live-site automation
- no browser executor loop
- no desktop control
- no approval-gated outbound browser workflows
