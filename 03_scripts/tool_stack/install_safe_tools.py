"""Safe installer planner for package-managed dev basics.

Conservative by design: it NEVER installs unknown repos and NEVER starts
services. Even with --apply it only reports manual steps unless a known-safe
package manager + command is available; this build defaults to manual-report so
nothing mutates the system unexpectedly. check_only tools (docker, ollama) are
never installed here - presence is only reported.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_tool_stack  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLED = REPO_ROOT / "14_context" / "tool_stack" / "installed_tools.json"

# Documented manual install hints per OS family. We report these; we do not run
# them automatically (winget/choco/apt invocations are left to the human).
INSTALL_HINTS = {
    "git": "winget install Git.Git  |  https://git-scm.com",
    "gh": "winget install GitHub.cli  |  https://cli.github.com",
    "node": "winget install OpenJS.NodeJS.LTS  |  https://nodejs.org",
    "npm": "ships with Node.js (install node)",
    "python": "winget install Python.Python.3.11  |  https://python.org",
    "cargo": "rustup (https://rustup.rs) installs cargo + rustc",
    "rustc": "rustup (https://rustup.rs) installs cargo + rustc",
    "docker": "check-only: install Docker Desktop manually if needed; do not auto-start",
    "ollama": "check-only: https://ollama.com if local models are wanted",
}


def plan(apply: bool = False) -> dict:
    detected = check_tool_stack.check_local_basics()
    actions = []
    for name, info in sorted(detected["tools"].items()):
        if info["present"]:
            actions.append({"tool": name, "action": "already_present",
                            "version": info["version"], "applied": False})
        elif info["check_only"]:
            actions.append({"tool": name, "action": "manual_check_only",
                            "hint": INSTALL_HINTS[name], "applied": False})
        else:
            # Missing, installable basic: we REPORT the manual command. We do not
            # execute it - safer and portable across machines.
            actions.append({"tool": name, "action": "manual_install_recommended",
                            "hint": INSTALL_HINTS[name], "applied": False})
    payload = {
        "ok": True,
        "action": "install-safe",
        "mode": "apply" if apply else "dry-run",
        "system_modified": False,
        "note": ("Apply mode still reports manual steps for missing tools: this "
                 "stack never auto-installs to avoid surprising system changes. "
                 "Run the printed hints yourself."),
        "actions": actions,
        "present": detected["present"],
        "missing": detected["missing"],
        "safety": {"installs_performed": False, "services_started": False,
                   "unknown_repos_executed": False, "network_used": False},
    }
    return payload


def write_installed_snapshot() -> str:
    detected = check_tool_stack.check_local_basics()
    INSTALLED.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {"schema": "ghoti_installed_tools/1",
                "tools": detected["tools"], "present": detected["present"],
                "missing": detected["missing"],
                "safety": {"installs_performed": False}}
    INSTALLED.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    return INSTALLED.relative_to(REPO_ROOT).as_posix()


if __name__ == "__main__":
    print(json.dumps(plan("--apply" in sys.argv), indent=2))
