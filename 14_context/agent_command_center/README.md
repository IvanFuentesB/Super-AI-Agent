# Ghoti Local Agent Command Center

N+6.44A is a local simulation and planning surface. It connects the reviewed
shared memory/search layer to supervised swarm scenarios, an Agent Arena-shaped
preview, and a Paperclip-compatible company-plan preview.

The center does not guarantee income. Content and ecommerce lanes produce
research, drafts, assumptions, audits, and human decision packets only.

Paperclip is used as a planning-shape reference. It is not installed or run;
Docker and live company/team launch remain blocked. Obsidian-compatible shared
memory remains the durable source-linked handoff layer.

Full computer-use remains blocked. Mouse clicks, keyboard input, accounts,
posting, purchases, payments, ads, supplier contact, and auto-submit require
later audited adapters plus explicit human approval.

Useful commands:

```text
python 03_scripts/agent_command_center/ghoti_agent_command_center.py --check --json
python 03_scripts/agent_command_center/ghoti_agent_command_center.py --status --json
python 03_scripts/agent_command_center/ghoti_agent_command_center.py --scenario content-revenue-research --json
python 03_scripts/agent_command_center/ghoti_agent_command_center.py --arena-preview content-revenue-research --json
python 03_scripts/agent_command_center/ghoti_agent_command_center.py --paperclip-preview content-revenue-research --json
python 03_scripts/agent_command_center/ghoti_agent_command_center.py --memory-query "coordinator planner memory writer" --json
powershell -ExecutionPolicy Bypass -File 03_scripts/agent_command_center/check_agent_command_center.ps1
powershell -ExecutionPolicy Bypass -File 03_scripts/agent_command_center/start_agent_command_center.ps1 -DryRun
```

To run the read-only visual center in the foreground, omit `-DryRun` and open
`http://127.0.0.1:8770/`. Closing that terminal stops the server.
