from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .storage import get_project_root

ALLOWED_MCP_TOOLS = {
    "ghoti_status",
    "read_repo_summary",
    "read_current_state",
    "read_latest_operator_state",
    "read_manual_execution_queue",
    "read_control_center_state",
    "read_pipeline_items_overview",
    "read_approval_inbox",
    "read_approval_item",
    "read_manual_queue_item",
    "read_audit_trace",
}


def _repo_root() -> Path:
    return get_project_root().parents[1]


def _mcp_server_script_path() -> Path:
    return _repo_root() / "01_projects" / "mcp_server" / "server.py"


def call_mcp_tool(tool_name: str, arguments: dict | None = None) -> dict:
    if tool_name not in ALLOWED_MCP_TOOLS:
        raise ValueError(f"Only allowlisted MCP tools are permitted: {sorted(ALLOWED_MCP_TOOLS)}")

    script_path = _mcp_server_script_path()
    if not script_path.exists():
        raise FileNotFoundError(f"MCP server script not found: {script_path}")

    request = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "call_tool",
        "params": {
            "name": tool_name,
            "arguments": arguments if isinstance(arguments, dict) else {},
        },
    }) + "\n"

    result = subprocess.run(
        [sys.executable, str(script_path)],
        input=request,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
        cwd=str(_repo_root()),
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    if result.returncode != 0 and not stdout:
        raise RuntimeError(stderr or f"MCP call exited with code {result.returncode}")

    first_line = stdout.splitlines()[0].strip() if stdout else ""
    if not first_line:
        raise RuntimeError(stderr or "MCP call returned no output.")

    try:
        response = json.loads(first_line)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"MCP call returned invalid JSON: {exc}") from exc

    if "error" in response:
        raise RuntimeError(str(response["error"]))

    payload = response.get("result")
    if not isinstance(payload, dict):
        raise RuntimeError("MCP call returned a non-object result.")
    return payload
