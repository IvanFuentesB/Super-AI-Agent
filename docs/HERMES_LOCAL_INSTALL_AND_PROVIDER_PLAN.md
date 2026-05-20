# Hermes Local Install And Provider Plan

## Official Installer

- Official installer URL: `https://hermes-agent.nousresearch.com/install.sh`
- The installer may be downloaded for inspection, but it must not be executed
  blindly.
- On Windows PowerShell, use `curl.exe`, not the `curl` alias for
  `Invoke-WebRequest`.

## Local-First Setup

- Target machine: the Windows `ai_sandbox` user profile.
- Paid VPS required: no.
- VPS used: no.
- Docker is optional only; this milestone does not require Docker, a VPS, or an
  always-on paid host.
- Git Bash or WSL may be used only as local shells for the installer after
  human review.

## Provider Truth

Codex is the preferred provider if Hermes supports it. Codex provider support
is currently pending / not verified until Hermes is installed or official
provider documentation is inspected. Do not claim Codex support until a
non-interactive Hermes command or official local docs verify it.

Fallback planning:

- Use local Gemma/Ollama as cheap summarization/classification worker brains.
- Use ChatGPT and Claude for planning/reasoning when manually invoked by the
  human.
- Keep Claude Code as the implementation lane when available.
- Keep Codex as the audit/verification lane.

## Telegram Boundary

Telegram setup is later/manual. The user must create and provide the bot token
and chat ID outside git. No Telegram action should run until a human approves
the setup and stores secrets locally.

## Approval Gates

- No autonomous live provider launch.
- No provider tokens committed.
- No Telegram tokens committed.
- No live APIs connected in this milestone.
- No desktop or account action without a later audited approval gate.
