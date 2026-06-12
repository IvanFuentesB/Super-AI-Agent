"""Ghoti Agent OS - integrated command center CLI.

One entry point that composes the existing finished parts instead of
duplicating them: operator recipes (policy gate), compact memory and the
context pack, the Obsidian vault, agent lanes/locks, the prompt bus and
relay pairs, the local model probe, and the suggestion-only worker.

Everything is local, supervised, and deny-by-default. The only writes
are repo-local files under 14_context/agent_os/ (plans, suggestions,
handoffs, evidence). No agent is launched; packets are copy-paste only.

Usage:
  python 03_scripts/agent_os/ghoti_agent_os.py --status --json
  python 03_scripts/agent_os/ghoti_agent_os.py --list-workflows --json
  python 03_scripts/agent_os/ghoti_agent_os.py --plan-workflow content-video --json
  python 03_scripts/agent_os/ghoti_agent_os.py --task-wave coding-task --json
  python 03_scripts/agent_os/ghoti_agent_os.py --worker-suggest content-video --json
  python 03_scripts/agent_os/ghoti_agent_os.py --build-handoff --json
  python 03_scripts/agent_os/ghoti_agent_os.py --search-memory ghoti --json
  python 03_scripts/agent_os/ghoti_agent_os.py --ownership-check --json
  python 03_scripts/agent_os/ghoti_agent_os.py --check --json
  python 03_scripts/agent_os/ghoti_agent_os.py --full-demo --json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import local_worker  # noqa: E402
import agent_os_guard_bridge  # noqa: E402
import workflow_templates  # noqa: E402

REPO_ROOT = SCRIPT_DIR.parents[1]
RECIPES_SCRIPT = REPO_ROOT / "03_scripts" / "operator_recipes" / "ghoti_operator_recipes.py"
ACTIVE_LOCKS = REPO_ROOT / "14_context" / "agent_lanes" / "active_locks.jsonl"
PROMPT_BUS_OUTBOX = REPO_ROOT / "14_context" / "prompt_bus" / "outbox"
RELAY_PAIRS_DIR = REPO_ROOT / "14_context" / "agent_relay" / "pairs"
CONTEXT_PACK_JSON = REPO_ROOT / "14_context" / "compact_memory" / "generated" / "ghoti_current_context_pack.json"
OBSIDIAN_VAULT = REPO_ROOT / "14_context" / "obsidian_vault"
OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"
RUST_CHECKER_CANDIDATES = [
    REPO_ROOT / "rust" / "target" / "release" / "ghoti_policy_checker",
    REPO_ROOT / "rust" / "target" / "release" / "ghoti_policy_checker.exe",
    REPO_ROOT / "rust" / "target" / "debug" / "ghoti_policy_checker",
    REPO_ROOT / "rust" / "target" / "debug" / "ghoti_policy_checker.exe",
]

_recipes_module = None


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safety_flags() -> dict:
    return {
        "no_live_actions": True,
        "provider_api_used": False,
        "agents_launched": False,
        "accounts_touched": False,
        "localhost_only_network": True,
        "writes_repo_local_generated_only": True,
        "relay_mode": "copy_paste_only",
        "human_approval_required": True,
    }


def _load_recipes_module():
    """Import the operator recipes module from its file (policy gate reuse)."""
    global _recipes_module
    if _recipes_module is not None:
        return _recipes_module
    spec = importlib.util.spec_from_file_location("ghoti_operator_recipes", RECIPES_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _recipes_module = module
    return module


def check_workflow_policy(workflow_id: str, capabilities: list[str]) -> dict:
    """Deny-by-default capability check via the shared recipes policy gate."""
    try:
        recipes = _load_recipes_module()
        return recipes.check_recipe_policy("agent-os-" + workflow_id, capabilities)
    except Exception as error:  # gate must fail closed, never open
        return {"policy_check_passed": False, "decision": "deny",
                "checker": "unavailable", "reasons": ["policy gate import failed"],
                "denied_capabilities": capabilities, "error": str(error)}


def _git(args: list[str]) -> str:
    try:
        proc = subprocess.run(["git"] + args, capture_output=True, text=True,
                              cwd=str(REPO_ROOT), timeout=30, shell=False)
        return proc.stdout.strip()
    except Exception:
        return ""


def _probe_ollama() -> dict:
    """Local model probe: ollama on PATH + localhost tags endpoint. No pulls."""
    found = shutil.which("ollama") is not None
    endpoint_up = False
    models: list[str] = []
    try:
        with urllib.request.urlopen(OLLAMA_TAGS_URL, timeout=3) as resp:  # noqa: S310 - localhost only
            data = json.loads(resp.read().decode("utf-8"))
        endpoint_up = True
        models = sorted(m.get("name", "") for m in data.get("models", []))
    except Exception:
        pass
    return {"ollama_command_found": found, "ollama_endpoint_up": endpoint_up,
            "models": models, "auto_pull": False}


def _read_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except OSError:
        pass
    return records


def _memory_status() -> dict:
    compact = REPO_ROOT / "14_context" / "compact_memory"
    canonical = [p.name for p in sorted(compact.glob("*.md"))]
    snapshots = sorted(compact.glob("n4_2a_snapshot_*.md"))
    pack_meta: dict = {"exists": CONTEXT_PACK_JSON.is_file()}
    if pack_meta["exists"]:
        try:
            pack = json.loads(CONTEXT_PACK_JSON.read_text(encoding="utf-8"))
            pack_meta["generated_at"] = pack.get("generated_at")
            pack_meta["main_hash"] = pack.get("main_hash")
        except Exception:
            pack_meta["parse_error"] = True
    obsidian_index = OBSIDIAN_VAULT / "00_Index.md"
    return {
        "compact_memory_dir": "14_context/compact_memory",
        "canonical_file_count": len(canonical),
        "snapshot_count": len(snapshots),
        "context_pack": pack_meta,
        "obsidian": {
            "vault_path": "14_context/obsidian_vault",
            "start_note": "14_context/obsidian_vault/00_Index.md",
            "start_note_exists": obsidian_index.is_file(),
            "note_count": len(list(OBSIDIAN_VAULT.glob("*.md"))) if OBSIDIAN_VAULT.is_dir() else 0,
        },
        "search_sources": local_worker.SEARCH_ROOTS,
    }


def _handoff_status() -> dict:
    agent_os_handoffs = sorted(local_worker.HANDOFFS_DIR.glob("*.md")) \
        if local_worker.HANDOFFS_DIR.is_dir() else []
    outbox = sorted(PROMPT_BUS_OUTBOX.glob("*.md")) if PROMPT_BUS_OUTBOX.is_dir() else []
    pairs = sorted(p.name for p in RELAY_PAIRS_DIR.iterdir() if p.is_dir()) \
        if RELAY_PAIRS_DIR.is_dir() else []
    return {
        "agent_os_handoff_count": len(agent_os_handoffs),
        "latest_agent_os_handoff": agent_os_handoffs[-1].name if agent_os_handoffs else None,
        "prompt_bus_outbox_count": len(outbox),
        "relay_pair_count": len(pairs),
        "latest_relay_pair": pairs[-1] if pairs else None,
        "inbox_vault": "14_context/agent_handoff_vault/02_Agent_Handoffs",
    }


def _worker_mode() -> dict:
    approval_present = local_worker.APPROVAL_FILE.is_file()
    return {
        "mode": "suggestion_only",
        "approval_file": "14_context/agent_os/APPROVED_ACTIONS.json",
        "approval_file_present": approval_present,
        "approved_extra_output_dirs": [
            str(p.relative_to(REPO_ROOT)) for p in local_worker._approved_extra_roots()
        ] if approval_present else [],
        "can_run_approved_local_worker": approval_present,
        "label": "approved_local_action_paths_extended" if approval_present
                 else "suggestion_only",
    }


def cmd_status() -> dict:
    locks = [r for r in _read_jsonl(ACTIVE_LOCKS) if isinstance(r, dict)]
    recipes_info: dict = {"available": False}
    try:
        recipes = _load_recipes_module()
        listing = recipes.list_recipes()
        recipes_info = {"available": True, "count": listing["count"],
                        "ids": [r["id"] for r in listing["recipes"]]}
    except Exception as error:
        recipes_info["error"] = str(error)
    return {
        "ok": True,
        "action": "status",
        "product": "Ghoti Agent OS Command Center",
        "repo": {
            "branch": _git(["branch", "--show-current"]) or "detached",
            "head": _git(["rev-parse", "--short=12", "HEAD"]),
            "dirty_file_count": len([l for l in _git(["status", "--porcelain"]).splitlines() if l.strip()]),
        },
        "recipes": recipes_info,
        "memory": _memory_status(),
        "handoffs": _handoff_status(),
        "lanes": {
            "active_lock_records": len(locks),
            "registry": "14_context/agent_lanes/agent_lane_registry.json",
        },
        "local_model": _probe_ollama(),
        "worker": _worker_mode(),
        "agent_os_guard": agent_os_guard_bridge.guard_status(),
        "workflows": {"count": len(workflow_templates.WORKFLOW_ORDER),
                      "ids": workflow_templates.WORKFLOW_ORDER},
        "rust_checker_built": any(c.is_file() for c in RUST_CHECKER_CANDIDATES),
        "simulation_only_remaining": ["agent_arena visual swarm"],
        "safety_flags": _safety_flags(),
        "generated_at": _now(),
    }


def cmd_list_workflows() -> dict:
    payload = workflow_templates.list_templates()
    payload["action"] = "list-workflows"
    payload["generated_at"] = _now()
    payload["safety_flags"] = _safety_flags()
    return payload


def cmd_guard_status() -> dict:
    payload = dict(agent_os_guard_bridge.guard_status())
    payload["action"] = "guard-status"
    payload["safety_flags"] = _safety_flags()
    return payload


def cmd_plan_workflow(workflow_id: str) -> dict:
    template = workflow_templates.get_template(workflow_id)
    if template is None:
        return {"ok": False, "action": "plan-workflow", "workflow": workflow_id,
                "error": "unknown workflow id",
                "known_ids": workflow_templates.WORKFLOW_ORDER}
    policy = check_workflow_policy(workflow_id, template["capabilities"])
    if not policy.get("policy_check_passed"):
        return {"ok": False, "action": "plan-workflow", "workflow": workflow_id,
                "mode": "policy_denied", "policy": policy,
                "generated_at": _now(), "safety_flags": _safety_flags()}
    stamp = _now()
    branch = _git(["branch", "--show-current"]) or "detached"
    pointers = local_worker.read_memory_pointers()
    plan_md = workflow_templates.render_plan_markdown(workflow_id, stamp, branch,
                                                      memory_pointers=pointers)
    base = "%s_plan_%s" % (workflow_id.replace("-", "_"), stamp)
    md_result = local_worker._write_text(local_worker.WORKFLOWS_DIR / (base + ".md"), plan_md)
    wave = workflow_templates.build_task_wave(workflow_id)
    payload = {
        "ok": md_result["written"],
        "action": "plan-workflow",
        "workflow": workflow_id,
        "mode": "suggestion_only",
        "plan_path": md_result["path"] if md_result["written"] else None,
        "task_wave": wave,
        "policy": policy,
        "memory_pointers": pointers,
        "generated_at": stamp,
        "safety_flags": _safety_flags(),
    }
    json_result = local_worker._write_text(
        local_worker.WORKFLOWS_DIR / (base + ".json"), json.dumps(payload, indent=2) + "\n")
    payload["plan_json_path"] = json_result["path"] if json_result["written"] else None
    return payload


def cmd_task_wave(workflow_id: str) -> dict:
    wave = workflow_templates.build_task_wave(workflow_id)
    wave["action"] = "task-wave"
    wave["generated_at"] = _now()
    wave["safety_flags"] = _safety_flags()
    return wave


def _python_ownership_check(assignments: list[dict]) -> dict:
    """Mirror of the Rust ownership check: flag any path prefix two agents share."""
    overlaps: list[dict] = []
    seen: list[tuple[str, str]] = []  # (agent, normalized path)
    for entry in assignments:
        agent = str(entry.get("agent", "?"))
        for raw in entry.get("files", []):
            norm = str(raw).strip().lower().replace("\\", "/")
            for other_agent, other_path in seen:
                if other_agent != agent and (
                        norm.startswith(other_path) or other_path.startswith(norm)):
                    overlaps.append({"file": norm, "agents": sorted({agent, other_agent})})
            seen.append((agent, norm))
    merged: dict[str, set] = {}
    for o in overlaps:
        merged.setdefault(o["file"], set()).update(o["agents"])
    overlap_list = [{"file": f, "agents": sorted(a)} for f, a in sorted(merged.items())]
    return {"ok": True, "checker": "python_mirror_of_ghoti_policy_checker",
            "mode": "ownership_check", "overlap_count": len(overlap_list),
            "overlaps": overlap_list, "allowed": not overlap_list}


def _rust_ownership_check(assignments: list[dict]) -> dict | None:
    checker = next((c for c in RUST_CHECKER_CANDIDATES if c.is_file()), None)
    if checker is None:
        return None
    payload = {"wave_id": "agent-os-ownership", "assignments": assignments}
    plan_file = local_worker.RUNS_DIR / "ownership_check_input.json"
    write = local_worker._write_text(plan_file, json.dumps(payload, indent=2) + "\n")
    if not write["written"]:
        return None
    try:
        proc = subprocess.run([str(checker), "--ownership-input",
                               str(local_worker.RUNS_DIR / "ownership_check_input.json")],
                              capture_output=True, text=True, timeout=30, shell=False)
        return json.loads(proc.stdout)
    except Exception:
        return None


def _default_wave_assignments() -> list[dict]:
    """One assignment set per roster role, derived from every template step."""
    by_role: dict[str, set] = {}
    for wid in workflow_templates.WORKFLOW_ORDER:
        for step in workflow_templates.TEMPLATES[wid]["steps"]:
            by_role.setdefault(step["role"], set()).update(step["owned_paths"])
    return [{"agent": role, "files": sorted(paths)} for role, paths in sorted(by_role.items())]


def cmd_ownership_check(wave_input: str | None) -> dict:
    if wave_input:
        source = Path(wave_input)
        try:
            source.resolve().relative_to(REPO_ROOT)
        except ValueError:
            return {"ok": False, "action": "ownership-check",
                    "error": "wave input must be a repo-local file"}
        try:
            assignments = json.loads(source.read_text(encoding="utf-8")).get("assignments", [])
        except Exception as error:
            return {"ok": False, "action": "ownership-check", "error": str(error)}
    else:
        assignments = _default_wave_assignments()
    decision = _rust_ownership_check(assignments)
    rust_used = decision is not None
    if decision is None:
        decision = _python_ownership_check(assignments)
    decision.update({
        "action": "ownership-check",
        "rust_checker_used": rust_used,
        "assignments": assignments,
        "generated_at": _now(),
        "safety_flags": _safety_flags(),
    })
    return decision


def cmd_search_memory(term: str) -> dict:
    result = local_worker.search_memory(term)
    result["action"] = "search-memory"
    result["generated_at"] = _now()
    return result


def cmd_worker_suggest(workflow_id: str) -> dict:
    template = workflow_templates.get_template(workflow_id)
    if template is None:
        return {"ok": False, "action": "worker-suggest", "workflow": workflow_id,
                "error": "unknown workflow id"}
    policy = check_workflow_policy(workflow_id, template["capabilities"])
    if not policy.get("policy_check_passed"):
        return {"ok": False, "action": "worker-suggest", "workflow": workflow_id,
                "mode": "policy_denied", "policy": policy,
                "generated_at": _now(), "safety_flags": _safety_flags()}
    branch = _git(["branch", "--show-current"]) or "detached"
    payload = local_worker.run_suggestion(workflow_id, branch=branch)
    payload["policy"] = policy
    payload["safety_flags"] = _safety_flags()
    return payload


def cmd_build_handoff(workflow_id: str | None) -> dict:
    branch = _git(["branch", "--show-current"]) or "detached"
    payload = local_worker.build_handoffs(workflow_id, branch=branch)
    payload["safety_flags"] = _safety_flags()
    return payload


def cmd_check() -> dict:
    checks: list[dict] = []

    def record(name: str, ok: bool, details: str) -> None:
        checks.append({"name": name, "ok": bool(ok), "details": details})

    fp1 = workflow_templates.template_fingerprint()
    fp2 = workflow_templates.template_fingerprint()
    record("templates_fingerprint_stable", fp1 == fp2, fp1[:16])

    bad_caps: list[str] = []
    for wid in workflow_templates.WORKFLOW_ORDER:
        policy = check_workflow_policy(wid, workflow_templates.TEMPLATES[wid]["capabilities"])
        if not policy.get("policy_check_passed"):
            bad_caps.append(wid)
    record("template_capabilities_pass_policy", not bad_caps,
           "denied: %s" % ", ".join(bad_caps) if bad_caps else "all workflows allowed")

    deny = check_workflow_policy("self-test-deny", ["external_write"])
    record("policy_gate_denies_blocked_capability",
           not deny.get("policy_check_passed"), deny.get("decision", "?"))

    probe = local_worker._write_text(local_worker.RUNS_DIR / "write_probe.json",
                                     json.dumps({"probe": True}) + "\n")
    record("generated_dirs_writable", probe["written"], probe["path"])

    refused = local_worker._write_text(REPO_ROOT / "03_scripts" / "agent_os_probe.tmp", "x")
    record("writes_outside_agent_os_refused", not refused["written"],
           refused["refused"] or "unexpectedly written")

    overlap = _python_ownership_check([
        {"agent": "a", "files": ["03_scripts/x.py"]},
        {"agent": "b", "files": ["03_scripts/x.py"]},
    ])
    record("ownership_check_catches_overlap", overlap["overlap_count"] == 1,
           "%d overlap(s) in fixture" % overlap["overlap_count"])

    clean = cmd_ownership_check(None)
    record("default_wave_has_no_overlap", clean.get("allowed", False),
           "%d overlap(s)" % clean.get("overlap_count", -1))

    search = local_worker.search_memory("ghoti", limit=3)
    record("memory_search_returns_pointers",
           search["ok"] and search["hit_count"] > 0,
           "%d hit(s)" % search.get("hit_count", 0))

    sample = workflow_templates.render_plan_markdown(
        "coding-task", "00000000T000000Z", "self-test")
    record("rendered_plan_is_ascii", all(ord(c) < 128 for c in sample),
           "%d chars" % len(sample))

    worker_source = (SCRIPT_DIR / "local_worker.py").read_text(encoding="utf-8")
    execution_markers = ("import subprocess", "from subprocess", "os.system(",
                         "os.popen(", "os.exec")
    record("local_worker_never_executes",
           not any(marker in worker_source for marker in execution_markers),
           "no execution primitive imported or called in local_worker.py")

    for guard_check in agent_os_guard_bridge.guard_check_records():
        record(guard_check["name"], guard_check["ok"], guard_check["details"])

    all_ok = all(c["ok"] for c in checks)
    return {"ok": all_ok, "action": "check", "checks": checks,
            "passed": sum(1 for c in checks if c["ok"]), "total": len(checks),
            "generated_at": _now(), "safety_flags": _safety_flags()}


def cmd_full_demo() -> dict:
    """One command that proves the integrated slice end to end."""
    stamp = _now()
    steps: list[dict] = []

    def run_step(name: str, payload: dict, ok_key: str = "ok") -> dict:
        steps.append({"step": name, "ok": bool(payload.get(ok_key)),
                      "summary": payload.get("error") or payload.get("action", name)})
        return payload

    status = run_step("status", cmd_status())
    check = run_step("check", cmd_check())
    search = run_step("memory-search", cmd_search_memory("memory"))
    plan = run_step("plan-workflow content-video", cmd_plan_workflow("content-video"))
    suggest = run_step("worker-suggest content-video", cmd_worker_suggest("content-video"))
    handoff = run_step("build-handoff content-video", cmd_build_handoff("content-video"))

    all_ok = all(s["ok"] for s in steps)
    artifacts = [p for p in [
        plan.get("plan_path"), plan.get("plan_json_path"),
        suggest.get("suggestion_path"), suggest.get("suggestion_json_path"),
    ] + list((handoff.get("packets") or {}).values()) if p]

    lines = [
        "# Ghoti Agent OS - Full Local Demo Evidence",
        "",
        "Generated: %s" % stamp,
        "Branch: %s" % (status["repo"]["branch"]),
        "Head: %s" % (status["repo"]["head"]),
        "",
        "---",
        "",
        "## Steps",
        "",
    ]
    for s in steps:
        lines.append("- [%s] %s" % ("ok" if s["ok"] else "FAIL", s["step"]))
    lines += ["", "## Created artifacts", ""]
    for a in artifacts:
        lines.append("- %s" % a)
    lines += [
        "",
        "## Truth summary",
        "",
        "- Self-check: %d/%d passed." % (check["passed"], check["total"]),
        "- Memory search hits for 'memory': %d." % search.get("hit_count", 0),
        "- Local model endpoint up: %s." % status["local_model"]["ollama_endpoint_up"],
        "- Worker mode: %s (no command executed)." % suggest.get("mode", "?"),
        "- Relay mode: copy_paste_only; nothing was launched, posted, or sent.",
        "",
    ]
    base = "full_local_demo_%s" % stamp
    md_result = local_worker._write_text(
        local_worker.EVIDENCE_DIR / (base + ".md"), "\n".join(lines))
    payload = {
        "ok": all_ok and md_result["written"],
        "action": "full-demo",
        "steps": steps,
        "artifacts": artifacts,
        "evidence_path": md_result["path"] if md_result["written"] else None,
        "generated_at": stamp,
        "safety_flags": _safety_flags(),
    }
    json_result = local_worker._write_text(
        local_worker.EVIDENCE_DIR / (base + ".json"), json.dumps(payload, indent=2) + "\n")
    payload["evidence_json_path"] = json_result["path"] if json_result["written"] else None
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ghoti Agent OS: integrated local supervised command center.")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--guard-status", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--list-workflows", action="store_true")
    parser.add_argument("--plan-workflow", metavar="ID")
    parser.add_argument("--task-wave", metavar="ID")
    parser.add_argument("--ownership-check", action="store_true")
    parser.add_argument("--wave-input", metavar="PATH",
                        help="Optional repo-local JSON with {assignments:[{agent,files[]}]}")
    parser.add_argument("--search-memory", metavar="TERM")
    parser.add_argument("--worker-suggest", metavar="ID")
    parser.add_argument("--build-handoff", action="store_true")
    parser.add_argument("--workflow", metavar="ID",
                        help="Workflow context for --build-handoff")
    parser.add_argument("--full-demo", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if args.status:
        payload = cmd_status()
    elif args.guard_status:
        payload = cmd_guard_status()
    elif args.check:
        payload = cmd_check()
    elif args.list_workflows:
        payload = cmd_list_workflows()
    elif args.plan_workflow:
        payload = cmd_plan_workflow(args.plan_workflow)
    elif args.task_wave:
        payload = cmd_task_wave(args.task_wave)
    elif args.ownership_check:
        payload = cmd_ownership_check(args.wave_input)
    elif args.search_memory:
        payload = cmd_search_memory(args.search_memory)
    elif args.worker_suggest:
        payload = cmd_worker_suggest(args.worker_suggest)
    elif args.build_handoff:
        payload = cmd_build_handoff(args.workflow)
    elif args.full_demo:
        payload = cmd_full_demo()
    else:
        parser.print_help()
        return 2

    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        print("Ghoti Agent OS - %s" % payload.get("action", "?"))
        print("ok: %s" % payload.get("ok"))
        for key in ("plan_path", "suggestion_path", "evidence_path"):
            if payload.get(key):
                print("%s: %s" % (key, payload[key]))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
