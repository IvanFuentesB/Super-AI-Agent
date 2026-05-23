# Hermes Safe Next Steps

        Hermes workflow readiness: 58%.

        ## Safe probes only

        - `wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; command -v hermes || true"`
- `wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes --version || true"`
- `wsl -d Ubuntu -- bash -lc "source ~/.bashrc >/dev/null 2>&1 || true; hermes skills list | head -120 || true"`
- `python 03_scripts/hermes_local_bootstrap.py --status --json`
- `python 03_scripts/hermes_agent_workflow_bridge.py --status --json`
- `python 03_scripts/hermes_agent_workflow_bridge.py --write-readiness --json`

        ## Human next steps

        - Run the Hermes bridge status command and review generated files.
- Review the Hermes skills index to understand what is visible locally.
- Only after human-approved setup, decide whether to verify provider support.
- Keep Codex provider verification manual until a safe Hermes command proves support.
- Keep Telegram setup manual later; do not place tokens in git.
- Treat browser/Playwright as degraded/not claimed until a later remediation milestone verifies it.

        ## Blocked commands

        - `hermes setup`
- `hermes login`
- `hermes auth`
- `hermes pairing`
- `provider config`
- `Telegram setup`
- `token commands`
- `live provider API calls`
- `browser automation`
