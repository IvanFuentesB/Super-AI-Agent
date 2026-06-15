"""Detect locally available dev tools. Read-only: runs only `<tool> --version`
style probes via fixed argv, never installs or starts services."""

from __future__ import annotations

import shutil
import subprocess

# name -> (probe args, check_only). check_only tools are never installed by
# this stack even with --apply (docker/ollama): we only report presence.
LOCAL_BASICS = {
    "git": (["git", "--version"], False),
    "gh": (["gh", "--version"], False),
    "node": (["node", "--version"], False),
    "npm": (["npm", "--version"], False),
    "python": (["python", "--version"], False),
    "cargo": (["cargo", "--version"], False),
    "rustc": (["rustc", "--version"], False),
    "docker": (["docker", "--version"], True),
    "ollama": (["ollama", "--version"], True),
}


def _probe(args: list[str]) -> str | None:
    exe = shutil.which(args[0])
    if not exe:
        return None
    try:
        proc = subprocess.run([exe] + args[1:], capture_output=True, text=True,
                              timeout=15, shell=False)
        out = (proc.stdout or proc.stderr or "").strip().splitlines()
        return out[0] if out else "present"
    except Exception:
        return "present"


def check_local_basics() -> dict:
    tools = {}
    for name, (args, check_only) in LOCAL_BASICS.items():
        version = _probe(args)
        tools[name] = {
            "present": version is not None,
            "version": version,
            "check_only": check_only,
            "on_path": shutil.which(args[0]) is not None,
        }
    present = [n for n, t in tools.items() if t["present"]]
    missing = [n for n, t in tools.items() if not t["present"]]
    return {
        "ok": True,
        "tools": tools,
        "present": sorted(present),
        "missing": sorted(missing),
        "present_count": len(present),
        "missing_count": len(missing),
        "safety": {"network_used": False, "installs_performed": False,
                   "services_started": False},
    }


if __name__ == "__main__":
    import json
    print(json.dumps(check_local_basics(), indent=2))
