# ghoti-overlay-ui-smoke-test

**Status:** skill_package_created / not_runtime_wired
**Created:** 2026-04-25
**Branch:** feat/ghoti-visible-operator-stack

---

## Purpose

Validate the Ghoti browser overlay UI in a repeatable, local-only way using route checks plus browser/Playwright interaction smoke tests.

This skill focuses on overlay behavior only: `/overlay`, diagnostics drawer, Start/Stop Ghoti button behavior, visible safety wording, and console/page errors. It does not create a native overlay, wire runtime automation, or expand Ghoti autonomy.

---

## When to Use

Use this skill when a milestone touches or depends on:

- `01_projects/dashboard_mvp/public/overlay.html`
- `01_projects/dashboard_mvp/public/overlay.css`
- `01_projects/dashboard_mvp/public/overlay.js`
- `01_projects/dashboard_mvp/server.js` overlay routing or Active Mode endpoints
- Presence overlay wording, diagnostics behavior, Start/Stop Ghoti UI, overlay route truth, or browser overlay status.

Also use it before saying the overlay interaction behavior was validated.

---

## Forbidden Uses

- Claiming native always-on-top overlay behavior unless a native overlay is actually tested.
- Claiming AI screen sharing when only local capture gallery or local screenshot frames exist.
- Changing runtime behavior just to make smoke tests pass.
- Hiding errors, console failures, route failures, or stale-state observations.
- Starting hidden recording, hidden cleanup, autonomous actions, posting, scraping, trading, or external mutations.
- Weakening approval-gated behavior or treating Start Ghoti as permission for autonomous action.
- Deploying or connecting external services.
- Staging Playwright screenshots, traces, videos, runtime data, `.tmp-screenshots/`, `output/`, or other artifacts unless the user explicitly asks.
- Testing arbitrary desktop apps from this workflow. Keep browser automation inside the local dashboard/overlay target.

---

## Required Overlay Smoke Workflow

1. Start with repo truth:

```powershell
git status --short
git branch --show-current
git diff --cached --name-status
```

2. Run static checks:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/overlay.js
```

3. Start the dashboard server on an available local port.
4. Confirm `GET /overlay` returns `200`.
5. If browser/Playwright automation is available, run the interaction smoke checks.
6. Confirm Active Mode is stopped at the end if the test clicked Start Ghoti.
7. Record command + result for every check.
8. Stop any fallback dashboard server process started by this validation.
9. Confirm no screenshots, videos, traces, runtime data, or output artifacts are staged.

---

## Required Server / Port Rules

The dashboard defaults to port `3210`, but `server.js` supports `PORT`.

Use a fallback local port such as `3220`, `3221`, or another free high port when needed. Always report the exact port used.

Safe startup pattern:

```powershell
$port = 3221
$existing = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($existing) {
  Stop-Process -Id $existing.OwningProcess -Force
  Start-Sleep -Milliseconds 500
}
$proc = Start-Process -FilePath node -ArgumentList 'server.js' -WorkingDirectory 'C:\Users\ai_sandbox\Documents\AI_Managed_Only\01_projects\dashboard_mvp' -PassThru -WindowStyle Hidden -Environment @{ PORT = "$port" }
Start-Sleep -Seconds 2
```

Safe stop pattern:

```powershell
$conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($conn) { Stop-Process -Id $conn.OwningProcess -Force }
```

Do not kill unrelated processes on other ports unless the user explicitly asks.

---

## Required Browser / Playwright Checks

When Playwright or browser automation is available, verify:

- Open `/overlay`.
- Overlay route returns `200`.
- `#operator-dock` exists and is visible.
- `#diag-drawer` is hidden by default.
- Click `#dock-diag-btn`.
- Verify diagnostics drawer opens.
- Click `#diag-close-btn`.
- Verify diagnostics drawer closes.
- Click Start Ghoti only if it is safe/local-only.
- Click `#dock-start-btn` only if safe/local-only.
- Verify running state truthfully, using visible UI and/or `GET /api/ghoti/active-state`.
- Click Stop Ghoti only if it is safe/local-only.
- Click `#dock-start-btn` again to stop Ghoti only if safe/local-only.
- Verify Active Mode/API state returns to `active:false` / `mode:idle` if the route exists.
- Verify visible wording includes local-only and approval-gated labels when present.
- Verify visible wording says the overlay is browser-based / not a native always-on-top window when present.
- Report whether capture/observer summary exists or is not implemented.

Current expected overlay selectors:

```text
#operator-dock
#dock-start-btn
#dock-diag-btn
#diag-drawer
#diag-close-btn
```

---

## Required Console / Page Error Checks

Capture browser console errors and page errors if the tool exposes them.

Record:

- `consoleErrorCount`
- any page errors
- whether errors are blocking or non-blocking

If console/page errors occur, do not call the overlay smoke a clean pass. Record the exact messages.

---

## Required Screenshot / Artifact Handling Rules

Screenshots can be useful for manual inspection, but they are artifacts.

Rules:

- Store temporary screenshots under an already ignored output/runtime location only.
- Do not stage `output/`, `.tmp-screenshots/`, Playwright traces, videos, or screenshots.
- If a screenshot is important evidence, mention its local path in the report instead of committing it.
- Do not delete artifacts unless the user explicitly asks for cleanup.

---

## Required Honest Wording Rules

Every report using this skill must preserve these truths:

- Browser overlay is browser-based, not native always-on-top.
- Capture gallery means local screenshot frames saved on this machine, not AI screen sharing.
- Start Ghoti does not authorize autonomous execution.
- Ghoti remains local-first, supervised, and approval-gated.
- Gemma/Ollama diagnostic status does not mean the model drives operator actions.
- Codex skills/plugins are operator-session capabilities, not Ghoti runtime wiring unless proven.

---

## Example Playwright Smoke Script

Run from a folder where `playwright` is available, such as the repo-local browser playground if installed.

```powershell
@'
const { chromium } = require("playwright");

(async () => {
  const base = "http://127.0.0.1:3221";
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 900, height: 700 } });
  const errors = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));

  const response = await page.goto(base + "/overlay", { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1000);

  const initial = await page.evaluate(() => ({
    status: "initial",
    routeOk: true,
    dockVisible: getComputedStyle(document.getElementById("operator-dock")).display !== "none",
    diagHidden: document.getElementById("diag-drawer")?.hidden,
    diagDisplay: getComputedStyle(document.getElementById("diag-drawer")).display,
    localOnly: document.body.innerText.includes("LOCAL ONLY"),
    approvalGated: document.body.innerText.includes("APPROVAL GATED"),
    browserOverlayTruth: document.body.innerText.includes("Browser overlay") && document.body.innerText.includes("not a native always-on-top")
  }));

  await page.click("#dock-diag-btn");
  await page.waitForTimeout(300);
  const afterOpen = await page.evaluate(() => ({
    diagHidden: document.getElementById("diag-drawer")?.hidden,
    diagDisplay: getComputedStyle(document.getElementById("diag-drawer")).display
  }));

  await page.click("#diag-close-btn");
  await page.waitForTimeout(300);
  const afterClose = await page.evaluate(() => ({
    diagHidden: document.getElementById("diag-drawer")?.hidden,
    diagDisplay: getComputedStyle(document.getElementById("diag-drawer")).display
  }));

  await page.click("#dock-start-btn");
  await page.waitForTimeout(1000);
  const afterStart = await page.evaluate(() => ({
    buttonText: document.getElementById("dock-start-btn")?.textContent?.trim(),
    bodyText: document.body.innerText
  }));

  await page.click("#dock-start-btn");
  await page.waitForTimeout(1000);
  const afterStop = await page.evaluate(() => ({
    buttonText: document.getElementById("dock-start-btn")?.textContent?.trim(),
    bodyText: document.body.innerText
  }));

  const activeState = await page.evaluate(async () => {
    const res = await fetch("/api/ghoti/active-state");
    return res.ok ? await res.json() : { ok: false, status: res.status };
  });

  await browser.close();

  console.log(JSON.stringify({
    routeStatus: response?.status(),
    initial,
    afterOpen,
    afterClose,
    afterStart,
    afterStop,
    activeState,
    captureObserverSummary: "report manually: exists or not_implemented",
    consoleErrorCount: errors.length,
    errors
  }, null, 2));
})();
'@ | node -
```

Pass criteria:

- `routeStatus` is `200`.
- Diagnostics hidden by default.
- Diagnostics opens and closes.
- Start/Stop Ghoti returns Active Mode to idle/off state by the end.
- Local-only / approval-gated / browser-overlay-not-native wording is visible when present.
- `consoleErrorCount` is `0`.

---

## Required Failure Handling

If a check fails:

1. Record the exact check, command, and failure.
2. Do not claim a clean pass.
3. Do not change unrelated runtime behavior to force green.
4. If the milestone allows overlay edits, fix only the smallest affected overlay file.
5. Re-run the failed smoke step after any fix.
6. If no fix is allowed, document the blocker and leave code unchanged.

If Start Ghoti succeeds but Stop Ghoti fails:

1. Try the explicit local API stop once:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/ghoti/active/stop" -Method Post
```

2. Re-check `GET /api/ghoti/active-state`.
3. Report the failure honestly.

---

## Required Final Report Format

```markdown
- branch
- previous HEAD
- new commit hash, if any
- pushed yes/no
- overlay port used
- overlay route result
- diagnostics hidden/open/close result
- Start/Stop Ghoti result
- Active Mode final state
- local-only / approval-gated / browser-overlay wording result
- console/page error result
- capture/observer summary truth
- files changed
- artifacts created but not staged
- runtime wiring truth
- dirty files intentionally left unstaged
- next recommended milestone
```

---

*Status: skill_package_created / not_runtime_wired*

*This skill is a Codex operator-side workflow document. It is not wired into the Ghoti runtime, dashboard, approval queue, MCP server, or executor.*
