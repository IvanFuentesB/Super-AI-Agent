#!/usr/bin/env python3
"""Read-only ECC agent setup inspector for Ghoti N+6.19A.

The inspector reads a local ECC clone and detects agentic coding setup patterns:
agents, skills, rules, commands, hooks, MCP/client configuration, and security
scanner ideas. It never imports or executes ECC code.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

MILESTONE = "N+6.19A"

KEYWORDS = {
    "agents": ["agent", "agents"],
    "skills": ["skill", "skills"],
    "rules": ["rule", "rules", "instructions"],
    "commands": ["command", "commands"],
    "hooks": ["hook", "hooks"],
    "mcp": ["mcp", "model-context"],
    "security_scanner": ["security", "scanner", "audit", "lint", "secret"],
    "prompt_rules": ["prompt", "prompts", "constitution", "policy"],
}

SAFETY = {
    "local_only": True,
    "execution_performed": False,
    "imports_external_code": False,
    "reads_secret_values": False,
    "live_api_used": False,
}


def _license(repo: Path) -> str | None:
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt"):
        path = repo / name
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace").lower()
            if "mit license" in text or "permission is hereby granted" in text:
                return "MIT"
            if "apache license" in text:
                return "Apache-2.0"
            return "present_unclassified"
    return None


def inspect_repo(repo: Path) -> dict:
    repo = repo.resolve()
    present = repo.is_dir()
    components = {key: [] for key in KEYWORDS}
    top_level = []

    if present:
        top_level = sorted(p.name for p in repo.iterdir() if p.name != ".git")[:100]
        for path in repo.rglob("*"):
            if ".git" in path.parts:
                continue
            rel = path.relative_to(repo).as_posix().lower()
            for key, needles in KEYWORDS.items():
                if any(needle in rel for needle in needles):
                    bucket = components[key]
                    if len(bucket) < 25:
                        bucket.append(path.relative_to(repo).as_posix())

    detected = {k: v for k, v in components.items() if v}
    reusable = []
    adaptations = []
    if detected.get("agents"):
        reusable.append("agent profile directory layout")
        adaptations.append("Create Ghoti agent profiles for Claude implementation, Codex audit, Hermes coordination, and Gemma summaries.")
    if detected.get("skills"):
        reusable.append("skill registry and install workflow")
        adaptations.append("Map external skills into Ghoti's 14_context/skills registry before any runtime install.")
    if detected.get("commands"):
        reusable.append("command templates and operator command surface")
        adaptations.append("Use command templates for dry-run wrappers only; keep live run/paste blocked until N+6.20A+.")
    if detected.get("hooks"):
        reusable.append("hook lifecycle pattern")
        adaptations.append("Adapt hook ideas as status/report validators, not automatic code execution hooks.")
    if detected.get("security_scanner"):
        reusable.append("security scanner/checklist pattern")
        adaptations.append("Fold scanner ideas into public_repo_security_audit and Codex merge gates.")
    if detected.get("mcp"):
        reusable.append("MCP/client configuration pattern")
        adaptations.append("Keep MCP config as docs/spec only until a separate manual setup milestone.")

    return {
        "ok": present,
        "milestone": MILESTONE,
        "repo_present": present,
        "repo": str(repo),
        "license": _license(repo) if present else None,
        "top_level": top_level,
        "detected_components": detected,
        "reusable_patterns": reusable,
        "recommended_ghoti_adaptations": adaptations,
        "blocked_runtime_actions": [
            "installing ECC globally",
            "executing ECC commands",
            "running hooks automatically",
            "configuring MCP",
            "launching live agents",
            "reading tokens or credentials",
        ],
        "safety": dict(SAFETY),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Inspect a local ECC clone without executing it.")
    parser.add_argument("--repo", required=True, help="Path to local ECC clone.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args(argv)
    result = inspect_repo(Path(args.repo))
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
