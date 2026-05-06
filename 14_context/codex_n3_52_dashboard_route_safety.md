# Codex N+3.52 - Dashboard Route Safety

## Route Truth

N+3.50A adds a local dashboard/read card for local orchestrator state, including a route expected as `GET /api/ghoti/local-orchestrator/status`. Syntax checks passed for the touched dashboard server and app files.

## Safety Review

The route is status-only in design. It reports local facts for prompt bus, lane locks, Obsidian vault, compact memory, Ruflo package/install state, Ollama/Gemma availability, and safety flags. No install, send, post, pay, scrape, job application, giveaway, account action, approve action, or execute action was validated or required.

The route may call local read-only status commands such as Git or Ollama checks. That remains acceptable only while it stays non-mutating.

## Must Stay Forbidden

- No npm install from dashboard refresh.
- No Ruflo command launch from dashboard refresh.
- No Ollama model pull from dashboard refresh.
- No writes to prompt bus, lane files, compact memory, Obsidian, logs, or state docs from a read route.
- No approve button.
- No execute button.
- No connector/account/live action.

## Frontend Truth

The frontend card is useful, but it needs stronger truth labels. The next implementation should expose and render:

- `bridge_auto_control = false`
- `manual_copy_paste_required = true`
- `ruflo_runtime_wired = false`
- `gemma_token_saving_ready = false` unless a model and successful draft write are proven
- `obsidian_app_accessible = false` unless app launch is proven

## Verdict

`PASS WITH HARDENING REQUIRED`

The dashboard surface appears safe/read-only, but it must not let visibility become confused with capability. Status is not orchestration. Refresh is not execution.
