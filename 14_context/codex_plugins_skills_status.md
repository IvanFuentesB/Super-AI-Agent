# Codex Plugins And Skills Status

Date: 2026-04-24
Branch: feat/ghoti-visible-operator-stack
Current HEAD at audit start: 4f1c8c5
Milestone: N+1.8 Overlay Triage + Skills/Plugin Truth Pass

## Core Truth

Codex app can use installed plugins and skills during this chat/session. That does not mean Ghoti runtime can call those plugins automatically.

Ghoti runtime integration must be proven by repo code, routes, tests, and approval-gated behavior before any plugin or skill is described as wired.

## Plugin / Tool Surface Truth

| Plugin or service | Current truth | Ghoti runtime wired? | N+1.8 action |
|---|---|---:|---|
| GitHub | Available to Codex context and useful for repo/PR/branch work | No automatic runtime wiring proven | No GitHub app action needed beyond git push |
| Neon Postgres | Tool namespace available in this Codex session | No | No database action performed |
| Vercel | Mentioned as an available deployment capability in prior context/tool discovery | No | Not used; no deployment |
| Cloudflare | Mentioned as an available deployment capability in prior context/tool discovery | No | Not used; no deployment |
| Sentry | Not exposed as a callable tool in this session | No | Not used |
| Hugging Face | Not exposed as a callable tool in this session | No | Not used |
| Cloudinary | Not exposed as a callable tool in this session | No | Not used |
| Expo | Not exposed as a callable tool in this session | No | Not used |
| Superpowers | Not exposed as a callable tool in this session | No | Not used |
| Computer Use | No plugin named exactly "Computer Use" was found or proven | No | Do not assume it exists |

## Useful Codex Skills Observed

These are available to Codex as session skills, not Ghoti runtime modules:

- Playwright: useful for local dashboard/browser smoke testing.
- OpenAI Docs: useful for current OpenAI API/docs questions.
- Skill Creator / Plugin Creator / Skill Installer: useful for local Codex extension work.
- Jupyter Notebook: useful for notebooks and experiments.
- Spreadsheet / Excel: useful for CSV/XLSX workflows.
- Doc / PDF: useful for document/PDF work.
- ImageGen: useful for generated bitmap assets.
- GitHub skills: useful for PR/issue/CI workflows when GitHub work is requested.
- Cloudflare/Vercel deploy skills: useful later for deployment, but out of scope for N+1.8.

## Deployment And External Service Boundary

- No deployment was performed.
- No external paid service was connected.
- No API keys or secrets were added.
- No Neon, Vercel, Cloudflare, Sentry, Hugging Face, Cloudinary, or Expo runtime integration was added.

## Ghoti Safety Boundary

- Skills/plugins do not bypass approval gates.
- Skills/plugins do not authorize autonomous computer control.
- Skills/plugins do not make OpenClaw wired.
- Skills/plugins do not enable posting automation, fake engagement, phone-farm automation, trading execution, scraping automation, or quota/cap bypass.
- Any future runtime plugin bridge must be designed as a local adapter with explicit operator approval and payload logging.
