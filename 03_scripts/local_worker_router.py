#!/usr/bin/env python3
"""Local Worker Router — routing scaffold for Python/Gemma/Claude/Codex/ChatGPT task dispatch.

N+3.56-FIX: bridge handoff tasks now route to cc_codex_bridge_worker (not generic codex_audit).
stdlib only, repo-local, no external APIs, no live actions, no account actions.
Ollama status check is read-only and disabled by default.
"""
import argparse
import datetime
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
LOCAL_WORKERS_DIR = REPO_ROOT / "14_context" / "local_workers"
ROUTING_CONFIG = REPO_ROOT / "23_configs" / "local_worker_routing.example.json"

ROUTE_RULES = [
    {
        "keywords": ["bridge handoff", "cc codex bridge", "codex bridge", "create bridge",
                     "handoff for claude code and codex", "bridge for claude", "write handoff"],
        "route": "cc_codex_bridge_worker",
        "reason": "Bridge handoff task — route to cc_codex_bridge.py, not generic Codex. Local file bridge only.",
    },
    {
        "keywords": ["json", "jsonl", "validate", "parse", "csv", "report", "file generation",
                     "file parsing", "validation", "generate", "list files", "count"],
        "route": "python_automation_worker",
        "reason": "Deterministic file/data task — Python stdlib handles this cheaply without model tokens.",
    },
    {
        "keywords": ["compress", "summary", "summarize", "summarise", "compression", "scoring",
                     "draft", "score", "distill", "extract key points", "shorten"],
        "route": "gemma_local_worker",
        "reason": "Cheap text reduction task — route to Gemma/Ollama if available, else Claude prompt.",
        "fallback": "claude_code_impl",
    },
    {
        "keywords": ["implement", "build", "create script", "write code", "fix bug", "test",
                     "commit", "edit file", "refactor", "edit dashboard", "javascript", "python script"],
        "route": "claude_code_impl",
        "reason": "Implementation/reasoning task — requires Claude Code.",
    },
    {
        "keywords": ["audit", "source check", "source-check", "verify", "spec", "review safety",
                     "check policy", "confirm", "gate", "security", "codex audit"],
        "route": "codex_audit",
        "reason": "Audit/verification task — route to Codex.",
    },
    {
        "keywords": ["organize local prompt", "small python automation", "local prompt files",
                     "automate local", "python automation", "automation script", "organize files"],
        "route": "python_automation_worker",
        "reason": "Python automation task -- stdlib file manipulation, no external APIs.",
    },
    {
        "keywords": ["course certificate", "certificate tracker", "study plan", "study tracker",
                     "coursera", "udemy", "linkedin learning", "badge", "learning path", "course cert"],
        "route": "course_certificate_assistant",
        "reason": "Course/cert planning task -- template generation and study tracking only, human does assessments.",
    },
    {
        "keywords": ["ruflo", "orchestrate claude agents", "claude-flow", "ruv-swarm",
                     "agent swarm", "multi-agent orchestrat", "swarm orchestrat"],
        "route": "ruflo_orchestrator_candidate",
        "reason": "Ruflo/swarm orchestration candidate -- isolated from Ghoti runtime until safety gate passes.",
    },
    {
        "keywords": ["compress memory with local", "gemma compress", "gemma memory",
                     "local gemma", "ollama compress"],
        "route": "gemma_local_worker",
        "reason": "Local Gemma compression task — route to gemma_compact_memory_worker.py.",
    },
    {
        "keywords": ["obsidian vault", "vault note", "daily note", "note link", "obsidian memory",
                     "obsidian plugin", "markdown vault"],
        "route": "obsidian_memory_worker",
        "reason": "Obsidian vault task -- read-only inspection or local note creation.",
    },
    {
        "keywords": ["prompt bus", "prompt handoff", "copy-paste prompt", "write prompt to outbox",
                     "handoff to chatgpt", "prompt file outbox"],
        "route": "prompt_bus_worker",
        "reason": "Prompt bus task -- write or list prompt files via prompt_bus.py.",
    },
    {
        "keywords": ["strategy", "architecture", "plan", "design", "milestone", "roadmap",
                     "next steps", "prompt design", "chatgpt"],
        "route": "chatgpt_strategy",
        "reason": "Strategy/planning task — route to ChatGPT.",
    },
    {
        "keywords": ["live", "account", "email", "post", "pay", "sell", "scrape", "apply",
                     "login", "public", "money action", "send", "submit", "giveaway"],
        "route": "human_approval_required",
        "reason": "Live/account/public/money action — STOP. Human approval required. No automation.",
    },
]

ROUTE_DESCRIPTIONS = {
    "cc_codex_bridge_worker": "CC/Codex bridge lane. Routes to cc_codex_bridge.py — local file handoff only. CC/Codex automatic = NO.",
    "python_automation_worker": "Safe local Python script. stdlib only, no external APIs.",
    "gemma_local_worker": "Local Ollama/Gemma inference. Draft only — human review before canonical use.",
    "claude_code_impl": "Claude Code implementation. Use for reasoning, code, commits.",
    "codex_audit": "Codex audit lane. Use for source-check, spec, safety gate verification.",
    "chatgpt_strategy": "ChatGPT strategy lane. Use for planning, architecture, next-milestone design.",
    "course_certificate_assistant": "Course/cert tracker. Templates + study plans. Human does all assessments.",
    "ruflo_orchestrator_candidate": "Ruflo/claude-flow orchestration. Isolated from Ghoti until safety gate passes.",
    "obsidian_memory_worker": "Obsidian vault tasks. Read-only inspect or local note creation.",
    "prompt_bus_worker": "Prompt bus tasks. Write/list prompt files via prompt_bus.py.",
    "human_approval_required": "STOP. This task requires explicit human approval before any automation.",
}


def _recommend(task: str) -> dict:
    task_lower = task.lower()
    for rule in ROUTE_RULES:
        for kw in rule["keywords"]:
            if kw in task_lower:
                return rule
    return {
        "route": "claude_code_impl",
        "reason": "No clear rule match — defaulting to Claude Code for human judgment.",
    }


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def cmd_recommend(args):
    if not args.task:
        print("ERROR: --task required")
        sys.exit(1)
    rule = _recommend(args.task)
    route = rule["route"]
    reason = rule["reason"]
    fallback = rule.get("fallback")
    desc = ROUTE_DESCRIPTIONS.get(route, "")

    print(f"Task: {args.task}")
    print(f"Route: {route}")
    print(f"Description: {desc}")
    print(f"Reason: {reason}")
    if fallback:
        print(f"Fallback (if primary unavailable): {fallback}")
    if route == "human_approval_required":
        print("\nACTION REQUIRED: Do not automate. Get explicit human approval first.")


def _check_ollama_available():
    try:
        import subprocess
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=3
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def cmd_study_template(args):
    template = {
        "type": "study_tracker",
        "generated": _utc_now(),
        "course": "{{COURSE_NAME}}",
        "platform": "{{PLATFORM}}",
        "target_completion": "{{DATE}}",
        "modules": [
            {"id": 1, "title": "{{MODULE_1}}", "status": "not_started", "notes": ""},
            {"id": 2, "title": "{{MODULE_2}}", "status": "not_started", "notes": ""},
        ],
        "total_hours_estimated": 0,
        "hours_completed": 0,
        "certificate_checklist": [
            "complete all modules",
            "pass final assessment (human work only)",
            "download certificate",
            "add to portfolio (human review required before sharing)",
        ],
        "safety_note": "No impersonation. No bypassing proctoring. All assessments completed by human only.",
    }
    print(json.dumps(template, indent=2))
    if args.apply:
        out = REPO_ROOT / "05_logs" / "study_artifacts" / f"study_template_{_utc_now().replace(' ','_').replace(':','')}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(template, indent=2), encoding="utf-8")
        print(f"\nWritten: {out.relative_to(REPO_ROOT)}")
    else:
        print("\n[DRY RUN] Pass --apply to write to 05_logs/study_artifacts/.")


def cmd_course_cert_template(args):
    template = {
        "type": "course_certificate_backlog",
        "generated": _utc_now(),
        "courses": [
            {
                "id": "CERT-001",
                "title": "{{COURSE_TITLE}}",
                "provider": "{{PROVIDER}}",
                "url": "{{URL}}",
                "status": "backlog",
                "priority": "medium",
                "estimated_hours": 0,
                "start_date": None,
                "completion_date": None,
                "certificate_url": None,
                "notes": "",
            }
        ],
        "safety_note": (
            "All coursework completed by human. "
            "Claude may assist with: notes, study plans, quiz practice, progress tracking. "
            "Claude may NOT: submit assessments, impersonate user, bypass proctoring, fabricate certificates."
        ),
    }
    print(json.dumps(template, indent=2))
    if args.apply:
        out = REPO_ROOT / "05_logs" / "study_artifacts" / f"cert_backlog_{_utc_now().replace(' ','_').replace(':','')}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(template, indent=2), encoding="utf-8")
        print(f"\nWritten: {out.relative_to(REPO_ROOT)}")
    else:
        print("\n[DRY RUN] Pass --apply to write to 05_logs/study_artifacts/.")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Local Worker Router — recommend where to route a task. "
            "stdlib only, no live actions, no API calls. N+3.56-FIX."
        )
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--recommend", action="store_true", help="Recommend route for a task")
    group.add_argument("--study-template", action="store_true", help="Generate a study tracker template")
    group.add_argument("--course-cert-template", action="store_true", help="Generate a course/cert backlog template")

    parser.add_argument("--task", help="Task description for --recommend")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run (default)")
    parser.add_argument("--apply", action="store_true", help="Write output to file")

    args = parser.parse_args()

    if args.recommend:
        cmd_recommend(args)
    elif args.study_template:
        cmd_study_template(args)
    elif args.course_cert_template:
        cmd_course_cert_template(args)


if __name__ == "__main__":
    main()
