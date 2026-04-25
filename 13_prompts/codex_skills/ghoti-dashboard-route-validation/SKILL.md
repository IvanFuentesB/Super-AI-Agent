# ghoti-dashboard-route-validation

**Status:** skill_package_created / not_runtime_wired
**Created:** 2026-04-25
**Branch:** feat/ghoti-visible-operator-stack

---

## Purpose

Validate the local Ghoti dashboard routes, overlay route, dashboard JavaScript syntax, duplicate DOM IDs, and basic browser overlay interactions before dashboard-facing milestone commits.

This skill turns repeated dashboard smoke checks into one reusable Codex operator-side workflow. It does not add runtime behavior, route handlers, browser automation, deployment, or autonomous execution.

---

## When to Use

Use this skill when a milestone touches or depends on:

- `01_projects/dashboard_mvp/server.js`
- `01_projects/dashboard_mvp/public/app.js`
- `01_projects/dashboard_mvp/public/overlay.js`
- `01_projects/dashboard_mvp/public/index.html`
- `01_projects/dashboard_mvp/public/overlay.html`
- Dashboard route truth, status panels, overlay behavior, Active Mode UI, approvals UI, model/tooling truth UI, or operator-console status.

Also use it before describing the dashboard or overlay as validated.

---

## Forbidden Uses

- Changing runtime behavior just to make validation pass.
- Hiding errors behind fake-green dashboard states.
- Claiming routes are healthy without actual status checks.
- Claiming browser overlay is native always-on-top.
- Claiming capture gallery is AI screen sharing; it is local screenshot frames only.
- Claiming Gemma/Ollama drives operator behavior unless a validated runtime path proves it.
- Deploying, connecting paid/cloud services, or calling non-localhost services.
- Starting hidden recording, hidden cleanup, autonomous actions, posting, scraping, trading, or external mutations.
- Staging runtime screenshots, `output/`, `.tmp-screenshots/`, runtime data, CV files, `.claude/skills/`, third-party repo contents, or scratch files created during validation.

---

## Required Route Validation Workflow

1. Start with repo truth:

```powershell
git status --short
git branch --show-current
git diff --cached --name-status
```

2. Run JavaScript syntax checks.
3. Run duplicate-ID checks for dashboard and overlay HTML.
4. Start the dashboard on a local fallback port if needed.
5. Smoke-check the required route list.
6. If Playwright or a browser skill is available, run the overlay interaction smoke.
7. Record command + result for every check.
8. Stop any fallback dashboard server process started by the validation run.
9. Confirm no runtime screenshots/output artifacts are staged.

---

## Required Server Startup / Port Handling Rules

Default dashboard port is `3210`, but the server supports `PORT`.

Use a fallback local port such as `3220`, `3221`, or another free high port when `3210` is busy. Always report the actual port used.

Safe PowerShell startup pattern:

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

Stop the process when done:

```powershell
$conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($conn) { Stop-Process -Id $conn.OwningProcess -Force }
```

Do not kill unrelated processes on other ports unless the user explicitly asks.

---

## Required Route List

Smoke-check these routes against the actual local base URL:

```text
GET /
GET /overlay
GET /api/ghoti/system/health
GET /api/ghoti/tooling/status
GET /api/ghoti/continuity/status
GET /api/ghoti/models/inventory
GET /api/ghoti/approvals?status=pending
```

PowerShell route smoke template:

```powershell
$base = "http://127.0.0.1:$port"
$paths = @(
  "/",
  "/overlay",
  "/api/ghoti/system/health",
  "/api/ghoti/tooling/status",
  "/api/ghoti/continuity/status",
  "/api/ghoti/models/inventory",
  "/api/ghoti/approvals?status=pending"
)
foreach ($path in $paths) {
  $response = Invoke-WebRequest -Uri ($base + $path) -UseBasicParsing -TimeoutSec 5
  "$path`t$($response.StatusCode)`t$($response.Headers['Content-Type'])"
}
```

Expected result: `200` for every route. For JSON routes, inspect enough of the body to verify honest shape such as `ok`, `status`, `bridge`, `models`, `available`, or `pending_count` as applicable.

---

## Required API Truth Checks

Confirm the responses do not overclaim:

- `/api/ghoti/tooling/status`: bridge remains `manual_handoff_only` unless proven otherwise.
- `/api/ghoti/models/inventory`: model/tool status remains diagnostic truth; no claim that Gemma drives operator actions.
- `/api/ghoti/continuity/status`: continuity is file/log/checkpoint based, not unlimited context.
- `/api/ghoti/approvals?status=pending`: approval state is visible and does not imply autonomous approval.
- `/api/ghoti/system/health`: health endpoint returns local dashboard truth, not deployment/cloud truth.

If a route returns `500`, malformed JSON, or false-success content, record it as a failure. Do not hide it.

---

## Required Duplicate-ID Checks

Check both HTML files:

```text
01_projects/dashboard_mvp/public/index.html
01_projects/dashboard_mvp/public/overlay.html
```

Node duplicate-ID check:

```powershell
@'
const fs = require("fs");
for (const file of ["01_projects/dashboard_mvp/public/index.html", "01_projects/dashboard_mvp/public/overlay.html"]) {
  const html = fs.readFileSync(file, "utf8");
  const ids = [...html.matchAll(/\bid=["']([^"']+)["']/g)].map((match) => match[1]);
  const seen = new Set();
  const duplicates = [];
  for (const id of ids) {
    if (seen.has(id) && !duplicates.includes(id)) duplicates.push(id);
    seen.add(id);
  }
  console.log(`${file}: ids=${ids.length} unique=${seen.size} duplicates=${duplicates.length}`);
  if (duplicates.length) {
    console.log(`duplicates=${duplicates.join(",")}`);
    process.exitCode = 1;
  }
}
'@ | node -
```

Result must be `duplicates=0` for both files.

---

## Required JavaScript Syntax Checks

Run:

```powershell
node --check 01_projects/dashboard_mvp/server.js
node --check 01_projects/dashboard_mvp/public/app.js
node --check 01_projects/dashboard_mvp/public/overlay.js
```

All must pass before committing dashboard-facing changes.

---

## Required Browser / Playwright Smoke Checks When Available

If Playwright, browser skill, or an existing repo-local browser dependency is available, run an overlay interaction smoke against the same local port.

Required checks:

- Open `/overlay`.
- Verify diagnostics drawer is hidden by default.
- Open diagnostics.
- Close diagnostics.
- Click Start Ghoti if safe/local-only.
- Click Stop Ghoti if safe/local-only.
- Verify local-only / approval-gated / browser-overlay-not-native wording remains visible.
- Report whether a capture/observer summary exists or is not implemented.
- Record browser console/page errors if the tool exposes them.

Do not use this check to control arbitrary desktop apps. Keep it inside the local browser target.

Example Playwright script shape:

```powershell
@'
const { chromium } = require("playwright");
(async () => {
  const base = "http://127.0.0.1:3221";
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 900, height: 700 } });
  const errors = [];
  page.on("console", (msg) => { if (msg.type() === "error") errors.push(msg.text()); });
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto(base + "/overlay", { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1000);
  const initial = await page.evaluate(() => ({
    diagHidden: document.getElementById("diag-drawer")?.hidden,
    diagDisplay: getComputedStyle(document.getElementById("diag-drawer")).display,
    honesty: document.body.innerText.includes("Browser overlay") && document.body.innerText.includes("not a native always-on-top"),
    localOnly: document.body.innerText.includes("LOCAL ONLY"),
    approvalGated: document.body.innerText.includes("APPROVAL GATED")
  }));
  await page.click("#dock-diag-btn");
  await page.waitForTimeout(250);
  const afterOpen = await page.evaluate(() => ({ diagHidden: document.getElementById("diag-drawer")?.hidden }));
  await page.click("#diag-close-btn");
  await page.waitForTimeout(250);
  const afterClose = await page.evaluate(() => ({ diagHidden: document.getElementById("diag-drawer")?.hidden }));
  await browser.close();
  console.log(JSON.stringify({ initial, afterOpen, afterClose, consoleErrorCount: errors.length, errors }, null, 2));
})();
'@ | node -
```

If Playwright is unavailable, record `NOT RUN — Playwright/browser automation unavailable` and continue with route/static validation.

---

## Required Failure Handling

If a validation fails:

1. Record the exact command and failure.
2. Do not claim the route or UI is healthy.
3. Do not change unrelated runtime behavior to force green.
4. Fix only if the milestone explicitly allows changes to the affected file.
5. Re-run the failed check after a narrow fix.
6. If no fix is allowed, leave it documented as a blocker.

If validation creates runtime files:

1. Leave them unstaged.
2. Confirm they are ignored or listed under intentionally unstaged files.
3. Do not delete them unless the user explicitly asked for cleanup.

---

## Required Final Report Format

Final report should include:

```markdown
- branch
- previous HEAD
- new commit hash, if any
- pushed yes/no
- dashboard port used
- JavaScript syntax checks
- duplicate-ID checks
- route smoke results
- API truth checks
- browser/Playwright interaction smoke result
- files changed
- files intentionally not staged
- runtime wiring truth
- next recommended milestone
```

---

*Status: skill_package_created / not_runtime_wired*

*This skill is a Codex operator-side workflow document. It is not wired into the Ghoti runtime, dashboard, approval queue, MCP server, or executor.*
