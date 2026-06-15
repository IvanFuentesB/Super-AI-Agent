"""Write the skills registry (which agent skills to set up, and how).

Repo-local only: this records intended skills and manual setup steps. It does
NOT install into user/global skill folders. manual_required=true means a human
runs the documented install; the registry is the source of truth for status.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = REPO_ROOT / "14_context" / "tool_stack" / "skills_registry.json"

SKILLS = {
    "claude_code": [
        "karpathy-guidelines", "context-engineering", "search-first/source-driven-development",
        "incremental-implementation", "verification-loop", "parallel-execution-optimizer",
        "frontend-design", "code-review-security", "mcp-builder", "skill-creator",
        "prompt-optimizer", "hooks-mastery", "ccstatusline", "claudekit",
        "claude-code-action", "claude-task-master", "claude-loop", "claude-squad",
        "claude-mem", "superclaude", "bmad", "archon", "official-anthropic-skills-repo",
    ],
    "codex": [
        "karpathy-guidelines", "context-engineering", "verification-loop",
        "parallel-execution-optimizer", "security-review", "rust-guard-audit",
        "merge-gate", "repo-intake-audit", "token-saving-audit",
    ],
    "hermes": [
        "local-coordinator", "status-summarizer", "memory-compressor",
        "handoff-summarizer", "top-5-next-actions-reporter", "no-execution",
        "reads-ghoti-obsidian-files",
    ],
    "chatgpt_cowork": [
        "morning-dashboard-artifact", "ghoti-command-dashboard-artifact",
        "gmail-calendar-figma-connectors", "github-notion-connector-view",
        "prompt-memory-manager",
    ],
}

# Skills already proven in this repo's workflow (no external install needed).
KNOWN_LOCAL = {"karpathy-guidelines", "context-engineering", "verification-loop",
               "incremental-implementation", "search-first/source-driven-development",
               "code-review-security", "mcp-builder", "skill-creator",
               "security-review", "rust-guard-audit", "merge-gate", "repo-intake-audit"}


def build_registry() -> dict:
    agents = {}
    total = 0
    for agent, names in SKILLS.items():
        items = []
        for name in names:
            known = name in KNOWN_LOCAL
            items.append({
                "id": name,
                "agent": agent,
                "manual_required": not known,
                "status": "available_in_repo_workflow" if known else "manual_install_documented",
                "next_action": ("Use directly in agent prompts/discipline." if known
                                else "Confirm canonical source, then install per GHOTI_AGENT_SKILLS_SETUP.md."),
                "enabled": False,
            })
            total += 1
        agents[agent] = items
    return {"ok": True, "schema": "ghoti_skills_registry/1", "agent_count": len(agents),
            "skill_count": total, "agents": agents,
            "safety": {"writes_user_global_skills": False, "secrets": False}}


def write_registry() -> dict:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    data = build_registry()
    REGISTRY.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "action": "write-skills-templates",
            "registry_path": REGISTRY.relative_to(REPO_ROOT).as_posix(),
            "skill_count": data["skill_count"], "agent_count": data["agent_count"]}


if __name__ == "__main__":
    print(json.dumps(write_registry(), indent=2))
