# Hermes Local Install And Provider Plan

## Current N+5.4B Truth

- Ubuntu WSL is installed.
- Hermes is available at `/home/ai_sandbox/.local/bin/hermes`.
- Verified version: `Hermes Agent v0.14.0`.
- Browser/Playwright remains degraded/not claimed unless a later safe local
  check proves it.
- Codex provider support remains pending/not proven. The presence of a Hermes
  `codex` skill is not proof of provider support.
- Telegram setup is manual later. No token should be committed or configured by
  Codex.
- No VPS is required for the current local-first path.

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

## WSL Ubuntu Troubleshooting

Prefer explicit Ubuntu commands when checking a WSL install from PowerShell:

```powershell
wsl -d Ubuntu -- bash -lc "command -v hermes && hermes --help | head -80"
wsl.exe -d Ubuntu -- bash -lc "hermes --version || true"
```

If Ubuntu opens but Hermes is not found, the installer was not completed inside
Ubuntu. After human review of the installer, run the local Ubuntu install path:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
source ~/.bashrc
command -v hermes
hermes --help
```

PowerShell's `curl` alias issue is solved by using `curl.exe`. Bash launched
from PowerShell can route to WSL on some machines, so use `wsl -d Ubuntu` or
`wsl.exe -d Ubuntu` when troubleshooting the exact distro.

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
