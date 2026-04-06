# Browser Playground

Small local Playwright playground for deterministic browser-control smoke checks.

## What It Does

- opens a local demo page
- clicks one visible button
- verifies the page state changes
- captures a screenshot artifact

## Modes

- headless smoke mode: fast verification with no visible browser window
- visible demo mode: opens Chromium, slows the interaction down, and keeps the window open briefly so the click is easy to see

## How To Run

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only\01_projects\browser_playground
npm install --package-lock=false
npm run install-browsers
npm run smoke
npm run smoke:visible
```

## Artifact

Both modes should produce:

- `01_projects/browser_playground/artifacts/smoke-click.png`

## What It Does Not Do Yet

- no live-site automation
- no browser executor loop
- no desktop or Windows cursor control
- no approval-gated outbound browser workflows
