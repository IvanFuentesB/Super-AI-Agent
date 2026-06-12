"""Ghoti Agent OS - workflow templates and agent roster.

Pure data plus pure functions: no subprocess, no network, no writes.
Templates describe supervised local workflows; every capability they
request must exist in the deny-by-default operator recipe policy
(23_configs/operator_recipe_policy.example.json). Rendering produces
ASCII-only Markdown that follows the prompt-bus packet header
convention so existing tooling keeps parsing it.
"""

from __future__ import annotations

import hashlib
import json

# Display roster for the command center. Structured source of truth for
# lanes stays 14_context/agent_lanes/agent_lane_registry.json; lane_ref
# points into it. Every role is suggestion-only in this milestone.
ROSTER: dict[str, dict] = {
    "planner": {
        "title": "Planner",
        "mission": "Turn goals into small, verifiable task waves with clear file ownership.",
        "lane_ref": "chatgpt_strategy",
        "mode": "suggestion_only",
    },
    "coder": {
        "title": "Coder",
        "mission": "Implement one approved task at a time on a feature branch.",
        "lane_ref": "claude_code_impl",
        "mode": "suggestion_only",
    },
    "auditor": {
        "title": "Auditor",
        "mission": "Adversarially verify finished work before it is merged.",
        "lane_ref": "codex_audit",
        "mode": "suggestion_only",
    },
    "researcher": {
        "title": "Researcher",
        "mission": "Collect local context and draft research plans for human-run searches.",
        "lane_ref": "gemma_local_worker",
        "mode": "suggestion_only",
    },
    "content": {
        "title": "Content",
        "mission": "Draft scripts, titles, and checklists; humans publish manually.",
        "lane_ref": "gemma_local_worker",
        "mode": "suggestion_only",
    },
    "operator": {
        "title": "Operator",
        "mission": "Run safe local recipes/checks and keep the evidence trail honest.",
        "lane_ref": "python_automation_worker",
        "mode": "suggestion_only",
    },
}

# Workflow templates. owned_paths are repo-relative prefixes a role would
# touch if the plan were executed; the ownership check uses them to prove
# no two roles overlap inside one wave. Capabilities must stay inside the
# allowed list of the recipe policy.
TEMPLATES: dict[str, dict] = {
    "coding-task": {
        "title": "Coding Task",
        "goal": "Ship one small, tested code change on a feature branch.",
        "description": "Plan, implement, and audit a single repo-local coding task "
                       "with tests and a validation gate.",
        "wont_do": "No pushes, merges, or edits outside the planned file ownership.",
        "roles": ["planner", "coder", "auditor"],
        "capabilities": ["repo_read", "status_read", "plan_render", "report_write_repo_local"],
        "handoff_targets": ["claude", "codex"],
        "steps": [
            {"step": 1, "role": "planner", "action": "Write task brief: goal, files, success criteria.",
             "output": "task brief section in the plan", "owned_paths": ["14_context/agent_os/runs/planner/"]},
            {"step": 2, "role": "coder", "action": "Implement the change plus a focused test.",
             "output": "diff summary placeholder for the human-run lane", "owned_paths": ["01_projects/", "03_scripts/"]},
            {"step": 3, "role": "auditor", "action": "Review the diff against the brief; list findings.",
             "output": "audit checklist", "owned_paths": ["14_context/agent_os/runs/auditor/"]},
        ],
        "deliverables": ["task brief", "implementation handoff packet", "audit checklist"],
    },
    "repo-audit": {
        "title": "Repo Audit",
        "goal": "Produce an honest repo health and risk report.",
        "description": "Aggregate git truth, test gate state, security audit output, "
                       "and lane locks into one report.",
        "wont_do": "No fixes applied; findings only.",
        "roles": ["auditor", "operator"],
        "capabilities": ["repo_read", "status_read", "report_write_repo_local"],
        "handoff_targets": ["codex"],
        "steps": [
            {"step": 1, "role": "operator", "action": "Collect status: git, tests, audit, locks.",
             "output": "status snapshot", "owned_paths": ["14_context/agent_os/runs/operator/"]},
            {"step": 2, "role": "auditor", "action": "Rank risks and unverified claims.",
             "output": "ranked findings list", "owned_paths": ["14_context/agent_os/runs/auditor/"]},
        ],
        "deliverables": ["repo audit report draft"],
    },
    "content-video": {
        "title": "Content / Video Idea Pipeline",
        "goal": "Draft a video idea package ready for human review.",
        "description": "Idea list, one chosen script draft, title/thumbnail variants, "
                       "and a manual publish checklist.",
        "wont_do": "No posting, no uploads, no account access; drafts only.",
        "roles": ["researcher", "content", "planner"],
        "capabilities": ["repo_read", "plan_render", "report_write_repo_local"],
        "handoff_targets": ["claude", "hermes"],
        "steps": [
            {"step": 1, "role": "researcher", "action": "Pull context from memory; list 5 idea candidates.",
             "output": "idea candidate list", "owned_paths": ["14_context/agent_os/runs/researcher/"]},
            {"step": 2, "role": "content", "action": "Draft script outline plus 5 title variants for the top idea.",
             "output": "script and title drafts", "owned_paths": ["14_context/agent_os/runs/content/"]},
            {"step": 3, "role": "planner", "action": "Assemble manual publish checklist (human does every live step).",
             "output": "manual publish checklist", "owned_paths": ["14_context/agent_os/runs/planner/"]},
        ],
        "deliverables": ["idea list", "script draft", "title variants", "manual publish checklist"],
    },
    "business-research": {
        "title": "Business Research Plan",
        "goal": "Draft a research plan for one online-business hypothesis.",
        "description": "Question list, evaluation criteria, and a human-run research "
                       "checklist for a dropshipping/business idea.",
        "wont_do": "No purchases, no signups, no live market scraping.",
        "roles": ["researcher", "planner"],
        "capabilities": ["repo_read", "plan_render", "report_write_repo_local"],
        "handoff_targets": ["claude"],
        "steps": [
            {"step": 1, "role": "planner", "action": "Define the hypothesis and success criteria.",
             "output": "hypothesis brief", "owned_paths": ["14_context/agent_os/runs/planner/"]},
            {"step": 2, "role": "researcher", "action": "Draft research questions and source checklist for the human.",
             "output": "research checklist", "owned_paths": ["14_context/agent_os/runs/researcher/"]},
        ],
        "deliverables": ["hypothesis brief", "research checklist"],
    },
    "email-draft": {
        "title": "Email Draft Workflow",
        "goal": "Produce a reviewed email draft the human sends manually.",
        "description": "Context summary, draft body, tone check, and a send checklist. "
                       "Nothing is sent by Ghoti.",
        "wont_do": "No account access, no sending, no contact scraping.",
        "roles": ["content", "auditor"],
        "capabilities": ["repo_read", "plan_render", "report_write_repo_local"],
        "handoff_targets": ["claude"],
        "steps": [
            {"step": 1, "role": "content", "action": "Draft the email body from the stated intent.",
             "output": "email draft", "owned_paths": ["14_context/agent_os/runs/content/"]},
            {"step": 2, "role": "auditor", "action": "Check tone, claims, and recipients; flag risks.",
             "output": "review notes plus send checklist", "owned_paths": ["14_context/agent_os/runs/auditor/"]},
        ],
        "deliverables": ["email draft", "send checklist"],
    },
    "automation-n8n": {
        "title": "Automation / n8n Planning",
        "goal": "Design one automation flow on paper before any wiring.",
        "description": "Trigger/step/failure-mode table for a future n8n or script "
                       "automation, with an approval gate list.",
        "wont_do": "No live workflow creation, no credentials, no external calls.",
        "roles": ["planner", "operator"],
        "capabilities": ["repo_read", "plan_render", "report_write_repo_local"],
        "handoff_targets": ["claude", "hermes"],
        "steps": [
            {"step": 1, "role": "planner", "action": "Describe trigger, steps, data in/out, failure modes.",
             "output": "flow design table", "owned_paths": ["14_context/agent_os/runs/planner/"]},
            {"step": 2, "role": "operator", "action": "List required approval gates and manual setup steps.",
             "output": "approval gate list", "owned_paths": ["14_context/agent_os/runs/operator/"]},
        ],
        "deliverables": ["automation flow design", "approval gate list"],
    },
    "computer-use-prep": {
        "title": "Computer-Use Preparation Checklist",
        "goal": "Verify every precondition for future supervised computer-use.",
        "description": "Checklist over the existing observation-only adapter, policy "
                       "checker, kill-switch vocabulary, and approval flow.",
        "wont_do": "No mouse/keyboard control, no browser automation, observation only.",
        "roles": ["operator", "auditor"],
        "capabilities": ["repo_read", "status_read", "local_policy_check", "report_write_repo_local"],
        "handoff_targets": ["claude", "codex"],
        "steps": [
            {"step": 1, "role": "operator", "action": "Check adapter dry-run, policy checker, and feature flags.",
             "output": "precondition checklist", "owned_paths": ["14_context/agent_os/runs/operator/"]},
            {"step": 2, "role": "auditor", "action": "Confirm every live-action path is still blocked.",
             "output": "blocked-path confirmation", "owned_paths": ["14_context/agent_os/runs/auditor/"]},
        ],
        "deliverables": ["computer-use precondition checklist"],
    },
}

WORKFLOW_ORDER = [
    "coding-task", "repo-audit", "content-video", "business-research",
    "email-draft", "automation-n8n", "computer-use-prep",
]


def list_templates() -> dict:
    return {
        "ok": True,
        "count": len(TEMPLATES),
        "workflows": [
            {"id": wid, "title": t["title"], "goal": t["goal"],
             "description": t["description"], "wont_do": t["wont_do"],
             "roles": t["roles"], "capabilities": t["capabilities"],
             "handoff_targets": t["handoff_targets"],
             "deliverables": t["deliverables"]}
            for wid, t in ((w, TEMPLATES[w]) for w in WORKFLOW_ORDER)
        ],
        "roster": [
            {"id": rid, **ROSTER[rid]} for rid in
            ("planner", "coder", "auditor", "researcher", "content", "operator")
        ],
        "template_fingerprint": template_fingerprint(),
        "mode": "suggestion_only",
    }


def get_template(workflow_id: str) -> dict | None:
    return TEMPLATES.get(workflow_id)


def template_fingerprint() -> str:
    """Stable sha256 over the canonical JSON of all templates and roles."""
    canonical = json.dumps({"templates": TEMPLATES, "roster": ROSTER},
                           sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_task_wave(workflow_id: str) -> dict:
    """Deterministic task-wave preview: steps grouped into waves so that no
    two tasks in the same wave share a role or an owned path prefix."""
    template = TEMPLATES.get(workflow_id)
    if template is None:
        return {"ok": False, "workflow": workflow_id, "error": "unknown workflow id"}
    waves: list[list[dict]] = []
    for step in template["steps"]:
        placed = False
        for wave in waves:
            roles_in_wave = {t["role"] for t in wave}
            paths_in_wave = {p for t in wave for p in t["owned_paths"]}
            overlap = step["role"] in roles_in_wave or any(
                p.startswith(q) or q.startswith(p)
                for p in step["owned_paths"] for q in paths_in_wave)
            if not overlap:
                wave.append(step)
                placed = True
                break
        if not placed:
            waves.append([step])
    return {
        "ok": True,
        "workflow": workflow_id,
        "wave_count": len(waves),
        "task_count": len(template["steps"]),
        "waves": [
            {"wave": i + 1,
             "tasks": [{"step": t["step"], "role": t["role"], "action": t["action"],
                        "owned_paths": t["owned_paths"]} for t in wave]}
            for i, wave in enumerate(waves)
        ],
        "simulation_only": True,
    }


def render_plan_markdown(workflow_id: str, generated_at: str, branch: str,
                         memory_pointers: list[dict] | None = None) -> str:
    """Render an ASCII-only plan packet (prompt-bus header convention)."""
    template = TEMPLATES[workflow_id]
    lines = [
        "# Ghoti Agent OS Plan - %s" % template["title"],
        "",
        "Generated: %s" % generated_at,
        "Branch: %s" % branch,
        "",
        "---",
        "",
        "## Goal",
        "",
        template["goal"],
        "",
        "## What this will not do",
        "",
        template["wont_do"],
        "",
        "## Roles",
        "",
    ]
    for role_id in template["roles"]:
        role = ROSTER[role_id]
        lines.append("- **%s** (%s): %s" % (role["title"], role["mode"], role["mission"]))
    lines += ["", "## Steps", ""]
    for step in template["steps"]:
        lines.append("%d. [%s] %s -> %s" % (
            step["step"], ROSTER[step["role"]]["title"], step["action"], step["output"]))
    lines += ["", "## Deliverables", ""]
    for item in template["deliverables"]:
        lines.append("- %s" % item)
    if memory_pointers:
        lines += ["", "## Memory pointers (verified local sources)", ""]
        for pointer in memory_pointers:
            lines.append("- `%s:%s` %s" % (
                pointer.get("path", "?"), pointer.get("line", "?"),
                pointer.get("snippet", "").strip()))
    lines += [
        "",
        "## Safety",
        "",
        "- relay_mode: copy_paste_only; no agent is launched by Ghoti.",
        "- suggestion_only: a human reviews and runs every live step.",
        "- No posting, purchases, account changes, or browser control.",
        "",
    ]
    return "\n".join(lines)
