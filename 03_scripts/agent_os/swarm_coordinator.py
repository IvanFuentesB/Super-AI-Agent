"""Ghoti Agent OS - approved-worker swarm coordinator (control plane only).

This is the planner/coordinator layer above the existing approval queue. It
can lay out a multi-worker plan, but it NEVER launches a process and NEVER runs
more than one worker: each step is queued one at a time as a normal approval
request, validated by the Rust ``agent_os_guard`` and executed (later, by a
human-approved step) through the existing bounded executor. There is no parallel
execution, no browser/computer-use/account/money capability, and no new
execution path - the coordinator only reuses ``approval_queue``.

Plan lifecycle per step: planned -> queued -> approved -> executed (or blocked).
Only ``planned`` steps whose dependencies are all ``executed`` are runnable, and
only one step per plan may be in flight (queued/approved-not-executed) at a time.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import approval_queue  # noqa: E402  (reused; do not duplicate the queue)

REPO_ROOT = SCRIPT_DIR.parents[1]
SWARM_PLANS_DIR = REPO_ROOT / "14_context" / "agent_os" / "swarm_plans"
EVIDENCE_DIR = REPO_ROOT / "14_context" / "agent_os" / "evidence"

SCHEMA = "ghoti_swarm_plan/1"

# Only these worker ids may appear in a plan. Roster roles plus the two workers
# the runner branch is expected to add - listing them now keeps plans
# forward-compatible without importing any runner code.
KNOWN_WORKERS = {
    "planner", "coder", "auditor", "researcher", "content", "operator",
    "repo-summary-worker", "local-model-summary-classification-worker",
}

# A swarm step may only request these capabilities. Anything else (browser,
# computer_use, account, money, posting, email, ...) is refused at plan build.
ALLOWED_CAPABILITIES = {
    "repo_read", "status_read", "plan_render",
    "report_write_repo_local", "local_model_status_read",
}
BLOCKED_CAPABILITIES = {
    "account", "browser", "computer_use", "money", "mass_message", "mcp",
    "secrets", "telegram", "posting", "email_send", "purchase", "payment",
    "external_write", "file_delete", "file_move", "agent_launch", "auto_submit",
    "provider_api",
}

# Each swarm workflow maps onto one base Agent OS workflow (so queued steps use
# the existing bounded write action) and a fixed, ordered set of steps. Steps
# own disjoint repo-local folders; dependencies are 1-based step ids.
SWARM_WORKFLOWS: dict[str, dict] = {
    "coding-task-swarm-plan": {
        "title": "Coding Task Swarm Plan",
        "base_workflow": "coding-task",
        "steps": [
            {"worker_id": "planner", "purpose": "Break the coding task into a brief and file plan.",
             "required_inputs": ["14_context/compact_memory/current_working_summary.md"],
             "output_target": "14_context/agent_os/swarm_plans/coding/planner_brief.md",
             "owned_files": ["14_context/agent_os/runs/swarm/planner/"],
             "dependencies": [], "capabilities": ["repo_read", "status_read", "plan_render"],
             "risk_note": "Read + plan render only."},
            {"worker_id": "coder", "purpose": "Draft the implementation outline for the planned change.",
             "required_inputs": ["planner_brief"],
             "output_target": "14_context/agent_os/swarm_plans/coding/coder_outline.md",
             "owned_files": ["14_context/agent_os/runs/swarm/coder/"],
             "dependencies": [1], "capabilities": ["repo_read", "plan_render", "report_write_repo_local"],
             "risk_note": "Draft only; no edits to source until separately approved."},
            {"worker_id": "auditor", "purpose": "Review the outline against the brief; list findings.",
             "required_inputs": ["coder_outline"],
             "output_target": "14_context/agent_os/swarm_plans/coding/auditor_findings.md",
             "owned_files": ["14_context/agent_os/runs/swarm/auditor/"],
             "dependencies": [2], "capabilities": ["repo_read", "report_write_repo_local"],
             "risk_note": "Findings only."},
        ],
    },
    "content-pipeline-swarm-plan": {
        "title": "Content Pipeline Swarm Plan",
        "base_workflow": "content-video",
        "steps": [
            {"worker_id": "researcher", "purpose": "Collect local context and list idea candidates.",
             "required_inputs": ["14_context/compact_memory/current_working_summary.md"],
             "output_target": "14_context/agent_os/swarm_plans/content/idea_candidates.md",
             "owned_files": ["14_context/agent_os/runs/swarm/researcher/"],
             "dependencies": [], "capabilities": ["repo_read", "plan_render"],
             "risk_note": "Read + plan only."},
            {"worker_id": "content", "purpose": "Draft a script outline and title variants.",
             "required_inputs": ["idea_candidates"],
             "output_target": "14_context/agent_os/swarm_plans/content/script_drafts.md",
             "owned_files": ["14_context/agent_os/runs/swarm/content/"],
             "dependencies": [1], "capabilities": ["repo_read", "plan_render", "report_write_repo_local"],
             "risk_note": "Drafts only; no posting or uploads."},
            {"worker_id": "planner", "purpose": "Assemble a manual publish checklist (human runs every live step).",
             "required_inputs": ["script_drafts"],
             "output_target": "14_context/agent_os/swarm_plans/content/publish_checklist.md",
             "owned_files": ["14_context/agent_os/runs/swarm/planner/"],
             "dependencies": [2], "capabilities": ["repo_read", "plan_render", "report_write_repo_local"],
             "risk_note": "Checklist only; nothing is published."},
        ],
    },
    "business-research-swarm-plan": {
        "title": "Business Research Swarm Plan",
        "base_workflow": "business-research",
        "steps": [
            {"worker_id": "planner", "purpose": "Define the hypothesis and success criteria.",
             "required_inputs": ["14_context/compact_memory/current_working_summary.md"],
             "output_target": "14_context/agent_os/swarm_plans/business/hypothesis_brief.md",
             "owned_files": ["14_context/agent_os/runs/swarm/planner/"],
             "dependencies": [], "capabilities": ["repo_read", "plan_render"],
             "risk_note": "Read + plan only."},
            {"worker_id": "researcher", "purpose": "Draft research questions and a human-run source checklist.",
             "required_inputs": ["hypothesis_brief"],
             "output_target": "14_context/agent_os/swarm_plans/business/research_checklist.md",
             "owned_files": ["14_context/agent_os/runs/swarm/researcher/"],
             "dependencies": [1], "capabilities": ["repo_read", "plan_render", "report_write_repo_local"],
             "risk_note": "No purchases, signups, or live scraping; checklist only."},
        ],
    },
}

WORKFLOW_ORDER = [
    "coding-task-swarm-plan", "content-pipeline-swarm-plan", "business-research-swarm-plan",
]

# In-flight = queued for execution but not yet executed.
_IN_FLIGHT_STATES = {"queued", "approved"}


def _queue():
    """Construct the shared approval queue. Indirection so tests can inject an
    isolated queue; production always reuses the one real ApprovalQueue."""
    return approval_queue.ApprovalQueue()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _canonical(data) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _norm(path: str) -> str:
    return str(path).strip().lower().replace("\\", "/")


def _ownership_overlaps(steps: list[dict]) -> list[dict]:
    """Independent steps (no dependency path between them) must not share an
    owned-file prefix - that is what makes one-at-a-time scheduling safe."""
    overlaps: list[dict] = []
    for i, a in enumerate(steps):
        for b in steps[i + 1:]:
            if _dependency_linked(steps, a["step"], b["step"]):
                continue
            for pa in a["owned_files"]:
                for pb in b["owned_files"]:
                    na, nb = _norm(pa), _norm(pb)
                    if na.startswith(nb) or nb.startswith(na):
                        overlaps.append({"steps": sorted([a["step"], b["step"]]), "path": na})
    return overlaps


def _dependency_linked(steps: list[dict], a_id: int, b_id: int) -> bool:
    by_id = {s["step"]: s for s in steps}

    def reaches(start: int, target: int, seen: set) -> bool:
        if start in seen:
            return False
        seen.add(start)
        for dep in by_id.get(start, {}).get("dependencies", []):
            if dep == target or reaches(dep, target, seen):
                return True
        return False

    return reaches(a_id, b_id, set()) or reaches(b_id, a_id, set())


def validate_workflow(workflow: str) -> dict:
    spec = SWARM_WORKFLOWS.get(workflow)
    if spec is None:
        return {"ok": False, "errors": ["unknown swarm workflow: %s" % workflow]}
    errors: list[str] = []
    for idx, step in enumerate(spec["steps"], 1):
        if step["worker_id"] not in KNOWN_WORKERS:
            errors.append("step %d: unknown worker %s" % (idx, step["worker_id"]))
        caps = set(step.get("capabilities", []))
        blocked = caps & BLOCKED_CAPABILITIES
        if blocked:
            errors.append("step %d: blocked capability %s" % (idx, sorted(blocked)))
        unknown = caps - ALLOWED_CAPABILITIES
        if unknown:
            errors.append("step %d: capability not allowlisted %s" % (idx, sorted(unknown)))
        for dep in step.get("dependencies", []):
            if dep < 1 or dep >= idx:
                errors.append("step %d: dependency %s must reference an earlier step" % (idx, dep))
    return {"ok": not errors, "errors": errors}


def build_plan(workflow: str, created_at: str | None = None) -> dict:
    """Deterministic plan: same workflow -> same plan_id and fingerprint."""
    validation = validate_workflow(workflow)
    if not validation["ok"]:
        return {"ok": False, "workflow": workflow, "errors": validation["errors"]}
    spec = SWARM_WORKFLOWS[workflow]
    created = created_at or _now()
    steps = []
    for idx, raw in enumerate(spec["steps"], 1):
        steps.append({
            "step": idx,
            "worker_id": raw["worker_id"],
            "purpose": raw["purpose"],
            "required_inputs": list(raw["required_inputs"]),
            "output_target": raw["output_target"],
            "status": "planned",
            "owned_files": list(raw["owned_files"]),
            "dependencies": list(raw["dependencies"]),
            "risk_note": raw["risk_note"],
            "capabilities": list(raw["capabilities"]),
        })
    overlaps = _ownership_overlaps(steps)
    for ov in overlaps:
        for sid in ov["steps"][1:]:  # keep first runnable, block the rest
            steps[sid - 1]["status"] = "blocked"
            steps[sid - 1]["risk_note"] += " [blocked: owned-file overlap with step %d]" % ov["steps"][0]
    fingerprint = hashlib.sha256(_canonical(
        {"workflow": workflow, "base": spec["base_workflow"],
         "steps": [{k: s[k] for k in ("worker_id", "purpose", "owned_files",
                                      "dependencies", "capabilities")} for s in steps]}
    ).encode("utf-8")).hexdigest()
    plan_id = "swarm-" + fingerprint[:20]
    return {
        "ok": True,
        "schema": SCHEMA,
        "plan_id": plan_id,
        "workflow": workflow,
        "base_workflow": spec["base_workflow"],
        "title": spec["title"],
        "created_at": created,
        "fingerprint": fingerprint,
        "single_worker_lock": True,
        "mode": "planning_only",
        "steps": steps,
        "safety": {
            "parallel_execution": False,
            "max_workers_in_flight": 1,
            "live_execution": False,
            "queue_through_approval_queue": True,
        },
    }


def _render_markdown(plan: dict) -> str:
    lines = [
        "# Ghoti Swarm Plan - %s" % plan["title"],
        "",
        "Plan id: `%s`" % plan["plan_id"],
        "Workflow: `%s` (base `%s`)" % (plan["workflow"], plan["base_workflow"]),
        "Created: %s" % plan["created_at"],
        "Fingerprint: `%s`" % plan["fingerprint"],
        "Mode: planning_only; single-worker lock; at most one worker in flight.",
        "",
        "## Steps",
        "",
    ]
    for s in plan["steps"]:
        deps = ", ".join(str(d) for d in s["dependencies"]) or "none"
        lines.append("%d. [%s] **%s** - %s" % (s["step"], s["status"], s["worker_id"], s["purpose"]))
        lines.append("   - inputs: %s" % ", ".join(s["required_inputs"]))
        lines.append("   - output: `%s`" % s["output_target"])
        lines.append("   - owns: %s" % ", ".join(s["owned_files"]))
        lines.append("   - depends on: %s" % deps)
        lines.append("   - capabilities: %s" % ", ".join(s["capabilities"]))
        lines.append("   - risk: %s" % s["risk_note"])
    lines += [
        "",
        "## Safety",
        "",
        "- No parallel process launch; at most one worker queued at a time.",
        "- Every execution still goes through the approval queue + Rust guard.",
        "- No browser, computer-use, account, money, posting, or email actions.",
        "",
    ]
    return "\n".join(lines)


def write_plan(workflow: str, created_at: str | None = None) -> dict:
    plan = build_plan(workflow, created_at)
    if not plan.get("ok"):
        return plan
    # plan_id is deterministic from content, so re-planning the same workflow is
    # idempotent. If the plan already exists, preserve its step state (queued /
    # executed) instead of clobbering it back to "planned".
    existing = load_plan(plan["plan_id"])
    if existing is not None:
        existing["already_existed"] = True
        existing["plan_path"] = (
            SWARM_PLANS_DIR / ("%s.json" % plan["plan_id"])).relative_to(REPO_ROOT).as_posix()
        existing["plan_markdown_path"] = (
            SWARM_PLANS_DIR / ("%s.md" % plan["plan_id"])).relative_to(REPO_ROOT).as_posix()
        return existing
    SWARM_PLANS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = SWARM_PLANS_DIR / ("%s.json" % plan["plan_id"])
    md_path = SWARM_PLANS_DIR / ("%s.md" % plan["plan_id"])
    json_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(plan), encoding="utf-8")
    plan["plan_path"] = json_path.relative_to(REPO_ROOT).as_posix()
    plan["plan_markdown_path"] = md_path.relative_to(REPO_ROOT).as_posix()
    return plan


def load_plan(plan_id: str) -> dict | None:
    path = SWARM_PLANS_DIR / ("%s.json" % plan_id)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_plans() -> dict:
    plans = []
    if SWARM_PLANS_DIR.is_dir():
        for path in sorted(SWARM_PLANS_DIR.glob("swarm-*.json")):
            try:
                plan = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            plans.append({"plan_id": plan["plan_id"], "workflow": plan["workflow"],
                          "created_at": plan.get("created_at"),
                          "step_count": len(plan["steps"]),
                          "fingerprint": plan.get("fingerprint")})
    return {"ok": True, "action": "list-swarm-plans", "count": len(plans),
            "plans": plans, "available_workflows": WORKFLOW_ORDER}


def _approval_state(request_id: str | None) -> str | None:
    if not request_id:
        return None
    try:
        state, _ = _queue()._find(request_id)
        return state
    except Exception:
        return None


def _reconcile(plan: dict) -> dict:
    """Reflect the live approval-queue state of each queued step back into the plan."""
    in_flight = None
    for step in plan["steps"]:
        rid = step.get("request_id")
        state = _approval_state(rid)
        if state == "executed":
            step["status"] = "executed"
        elif state == "approved":
            step["status"] = "approved"
            in_flight = step["step"]
        elif state in ("pending",):
            step["status"] = "queued"
            in_flight = step["step"]
        elif state == "rejected":
            step["status"] = "planned"
            step["request_id"] = None
    return {"plan": plan, "in_flight_step": in_flight}


def next_runnable_step(plan: dict) -> dict | None:
    by_id = {s["step"]: s for s in plan["steps"]}
    for step in plan["steps"]:
        if step["status"] != "planned":
            continue
        if all(by_id[d]["status"] == "executed" for d in step["dependencies"]):
            return step
    return None


def queue_next_step(plan_id: str) -> dict:
    """Queue the next runnable step as ONE approval request. No execution."""
    plan = load_plan(plan_id)
    if plan is None:
        return {"ok": False, "action": "queue-next-swarm-step", "error": "unknown plan id"}
    reconciled = _reconcile(plan)
    if reconciled["in_flight_step"] is not None:
        return {"ok": False, "action": "queue-next-swarm-step", "plan_id": plan_id,
                "reason": "one_worker_lock", "in_flight_step": reconciled["in_flight_step"],
                "message": "A step is already in flight; only one worker at a time."}
    step = next_runnable_step(plan)
    if step is None:
        remaining = [s["step"] for s in plan["steps"] if s["status"] not in ("executed",)]
        return {"ok": True, "action": "queue-next-swarm-step", "plan_id": plan_id,
                "queued": None, "message": "No runnable step (done or blocked).",
                "remaining_steps": remaining}
    content = "\n".join([
        "# Swarm step %d - %s" % (step["step"], step["worker_id"]),
        "",
        "Plan: %s (%s)" % (plan_id, plan["workflow"]),
        "Purpose: %s" % step["purpose"],
        "Output target: %s" % step["output_target"],
        "Risk: %s" % step["risk_note"],
        "",
        "This step is suggestion-only until a human approves and executes it.",
        "",
    ])
    request = approval_queue.build_action_request(
        workflow_id=plan["base_workflow"], content=content,
        created_by="agent-os-swarm")
    result = _queue().propose(request)
    if not result.get("ok"):
        return {"ok": False, "action": "queue-next-swarm-step", "plan_id": plan_id,
                "reason": "guard_denied", "guard_decision": result.get("guard_decision")}
    step["status"] = "queued"
    step["request_id"] = result["request_id"]
    SWARM_PLANS_DIR.mkdir(parents=True, exist_ok=True)
    (SWARM_PLANS_DIR / ("%s.json" % plan_id)).write_text(
        json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True, "action": "queue-next-swarm-step", "plan_id": plan_id,
        "queued_step": step["step"], "worker_id": step["worker_id"],
        "request_id": result["request_id"], "approval_state": "pending",
        "executed": False,
        "message": "Approval request created. Approve and execute it via the "
                   "approval queue to run this one step.",
    }


def swarm_status() -> dict:
    listing = list_plans()
    plans = []
    for entry in listing["plans"]:
        plan = load_plan(entry["plan_id"])
        if plan is None:
            continue
        reconciled = _reconcile(plan)
        plans.append({
            "plan_id": plan["plan_id"], "workflow": plan["workflow"],
            "in_flight_step": reconciled["in_flight_step"],
            "steps": [{"step": s["step"], "worker_id": s["worker_id"],
                       "status": s["status"]} for s in plan["steps"]],
            "runnable_step": (next_runnable_step(plan) or {}).get("step"),
        })
    return {"ok": True, "action": "swarm-status", "plan_count": len(plans),
            "plans": plans, "single_worker_lock": True, "live_execution": False}


def full_swarm_planning_demo() -> dict:
    stamp = _now()
    built = []
    for workflow in WORKFLOW_ORDER:
        plan = write_plan(workflow, created_at=stamp)
        built.append({"workflow": workflow, "ok": plan.get("ok"),
                      "plan_id": plan.get("plan_id"),
                      "plan_path": plan.get("plan_path")})
    # Queue exactly one step on the first plan to prove the approval path.
    queued = queue_next_step(built[0]["plan_id"]) if built and built[0]["ok"] else {"ok": False}
    all_ok = all(b["ok"] for b in built) and queued.get("ok")
    lines = [
        "# Ghoti Swarm Planning - Full Demo Evidence",
        "",
        "Generated: %s" % stamp,
        "",
        "## Plans built",
        "",
    ]
    for b in built:
        lines.append("- %s -> `%s` (%s)" % (b["workflow"], b.get("plan_id"), b.get("plan_path")))
    lines += [
        "",
        "## One queued step (approval request, not execution)",
        "",
        "- plan: `%s`" % built[0].get("plan_id") if built else "- none",
        "- queued step: %s" % queued.get("queued_step"),
        "- approval request: `%s`" % queued.get("request_id"),
        "- executed: %s" % queued.get("executed"),
        "",
        "## Truth",
        "",
        "- At most one worker is ever in flight (single-worker lock).",
        "- The queued step is a pending approval request; nothing was executed.",
        "- No parallel launch, no browser/computer-use/account/money/posting.",
        "",
    ]
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    base = "full_swarm_planning_demo_%s" % stamp
    md_path = EVIDENCE_DIR / (base + ".md")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    payload = {
        "ok": bool(all_ok), "action": "full-swarm-planning-demo",
        "generated_at": stamp, "plans": built, "queued": queued,
        "evidence_path": md_path.relative_to(REPO_ROOT).as_posix(),
        "single_worker_lock": True, "live_execution": False,
    }
    json_path = EVIDENCE_DIR / (base + ".json")
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    payload["evidence_json_path"] = json_path.relative_to(REPO_ROOT).as_posix()
    return payload


def list_swarm_workflows() -> dict:
    return {"ok": True, "action": "list-swarm-workflows",
            "workflows": [{"id": w, "title": SWARM_WORKFLOWS[w]["title"],
                           "base_workflow": SWARM_WORKFLOWS[w]["base_workflow"],
                           "step_count": len(SWARM_WORKFLOWS[w]["steps"])}
                          for w in WORKFLOW_ORDER],
            "known_workers": sorted(KNOWN_WORKERS)}
