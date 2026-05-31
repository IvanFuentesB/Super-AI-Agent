# Odysseus Feature Intake (candidate-only)

Source: `https://github.com/pewdiepie-archdaemon/odysseus`

Status: **candidate_only**, documentation only. Odysseus is **not cloned**, not
installed, and not run. This note records the useful patterns from its public
README so Ghoti can adopt the *ideas* through the normal gated intake pipeline.
Listing a feature here is **not** adoption and enables nothing.

## What Odysseus is (as documented by its README)

A self-hosted, local-first AI workspace. The patterns worth extracting:

- **Self-hosted AI workspace** - a local-first workspace UX, one place for the user's
  AI tools.
- **Chat with local/API models** - talk to local models (and, optionally, API models).
- **Agent with tools** - an agent that can call tools under control.
- **Cookbook for model/hardware fit** - guidance on which model fits which hardware.
- **Deep Research reports** - structured, multi-section research output.
- **Model compare / AI council** - blind, council-style comparison of model answers.
- **Documents editor with AI assist** - a document editor for drafting/revising docs.
- **Memory / skills** - durable memory and reusable skills.
- **Email triage** - summaries, urgency scoring, tags, reply drafts, and spam handling.
- **Notes / tasks / reminders** - lightweight productivity capture.
- **Calendar** - schedule awareness.
- **Mobile / PWA** - installable progressive web app for phone use.
- **Bundled services** - ChromaDB (vectors), SearXNG (search), ntfy (notifications) and
  similar local services packaged together.

## Security warnings carried over from Odysseus' README

Odysseus ships a **powerful admin console**. Its own docs warn operators to:

- **Protect secrets** - guard the environment file (`.env`), data, logs, and tokens.
- **Never expose it publicly without authentication (auth) and HTTPS** - no public
  exposure of the admin console or services without auth + HTTPS in front.

Ghoti honours these warnings up front: no admin console is exposed, no secret/.env/
token is stored in the repo or vault, and nothing is published to the public internet.

## How Ghoti will adopt the ideas (not the install)

Each useful pattern becomes its own **candidate_only** module in
`tool_candidate_registry_additions_n6_7b.json`, evaluated through the N+6.7A intake
pipeline (inspect -> classify -> sandbox -> integrate). Nothing is installed,
cloned, run, or wired into the runtime by this milestone. The personal-comms ideas
(email/WhatsApp/calendar/style memory) follow the strict draft-only rules in
`personal_comms_agent_roadmap.md`; the workspace ideas (AI council, model cookbook,
deep research, document editor) follow `ai_council_and_model_cookbook_roadmap.md`.

## Not enabled by this intake

- Odysseus is **not cloned**, not installed, and not run; no external code executes.
- No email login, no WhatsApp login, no Telegram setup, no MCP install.
- No browser-use, no computer-use, no auto-send, no social posting.
- No secrets stored; `main` is untouched.
