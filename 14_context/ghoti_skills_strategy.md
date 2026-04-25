# Ghoti Skills Strategy

Date: 2026-04-24
Branch: feat/ghoti-visible-operator-stack
Status label: strategy_only / not_runtime_wired

## Current Truth Summary

Codex plugins and skills are useful operator-side capabilities during Codex app sessions. They are not automatically wired into the Ghoti runtime, dashboard, approval queue, executor, overlay, or MCP server unless repo code proves that wiring.

Ghoti remains local-first, supervised, manual, and approval-gated. Skills do not grant autonomous computer control, posting, trading, scraping, deployment, or external service access. Any future runtime bridge must be explicit, local-first, logged, and approval-bound.

## Plugin / Skill Categories

### A. Use Now

- GitHub workflow: status checks, branch/push verification, PR/issue inspection when requested.
- Playwright/browser smoke testing: local dashboard and overlay validation only.
- Docs/reports: milestone logs, audit reports, finish-line summaries, handoff documents.
- OpenAI Docs: only for current OpenAI API/product documentation questions.

### B. Use Soon

- Jam-style bug reporting: capture UI issue evidence and reproduction notes, but do not wire it into Ghoti runtime yet.
- Spreadsheet/simulation workflows: local CSV/XLSX modeling and paper simulations.
- Local project builder: repo-local scaffolds, code generation, and validation plans with operator review.
- Production web architecture: design reviews and deployment plans, not live deployment by default.

### C. Research Only

- Content factory: ideation, scripts, review checklists, and owned-account drafts only.
- Store/e-commerce research: market/product research and planning only.
- Security/OSINT: legal, authorized, TOS-aware research only.
- OpenClaw and other multi-agent dashboards: reference/prep only, not wired into Ghoti runtime.

### D. Do Not Use / Risky / Unnecessary

- Autonomous posting, fake engagement, spam, phone-farm automation, or ban evasion.
- Autonomous real-money trading, investing, money movement, legal filing, or permit filing.
- Unsafe aerospace, weapon guidance, or implementation details for harmful systems.
- Claude Code quota/cap bypass, hidden recording, hidden cleanup, or approval-gate bypass.
- Paid/cloud/deployment plugins unless the user explicitly asks and approves scope.

## Priority Areas

- Ghoti dashboard/UI testing: use Playwright/browser skills for local route, screenshot, and interaction smoke checks.
- Overlay interaction validation: check hidden/default states, diagnostics drawer, Start/Stop Ghoti buttons, and honesty labels.
- Bug reporting with Jam: collect screenshots, reproduction steps, expected/actual behavior, and affected files; keep as operator-side evidence.
- GitHub workflow: verify branch, remote, staged files, commits, pushes, and PR state without staging runtime/private files.
- Docs/reports: keep finish-line logs append-only and grounded in validation results.
- Spreadsheets/simulations: local-only planning, paper trading, budgets, and scenario models.
- Local project builder: create repo-local artifacts and code only after explicit scope.
- Content factory: safe ideation and drafts; no autonomous posting or engagement.
- Store/e-commerce research: research and planning only; no purchases, ads, or account automation.
- Production web architecture: architecture and readiness plans; deployment only after explicit approval.
- Security/OSINT: legal, authorized, privacy-aware, approval-gated only.

## Recommended Ghoti-Specific Codex Skills

### ghoti-git-safety

**Created in milestone N+2.0 — status: skill_package_created / not_runtime_wired**
**File:** `13_prompts/codex_skills/ghoti-git-safety/SKILL.md`

- Purpose: prevent accidental staging or committing of runtime, private, third-party, or scratch files.
- When to use: before every Ghoti commit or push.
- Forbidden uses: deleting files, rewriting history, force-pushing, or staging with `git add .`.
- Validation/checks: `git status --short`, `git diff --name-status`, `git diff --cached --name-status`, forbidden-path scan.
- Output artifact/file: update `14_context/ghoti_finish_line_log.md` with git hygiene results.

### ghoti-dashboard-route-validation

**Created in milestone N+2.2 — status: skill_package_created / not_runtime_wired**
**File:** `13_prompts/codex_skills/ghoti-dashboard-route-validation/SKILL.md`

- Purpose: validate local dashboard API routes and honesty/status endpoints.
- When to use: after dashboard/server changes or before UI milestone commits.
- Forbidden uses: deployment, paid service calls, hidden state mutation beyond explicit local route tests, or changing runtime behavior just to make validation pass.
- Validation/checks: node syntax checks, duplicate-ID checks, local server smoke, required route table, API truth checks, and browser/Playwright overlay interaction smoke when available.
- Output artifact/file: append validation table to `14_context/ghoti_finish_line_log.md`.

### ghoti-overlay-ui-smoke-test

- Purpose: validate overlay rendering and interactions without claiming native always-on-top behavior.
- When to use: after changes to `overlay.html`, `overlay.css`, or `overlay.js`.
- Forbidden uses: hidden recording, autonomous clicking outside the browser test page, broad desktop control.
- Validation/checks: `/overlay` 200, no duplicate IDs, diagnostics hidden/open/close, Start/Stop Ghoti button behavior, screenshot evidence when useful.
- Output artifact/file: append overlay results to `14_context/ghoti_finish_line_log.md`.

### ghoti-finish-line-log-update

**Created in milestone N+2.1 — status: skill_package_created / not_runtime_wired**
**File:** `13_prompts/codex_skills/ghoti-finish-line-log-update/SKILL.md`

- Purpose: keep milestone history accurate and append-only.
- When to use: every milestone before commit.
- Forbidden uses: rewriting prior history to make outcomes look cleaner.
- Validation/checks: include date, branch, HEAD, commit hash, push truth, files changed, validation results, dirty files left unstaged, what is real, what is scaffold, and what remains manual.
- Output artifact/file: `14_context/ghoti_finish_line_log.md`.

### ghoti-codex-claude-handoff

- Purpose: maintain honest manual handoff between ChatGPT, Codex app, and later Claude Code.
- When to use: when creating prompt files, handoff summaries, or next-run instructions.
- Forbidden uses: claiming automatic Claude Code <-> Codex bridge, quota bypass, or hidden cross-agent control.
- Validation/checks: explicitly label `manual_handoff_only` unless runtime proof exists.
- Output artifact/file: `14_context/claude_codex_bridge_status.md` or a scoped handoff file.

### ghoti-business-research-safe

- Purpose: support legitimate business research and planning.
- When to use: market scans, competitor notes, owned-account planning, outreach drafts.
- Forbidden uses: spam, fake engagement, account farming, impersonation, scraping that violates law/TOS, or autonomous sending.
- Validation/checks: source list, assumptions, risk flags, human-review checkpoint.
- Output artifact/file: research note under `08_research/` or `14_context/`.

### ghoti-investment-simulation-safe

- Purpose: support paper simulations and decision-support analysis.
- When to use: backtests, portfolio scenarios, risk notes, market research.
- Forbidden uses: autonomous trading, money movement, personalized financial advice, or live brokerage execution.
- Validation/checks: paper/simulation label, assumptions, data source notes, risk disclaimers.
- Output artifact/file: local report or spreadsheet artifact; never runtime execution state.

### ghoti-content-factory-safe

- Purpose: produce safe content concepts, scripts, review checklists, and owned-account drafts.
- When to use: YouTube/TikTok/Instagram idea planning, scripts, editing checklists, content calendars.
- Forbidden uses: autonomous posting, fake engagement, scraping user accounts, ban evasion, or deception.
- Validation/checks: owned-account requirement, human approval before posting, platform/TOS risk notes.
- Output artifact/file: content plan under `08_research/`, `14_context/`, or a repo-local artifact folder.

## Operating Rule

Until a skill is implemented as repo code with tests, explicit route/runtime wiring, and approval-gated behavior, it remains a strategy/operator-side capability only.
