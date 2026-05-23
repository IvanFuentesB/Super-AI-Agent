# Hermes Manual Provider Setup Checklist

This checklist is for a later human-approved setup. Codex must not run these setup actions in N+5.8A.

## Safe Before Setup

- Run `python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json`.
- Run `python 03_scripts/hermes_agent_workflow_bridge.py --skills-index --json`.
- Review `14_context/hermes_workflow/generated/hermes_operator_bridge_packet.md`.
- Confirm the dashboard still says Codex provider pending/not proven.

## Manual Later

- Decide whether Hermes provider setup is needed.
- Verify provider support with safe local Hermes documentation or commands.
- Configure provider credentials outside git only after explicit human approval.
- Configure Telegram outside git only after explicit human approval.
- Rerun public audit and Hermes bridge status after any manual setup.

## Still Blocked

- No provider setup by Codex.
- No token entry or token reading by Codex.
- No Telegram setup by Codex.
- No browser automation until a remediation milestone proves it safely.
- No live APIs or account actions.
