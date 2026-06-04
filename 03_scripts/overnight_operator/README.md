# Overnight Operator Scripts

Scripts in this folder are local-first N+6.19A tools.

- `ghoti_prompt_packet_builder.py` renders local task JSON into Markdown prompt packets.
- `ghoti_clipboard_relay.ps1` can dry-run packet relay and can copy locally only when explicitly asked.
- `ghoti_operator_queue.py` dispatches safe local tasks and blocks dangerous task types.
- `ghoti_repo_execution_sandbox.py` clones/static-scans allowlisted external repos inside the ignored runtime sandbox.
- `ecc_agent_setup_inspector.py` reads a local ECC clone and reports reusable agent setup patterns.
- `check_overnight_operator.ps1` validates required files and disabled flags.

No script in this milestone pastes into apps, submits forms, launches agents, starts MCP, configures Telegram, opens browsers, or runs third-party installers.
