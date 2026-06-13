"""Ghoti Agent OS - standalone self-check runner.

Thin wrapper so operators and CI-style gates can run the agent OS
self-test directly. Exit code 0 means every check passed.

Usage: python 03_scripts/agent_os/check_agent_os.py [--json]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ghoti_agent_os  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    payload = ghoti_agent_os.cmd_check()
    if "--json" in args:
        print(json.dumps(payload, indent=2))
    else:
        for check in payload["checks"]:
            print("[%s] %s - %s" % ("ok" if check["ok"] else "FAIL",
                                    check["name"], check["details"]))
        print("passed: %d/%d" % (payload["passed"], payload["total"]))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
