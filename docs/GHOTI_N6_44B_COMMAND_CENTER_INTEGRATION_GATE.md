# Ghoti N+6.44B Command Center Integration Gate

N+6.44B verifies that Ghoti's local command center, deterministic memory search,
Obsidian pointer views, simulated task waves, file ownership checks, agent
roster, Agent Arena shape, and Paperclip-compatible planning previews form one
coherent supervised system.

It does not add live agent launch or computer-use capability.

## What The Command Center Does Today

- Reads the reviewed local memory search index and verifies all source hashes.
- Links to the generated Obsidian-compatible start view and verifies its links.
- Produces deterministic supervised workflow plans and task waves.
- Assigns stable simulated agent roles without starting agent processes.
- Rejects overlapping file ownership before a simulated workflow can proceed.
- Produces Agent Arena-shaped and Paperclip-compatible planning previews.

Memory search and Obsidian pages remain navigation aids. The linked source files
and hashes remain the truth.

## What Remains Simulation-Only

- Agent launch and process control
- Browser and full computer-use
- Mouse clicks, keyboard input, and auto-submit
- Account, email, posting, purchase, payment, and other money actions
- Paperclip company launch or external repo execution

## Run The Gate

```text
python 03_scripts/agent_command_center/check_command_center_integration.py --check --json
python 03_scripts/agent_command_center/check_command_center_integration.py --write --json
```

The loopback health probe reports either `healthy` or `server_not_running`.
A stopped visual server is an explicit operational state, not an unexplained
integration failure.

To start the existing read-only command center:

```text
powershell -ExecutionPolicy Bypass -File 03_scripts/agent_command_center/start_agent_command_center.ps1 -DryRun
python 03_scripts/agent_command_center/ghoti_agent_command_center.py --serve --host 127.0.0.1 --port 8770 --json
```

Read the generated evidence:

- `14_context/operator_reports/generated/n6_44b_command_center_integration_gate.json`
- `14_context/operator_reports/generated/n6_44b_command_center_integration_gate.md`

## Ready For N+6.45A

`ready_for_n6_45a=true` means the deterministic planning, memory, ownership,
simulation, and approval boundaries passed. It does not authorize execution.

N+6.45A should design and trial exactly one allowlisted local agent process
behind explicit human approval, a kill switch, bounded inputs, bounded outputs,
and a complete local trace. It must keep browser control, accounts, posting,
money actions, and auto-submit disabled.
