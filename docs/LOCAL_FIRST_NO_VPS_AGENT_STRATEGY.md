# Local-First No-VPS Agent Strategy

The user does not want to pay for a VPS right now. Ghoti should treat the
Windows `ai_sandbox` profile as the local operator machine.

## Current Preference

- Local-first background tasks.
- No recurring paid infrastructure.
- No Hostinger or VPS assumption.
- Telegram requires manual user setup later.
- Always-on cloud/VPS can be a future optional lane, not the default path.
- Ubuntu WSL is the preferred local Linux path when Hermes needs a Linux shell.
- Use `wsl -d Ubuntu` or `wsl.exe -d Ubuntu` for distro-specific checks.
- If Ubuntu opens but Hermes is not found, Hermes was not installed inside that
  Ubuntu distro yet.

Manual Ubuntu recovery path after reviewing the installer:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
source ~/.bashrc
command -v hermes
hermes --help
```

PowerShell `curl` can mean `Invoke-WebRequest`; use `curl.exe` for downloads.
Bash from PowerShell can route to WSL, so prefer explicit `wsl -d Ubuntu`
commands when validating Hermes inside Ubuntu.

## NetworkChuck-Style Preference Note

The user referenced NetworkChuck-style Hermes/Telegram/local agent workflow
preferences. This document records the preference only; it does not claim exact
video details. The practical mapping is: local machine first, manual Telegram
setup, no paid VPS until there is a clear reason.

## Future Cloud Decision

If cloud hosting becomes necessary later, compare free or low-cost options
before buying a VPS:

- local scheduled tasks
- free-tier web hosting
- managed serverless functions
- low-cost queues/cache
- paid VPS only if the workload truly needs always-on state
