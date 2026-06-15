# Ghoti Acceleration Tool Stack

Local, safe tooling to make future Ghoti work faster. One CLI composes
detection, safe-install planning, MCP templates, skills registry, and repo
intake. Nothing here installs unknown repos, enables live accounts, or stores
secrets.

## CLI

```
python 03_scripts/tool_stack/ghoti_tool_stack.py --status --json
python 03_scripts/tool_stack/ghoti_tool_stack.py --check --json
python 03_scripts/tool_stack/ghoti_tool_stack.py --install-safe --dry-run --json
python 03_scripts/tool_stack/ghoti_tool_stack.py --install-safe --apply --json
python 03_scripts/tool_stack/ghoti_tool_stack.py --write-mcp-templates --json
python 03_scripts/tool_stack/ghoti_tool_stack.py --write-skills-templates --json
python 03_scripts/tool_stack/ghoti_tool_stack.py --repo-intake <repo> --dry-run --json
```

## Safety posture

- Dry-run is the default; `--install-safe` reports manual hints and never
  auto-installs or starts services.
- MCP templates are written `enabled:false` with env-var names only (no values).
- Repo intake dry-run never clones; `--apply` shallow-clones into a gitignored
  sandbox and only collects metadata - it never runs repo code.
- No secrets, no live account actions, no browser/computer-use.

## Files

- `ghoti_tool_stack.py` - main CLI.
- `check_tool_stack.py` - detect local dev basics (read-only).
- `install_safe_tools.py` - safe install planner (manual-report).
- `mcp_config_writer.py` - writes disabled MCP templates.
- `skills_config_writer.py` - writes the skills registry.
- `repo_intake.py` - safe clone+static-inspect (sandboxed).
