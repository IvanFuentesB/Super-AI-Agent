#!/usr/bin/env python3
"""Ghoti operator recipes: safe local supervised workflows (N+6.40A).

A "recipe" is a safe local supervised workflow. It can inspect, summarize,
validate, and write repo-local generated Markdown reports. It cannot touch
accounts, launch agents, call providers, submit forms, delete files, move
files, or modify folders outside the repo.

Every recipe run is checked against a deny-by-default capability policy.
When the Rust policy checker binary (rust/ghoti_policy_checker) is built,
it is invoked for real enforcement; otherwise a Python mirror of the same
policy (23_configs/operator_recipe_policy.example.json) enforces identical
deny-by-default rules.

Safety invariants (defensive, local, public-repo safety only):
- No live account actions. No agents launched. No provider/API calls.
- Network access is limited to localhost status reads (dashboard 127.0.0.1:3210,
  Ollama 127.0.0.1:11434). Nothing external. Nothing is posted anywhere.
- Writes go only to the repo-local generated reports folder by default.
- An --output-dir outside the repo is preview-only: the report content is
  returned in JSON but never written (no allowlisted external paths exist yet).
- No file is ever deleted, moved, or renamed by any recipe.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "14_context" / "operator_reports" / "generated"
RUNTIME_DATA_DIR = REPO_ROOT / "01_projects" / "dashboard_mvp" / "runtime_data"
POLICY_MANIFEST = REPO_ROOT / "23_configs" / "operator_recipe_policy.example.json"
LAUNCHER = REPO_ROOT / "03_scripts" / "ghoti_product_launcher.py"
PUBLIC_AUDIT = REPO_ROOT / "03_scripts" / "public_repo_security_audit.py"
FIXTURE_REPLAY = REPO_ROOT / "03_scripts" / "claude_swarm_fixture" / "ghoti_claude_swarm_fixture_replay.py"
RUST_CHECKER_CANDIDATES = [
    REPO_ROOT / "rust" / "target" / "release" / "ghoti_policy_checker",
    REPO_ROOT / "rust" / "target" / "release" / "ghoti_policy_checker.exe",
    REPO_ROOT / "rust" / "target" / "debug" / "ghoti_policy_checker",
    REPO_ROOT / "rust" / "target" / "debug" / "ghoti_policy_checker.exe",
]

DASHBOARD_STATUS_URL = "http://127.0.0.1:3210/api/product-control/status"
OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"

WHAT_REMAINS_DISABLED = (
    "Live agents, account actions, provider/API calls, Telegram, Obsidian, MCP, "
    "browser automation, computer-use, auto-submit, file deletion, file moves, "
    "and any write outside the repo. Blocking these is intentional."
)


# ===========================================================================
# Policy: deny-by-default capability check (Rust checker preferred, Python
# mirror otherwise). Both enforce the same allowed/blocked lists.
# ===========================================================================

def _load_policy_manifest() -> dict:
    try:
        return json.loads(POLICY_MANIFEST.read_text(encoding="utf-8"))
    except Exception:
        # Conservative built-in fallback: identical to the manifest defaults.
        return {
            "policy_version": "n6.40a-recipes-v1-builtin",
            "default_decision": "deny",
            "allowed_capabilities": [
                "fixture_read", "local_model_status_read", "local_policy_check",
                "plan_render", "repo_read", "report_write_repo_local", "status_read",
            ],
            "blocked_capabilities": [
                "account", "agent_launch", "auto_submit", "browser", "computer_use",
                "external_write", "file_delete", "file_move", "mass_message", "mcp",
                "money", "provider_api", "secrets", "telegram",
            ],
        }


def _find_rust_checker() -> Path | None:
    for candidate in RUST_CHECKER_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def _rust_policy_check(recipe_id: str, capabilities: list[str]) -> dict | None:
    """Invoke the real Rust policy checker if a built binary exists."""
    checker = _find_rust_checker()
    if checker is None:
        return None
    plan = {
        "plan_id": "operator-recipe-" + recipe_id,
        "dry_run": True,
        "live_launch": False,
        "requires_human_approval": True,
        "capabilities": capabilities,
    }
    # Plan file lives in repo-local gitignored runtime_data and is simply
    # overwritten on each run (never deleted, never moved).
    plan_file = RUNTIME_DATA_DIR / "operator_recipe_policy_plan.json"
    try:
        RUNTIME_DATA_DIR.mkdir(parents=True, exist_ok=True)
        plan_file.write_text(json.dumps(plan, indent=2), encoding="utf-8")
        proc = subprocess.run(
            [str(checker), "--input", str(plan_file)],
            capture_output=True, text=True, timeout=30, shell=False,
        )
        return json.loads(proc.stdout)
    except Exception:
        return None


def _python_policy_check(recipe_id: str, capabilities: list[str]) -> dict:
    """Python mirror of the Rust checker: deny-by-default, same lists."""
    manifest = _load_policy_manifest()
    allowed = set(manifest.get("allowed_capabilities", []))
    blocked = set(manifest.get("blocked_capabilities", []))
    reasons: list[str] = []
    blocked_caps: list[str] = []
    unknown_caps: list[str] = []
    for capability in capabilities:
        normalized = capability.strip().lower().replace(" ", "_").replace("-", "_")
        if normalized in blocked:
            blocked_caps.append(normalized)
        elif normalized not in allowed:
            unknown_caps.append(normalized)
    if blocked_caps:
        reasons.append("blocked_capability_requested")
    if unknown_caps:
        reasons.append("unknown_capability_requested")
    is_allowed = not reasons
    return {
        "ok": True,
        "checker": "python_mirror_of_ghoti_policy_checker",
        "policy_version": manifest.get("policy_version", "unknown"),
        "plan_id": "operator-recipe-" + recipe_id,
        "allowed": is_allowed,
        "decision": "allow" if is_allowed else "deny",
        "reasons": reasons,
        "blocked_capabilities": sorted(set(blocked_caps)),
        "unknown_capabilities": sorted(set(unknown_caps)),
    }


def check_recipe_policy(recipe_id: str, capabilities: list[str]) -> dict:
    """Check a recipe's requested capabilities; deny-by-default either way."""
    rust_available = _find_rust_checker() is not None
    decision = _rust_policy_check(recipe_id, capabilities) if rust_available else None
    rust_used = decision is not None
    if decision is None:
        decision = _python_policy_check(recipe_id, capabilities)
    denied = sorted(set(
        decision.get("blocked_capabilities", []) + decision.get("unknown_capabilities", [])
    ))
    return {
        "requested_capabilities": capabilities,
        "allowed_capabilities": [c for c in capabilities if c not in denied],
        "denied_capabilities": denied,
        "rust_checker_available": rust_available,
        "rust_checker_used": rust_used,
        "checker": decision.get("checker", "unknown"),
        "policy_version": decision.get("policy_version", "unknown"),
        "policy_check_passed": bool(decision.get("allowed")),
        "decision": decision.get("decision", "deny"),
        "reasons": decision.get("reasons", []),
    }


# ===========================================================================
# Local helpers (read-only git, repo-local python scripts, localhost HTTP)
# ===========================================================================

def _git(args: list[str], timeout: int = 30) -> str:
    """Run a read-only git command; never mutates anything."""
    try:
        proc = subprocess.run(
            ["git"] + args, capture_output=True, text=True,
            cwd=str(REPO_ROOT), timeout=timeout, shell=False,
        )
        return proc.stdout.strip()
    except Exception:
        return ""


def _run_repo_python(script: Path, args: list[str], timeout: int = 120) -> dict | None:
    """Run a repo-local python script with fixed argv; parse JSON stdout."""
    if not script.is_file():
        return None
    try:
        proc = subprocess.run(
            [sys.executable, str(script)] + args,
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            timeout=timeout, shell=False,
        )
        return json.loads(proc.stdout)
    except Exception:
        return None


def _local_http_json(url: str, timeout: int = 3) -> dict | None:
    """GET a localhost-only URL; refuses anything that is not 127.0.0.1/localhost."""
    if not (url.startswith("http://127.0.0.1") or url.startswith("http://localhost")):
        return None
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 - localhost only
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _is_under_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT)
        return True
    except ValueError:
        return False


# ===========================================================================
# Report rendering: every report has the same six honest sections.
# ===========================================================================

def _render_report(title: str, what_happened: str, did: list[str], refused: list[str],
                   created: list[str], next_actions: list[str], body_extra: str = "") -> str:
    lines = [
        "# " + title,
        "",
        "Generated: " + datetime.now(timezone.utc).isoformat(),
        "Generator: ghoti_operator_recipes.py (local supervised recipe)",
        "",
        "## What happened",
        "",
        what_happened,
        "",
        "## What Ghoti did",
        "",
    ]
    lines += ["- " + item for item in did] or ["- Nothing was executed."]
    lines += ["", "## What Ghoti refused to do", ""]
    lines += ["- " + item for item in refused]
    lines += ["", "## What files/reports were created", ""]
    lines += ["- " + item for item in created] or ["- None."]
    lines += ["", "## What the user can do next", ""]
    for index, action in enumerate(next_actions):
        prefix = "Next action: " if index == 0 else "Then: "
        lines.append("- " + prefix + action)
    lines += ["", "## What remains disabled", "", WHAT_REMAINS_DISABLED, ""]
    if body_extra:
        lines += ["---", "", body_extra, ""]
    return "\n".join(lines)


STANDARD_REFUSALS = [
    "Did not touch any account, provider, or external service.",
    "Did not launch any agent or external CLI.",
    "Did not delete, move, or rename any file.",
    "Did not write outside the repo-local generated reports folder.",
]


# ===========================================================================
# Recipe implementations. Each returns (summary, what_happened, did, extra_md,
# warnings, errors, next_actions, details).
# ===========================================================================

def _recipe_project_health() -> dict:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"
    head = _git(["rev-parse", "HEAD"]) or "unknown"
    main_sha = _git(["rev-parse", "origin/main"]) or "unknown"
    porcelain = _git(["status", "--porcelain"])
    dirty_count = len([ln for ln in porcelain.splitlines() if ln.strip()])

    warnings: list[str] = []
    did = [
        "Read current branch (%s) and HEAD (%s)." % (branch, head[:12]),
        "Read origin/main (%s)." % main_sha[:12],
        "Summarized git status: %d changed/untracked entries." % dirty_count,
    ]

    launcher = _run_repo_python(LAUNCHER, ["--status", "--json"], timeout=60)
    if launcher:
        did.append("Ran product launcher --status (dashboard_running=%s)."
                   % launcher.get("dashboard_running"))
    else:
        warnings.append("Product launcher status unavailable.")

    audit = _run_repo_python(PUBLIC_AUDIT, ["--run", "--json"], timeout=180)
    audit_blockers = None
    audit_warnings = None
    if audit:
        audit_blockers = len(audit.get("blocking_findings", []) or [])
        audit_warnings = len(audit.get("warning_findings", audit.get("warnings", [])) or [])
        did.append("Ran public repo security audit: %d blockers, %d warnings."
                   % (audit_blockers, audit_warnings))
    else:
        warnings.append("Public repo security audit could not be run.")

    rust_manifest = REPO_ROOT / "rust" / "Cargo.toml"
    rust_tracked = rust_manifest.is_file()
    if rust_tracked:
        did.append("Confirmed Rust workspace tracked at rust/Cargo.toml "
                   "(ghoti_policy_checker, ghoti_runtime_core).")

    dashboard = _local_http_json(DASHBOARD_STATUS_URL, timeout=2)
    dashboard_reachable = bool(dashboard and dashboard.get("ok"))
    did.append("Probed local dashboard status: %s."
               % ("reachable" if dashboard_reachable else "not running (normal when stopped)"))

    local_branches = _git(["branch", "--format=%(refname:short)"]).splitlines()
    feature_queue = [b for b in local_branches if b.startswith("feat/")][-8:]
    pr_queue = [
        "PR #14 - N+6.39A usability rescue (feature branch, awaiting Codex audit)",
        "PR #15 - N+6.39B demo-ready console (stacked on PR #14)",
        "Current branch - N+6.40A working MVP runtime recipes (this branch)",
    ]

    extra = "\n".join(
        ["### Detail", "",
         "| Item | Value |", "|------|-------|",
         "| Branch | %s |" % branch,
         "| HEAD | %s |" % head,
         "| origin/main | %s |" % main_sha,
         "| Dirty entries | %d |" % dirty_count,
         "| Audit blockers | %s |" % ("n/a" if audit_blockers is None else audit_blockers),
         "| Audit warnings | %s |" % ("n/a" if audit_warnings is None else audit_warnings),
         "| Rust workspace tracked | %s |" % rust_tracked,
         "| Dashboard reachable | %s |" % dashboard_reachable,
         "", "### PR / branch queue", ""]
        + ["- " + item for item in pr_queue]
        + ["", "### Local feature branches (latest)", ""]
        + ["- " + b for b in feature_queue]
        + ["", "### Blockers / next milestone", "",
           "- Codex is out of messages: PR #14 / PR #15 audits wait for credit reset.",
           "- Next recommended milestone: merge audits, then Obsidian curated memory."]
    )
    summary = ("Branch %s at %s; origin/main %s; %d dirty entries; audit blockers: %s; "
               "dashboard %s.") % (
        branch, head[:12], main_sha[:12], dirty_count,
        "n/a" if audit_blockers is None else audit_blockers,
        "reachable" if dashboard_reachable else "down",
    )
    return {
        "summary": summary,
        "what_happened": "Ghoti collected a full local project health snapshot: git truth, "
                         "launcher status, public security audit, Rust workspace status, "
                         "PR queue, and dashboard reachability.",
        "did": did, "extra": extra, "warnings": warnings, "errors": [],
        "next_actions": [
            "Read the generated project health report.",
            "Run `python 03_scripts/public_repo_security_audit.py --run --json` before sharing the repo.",
            "When Codex credits reset, request the PR #14 / #15 audits.",
        ],
        "details": {
            "branch": branch, "head": head, "origin_main": main_sha,
            "dirty_entries": dirty_count, "audit_blockers": audit_blockers,
            "dashboard_reachable": dashboard_reachable, "rust_tracked": rust_tracked,
        },
    }


def _recipe_handoff_pack() -> dict:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"
    head = _git(["rev-parse", "HEAD"]) or "unknown"
    main_sha = _git(["rev-parse", "origin/main"]) or "unknown"

    claude_packet = "\n".join([
        "```",
        "HANDOFF: Ghoti implementation continuation",
        "main: %s" % main_sha,
        "current branch: %s @ %s" % (branch, head),
        "PR queue: PR #14 (N+6.39A usability rescue), PR #15 (N+6.39B demo console,",
        "stacked on #14), current branch (N+6.40A working MVP runtime recipes).",
        "Merged on main: N+6.35B, N+6.36B, N+6.37B, N+6.38B.",
        "Blocked: Codex out of messages; audits wait for credit reset.",
        "Next: audit + merge PR queue, then Obsidian curated memory milestone.",
        "Hard rules: feature-branch-only push, no live actions, no provider keys,",
        "no Telegram/Obsidian/MCP this sprint, ASCII-safe PowerShell.",
        "```",
    ])
    codex_packet = "\n".join([
        "```",
        "AUDIT REQUEST (when credits reset)",
        "Target order: PR #14 first, then PR #15, then this branch.",
        "Audit branch names: audit/ghoti-agent-codex-n6-39a-ghoti-usability-rescue,",
        "audit/ghoti-agent-codex-n6-39b-demo-ready-operator-console,",
        "audit/ghoti-agent-codex-n6-40a-working-mvp-runtime-recipes.",
        "Verify: no AI attribution, no provider keys, no live actions, tests pass,",
        "public audit zero blockers, PowerShell ASCII-safe.",
        "```",
    ])
    ollama_models = _local_http_json(OLLAMA_TAGS_URL, timeout=3)
    model_names = []
    if ollama_models and isinstance(ollama_models.get("models"), list):
        model_names = [m.get("name", "?") for m in ollama_models["models"]]
    hermes_packet = "\n".join([
        "```",
        "HERMES / LOCAL MODEL STATUS",
        "Ollama endpoint 127.0.0.1:11434: %s" % ("UP" if ollama_models else "not responding"),
        "Models visible: %s" % (", ".join(model_names) if model_names else "none detected"),
        "Use Hermes/Ollama for cheap local status reads only.",
        "```",
    ])
    routing = "\n".join([
        "### Model routing", "",
        "- Hard implementation: use the strongest implementation lane while available.",
        "- Audit lane: Codex Extra High when credits reset.",
        "- Cheap local status: Hermes via Ollama.",
        "- Serious coordination only: GPT-5.5 Medium.",
    ])
    extra = "\n".join([
        "### Implementation continuation packet (copy-paste)", "", claude_packet, "",
        "### Audit packet (copy-paste)", "", codex_packet, "",
        "### Local model status packet (copy-paste)", "", hermes_packet, "",
        routing,
    ])
    return {
        "summary": "Handoff pack generated: implementation, audit, and local-model packets "
                   "for main %s / branch %s." % (main_sha[:12], branch),
        "what_happened": "Ghoti generated a copy-paste-ready handoff pack covering the "
                         "implementation lane, the audit lane (for when Codex credits reset), "
                         "and the local Hermes/Ollama status lane.",
        "did": [
            "Read git truth (branch %s, HEAD %s, origin/main %s)." % (branch, head[:12], main_sha[:12]),
            "Rendered three copy-paste packets (implementation, audit, local model).",
            "Probed local Ollama tags endpoint (localhost only) for the Hermes packet.",
        ],
        "extra": extra, "warnings": [], "errors": [],
        "next_actions": [
            "Copy the packet you need straight from the generated report.",
            "Paste the audit packet to Codex when credits reset.",
        ],
        "details": {"branch": branch, "head": head, "origin_main": main_sha,
                    "ollama_models": model_names},
    }


def _recipe_cleanup_preview() -> dict:
    porcelain = _git(["status", "--porcelain"]).splitlines()
    untracked = [ln[3:] for ln in porcelain if ln.startswith("??")][:50]
    modified = [ln[3:] for ln in porcelain if ln[:2].strip() and not ln.startswith("??")][:50]

    skip_dirs = {".git", "node_modules", "target", "__pycache__", ".venv", "venv"}
    large_files: list[tuple[str, int]] = []
    for path in REPO_ROOT.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        try:
            if path.is_file() and path.stat().st_size > 5 * 1024 * 1024:
                large_files.append((str(path.relative_to(REPO_ROOT)), path.stat().st_size))
        except OSError:
            continue
        if len(large_files) >= 20:
            break

    worktrees = _git(["worktree", "list", "--porcelain"])
    worktree_lines = [ln.split(" ", 1)[1] for ln in worktrees.splitlines()
                      if ln.startswith("worktree ")]

    cache_dirs = []
    for rel in ["01_projects/dashboard_mvp/runtime_data", "rust/target",
                "14_context/operator_reports/generated", "01_projects/dashboard_mvp/node_modules"]:
        candidate = REPO_ROOT / rel
        if candidate.is_dir():
            cache_dirs.append(rel)
    pycache_count = 0
    for path in REPO_ROOT.rglob("__pycache__"):
        if ".git" not in path.parts:
            pycache_count += 1
        if pycache_count >= 200:
            break

    log_files = []
    for path in REPO_ROOT.rglob("*.log"):
        if ".git" in path.parts or "node_modules" in path.parts:
            continue
        log_files.append(str(path.relative_to(REPO_ROOT)))
        if len(log_files) >= 20:
            break

    extra = "\n".join(
        ["### Untracked files (%d shown)" % len(untracked), ""]
        + (["- " + f for f in untracked] or ["- none"])
        + ["", "### Modified files (%d shown)" % len(modified), ""]
        + (["- " + f for f in modified] or ["- none"])
        + ["", "### Large files > 5 MB (%d shown)" % len(large_files), ""]
        + (["- %s (%.1f MB)" % (f, size / (1024 * 1024)) for f, size in large_files] or ["- none"])
        + ["", "### Worktrees", ""]
        + (["- " + w for w in worktree_lines] or ["- none"])
        + ["", "### Cache / generated folders", ""]
        + (["- " + d for d in cache_dirs] or ["- none"])
        + ["- __pycache__ folders found: %d" % pycache_count]
        + ["", "### Log files (%d shown)" % len(log_files), ""]
        + (["- " + f for f in log_files] or ["- none"])
        + ["", "**Preview only. Nothing was deleted, moved, or modified.**"]
    )
    return {
        "summary": "Cleanup preview: %d untracked, %d modified, %d large files, "
                   "%d cache folders, %d log files. Nothing was touched." % (
                       len(untracked), len(modified), len(large_files),
                       len(cache_dirs), len(log_files)),
        "what_happened": "Ghoti inspected the repo (read-only) and produced a cleanup "
                         "preview. It lists what could be reviewed for cleanup but it "
                         "deliberately deleted and moved nothing.",
        "did": [
            "Listed untracked and modified files from git status (read-only).",
            "Scanned for files over 5 MB outside cache folders.",
            "Listed worktrees, cache/generated folders, and *.log files.",
        ],
        "extra": extra, "warnings": [], "errors": [],
        "next_actions": [
            "Review the preview and decide manually what (if anything) to clean.",
            "Nothing in this recipe will ever delete for you - that stays manual.",
        ],
        "details": {
            "untracked_count": len(untracked), "modified_count": len(modified),
            "large_file_count": len(large_files), "log_file_count": len(log_files),
            "preview_only": True, "files_deleted": 0, "files_moved": 0,
        },
    }


def _recipe_local_model_check() -> dict:
    ollama_path = shutil.which("ollama")
    tags = _local_http_json(OLLAMA_TAGS_URL, timeout=3)
    model_names: list[str] = []
    if tags and isinstance(tags.get("models"), list):
        model_names = [m.get("name", "") for m in tags["models"]]

    def _has(prefix: str) -> bool:
        return any(name.startswith(prefix) for name in model_names)

    llama_ok = _has("llama3.1:8b")
    gemma_ok = _has("gemma3:4b")

    guidance = []
    if not ollama_path:
        guidance.append("Install Ollama first: https://ollama.com/download "
                        "(manual step; Ghoti will not install anything).")
    if not llama_ok:
        guidance.append("Pull llama3.1:8b manually: `ollama pull llama3.1:8b`")
    if not gemma_ok:
        guidance.append("Pull gemma3:4b manually: `ollama pull gemma3:4b`")
    if not guidance:
        guidance.append("All checked models are present. Nothing to install.")

    extra = "\n".join(
        ["### Local model readiness", "",
         "| Check | Result |", "|-------|--------|",
         "| ollama command on PATH | %s |" % ("yes (%s)" % ollama_path if ollama_path else "no"),
         "| Ollama HTTP 127.0.0.1:11434 | %s |" % ("responding" if tags else "not responding"),
         "| llama3.1:8b present | %s |" % ("yes" if llama_ok else "no"),
         "| gemma3:4b present | %s |" % ("yes" if gemma_ok else "no"),
         "", "### Models visible", ""]
        + (["- " + name for name in model_names] or ["- none detected"])
        + ["", "### Manual install / pull commands (Ghoti will NOT run these)", ""]
        + ["- " + g for g in guidance]
    )
    return {
        "summary": "Local model readiness: ollama %s, endpoint %s, llama3.1:8b %s, "
                   "gemma3:4b %s." % (
                       "found" if ollama_path else "missing",
                       "up" if tags else "down",
                       "present" if llama_ok else "missing",
                       "present" if gemma_ok else "missing"),
        "what_happened": "Ghoti checked local model readiness: the ollama command, the "
                         "localhost Ollama endpoint, and the expected models. Exact truth, "
                         "nothing faked; missing pieces come with manual commands only.",
        "did": [
            "Looked up the ollama command on PATH (no execution).",
            "Probed the localhost-only Ollama tags endpoint (127.0.0.1:11434).",
            "Checked for llama3.1:8b and gemma3:4b in the visible model list.",
        ],
        "extra": extra,
        "warnings": [] if (ollama_path or tags) else
                    ["Ollama is not available; this is informational, not a failure."],
        "errors": [],
        "next_actions": [
            "If a model is missing, run the listed pull command manually.",
            "Ghoti never pulls models automatically and never calls cloud providers.",
        ],
        "details": {
            "ollama_command_found": bool(ollama_path),
            "ollama_endpoint_up": bool(tags),
            "llama31_8b_present": llama_ok, "gemma3_4b_present": gemma_ok,
            "models": model_names, "auto_pull": False,
        },
    }


def _recipe_fixture_replay_demo() -> dict:
    replay = _run_repo_python(FIXTURE_REPLAY, ["--replay", "--json"], timeout=60)
    if replay is None:
        return {
            "summary": "Fixture replay wrapper unavailable; reported gracefully, nothing run.",
            "what_happened": "Ghoti looked for the claude-swarm fixture replay wrapper but "
                             "could not run it. Nothing was launched and nothing failed "
                             "dangerously - this is a graceful unavailable result.",
            "did": ["Checked for the fixture replay wrapper (not runnable here)."],
            "extra": "Fixture replay was unavailable. No agents, no provider, no external CLI.",
            "warnings": ["fixture replay wrapper unavailable"], "errors": [],
            "next_actions": ["Verify 03_scripts/claude_swarm_fixture exists, then rerun."],
            "details": {"available": False},
        }
    plan = replay.get("plan_summary", {}) or {}
    tasks = plan.get("task_count", 0)
    groups = plan.get("parallel_groups", []) or []
    overlaps = plan.get("overlap_count", 0)
    extra = "\n".join([
        "### Fixture replay result", "",
        "| Metric | Value |", "|--------|-------|",
        "| Tasks | %s |" % tasks,
        "| Parallel groups | %s |" % len(groups),
        "| Overlaps | %s |" % overlaps,
        "| Simulation | %s |" % replay.get("simulation"),
        "| Live execution | %s |" % replay.get("live_execution"),
        "", "### Why this proves safe supervised planning", "",
        "- The replay computed a real multi-task parallel plan (%s tasks in %s groups "
        "with %s file overlaps) using only a local fixture file." % (tasks, len(groups), overlaps),
        "- No external CLI was executed, no provider or API key was used, and no agent "
        "was launched - the same planning logic that would drive a live swarm ran in a "
        "fully supervised, repo-local simulation.",
        "- This is the safety model in action: prove the plan first, execute only after "
        "explicit human approval (which remains disabled).",
    ])
    return {
        "summary": "Fixture replay demo: %s tasks / %s parallel groups / %s overlaps, "
                   "simulation only, nothing launched." % (tasks, len(groups), overlaps),
        "what_happened": "Ghoti replayed the claude-swarm fixture plan locally: a real "
                         "scheduling computation over a checked-in fixture, with no agents, "
                         "no provider, and no external CLI.",
        "did": [
            "Ran the repo-local fixture replay wrapper with fixed argv.",
            "Validated plan: %s tasks, %s parallel groups, %s overlaps." % (tasks, len(groups), overlaps),
        ],
        "extra": extra, "warnings": [], "errors": [],
        "next_actions": [
            "Open the generated report to see the plan table.",
            "Use this replay as the investor-facing proof of supervised planning.",
        ],
        "details": {"available": True, "task_count": tasks,
                    "parallel_group_count": len(groups), "overlap_count": overlaps},
    }


RECIPES: dict[str, dict] = {
    "project-health": {
        "title": "Project Health Report",
        "description": "Full local snapshot: git truth, launcher status, security audit, "
                       "Rust status, PR queue, dashboard reachability.",
        "why": "One honest answer to 'where is the project right now?'.",
        "wont_do": "No pushes, no merges, no network beyond localhost probes.",
        "capabilities": ["repo_read", "status_read", "report_write_repo_local"],
        "runner": _recipe_project_health,
        "report_prefix": "project_health",
    },
    "handoff-pack": {
        "title": "Handoff Pack",
        "description": "Copy-paste packets for the implementation lane, the audit lane, "
                       "and the local Hermes/Ollama status lane.",
        "why": "Hand work between lanes without retyping context.",
        "wont_do": "No provider calls; packets are text you paste manually.",
        "capabilities": ["repo_read", "status_read", "plan_render", "report_write_repo_local"],
        "runner": _recipe_handoff_pack,
        "report_prefix": "handoff_pack",
    },
    "cleanup-preview": {
        "title": "Cleanup Preview",
        "description": "Read-only inspection: untracked/modified files, large files, "
                       "worktrees, cache folders, old logs.",
        "why": "See what could be cleaned without risking anything.",
        "wont_do": "Never deletes, never moves - strictly a preview.",
        "capabilities": ["repo_read", "report_write_repo_local"],
        "runner": _recipe_cleanup_preview,
        "report_prefix": "repo_cleanup_preview",
    },
    "local-model-check": {
        "title": "Local Model Readiness",
        "description": "Checks the ollama command, the localhost endpoint, and the "
                       "llama3.1:8b / gemma3:4b models.",
        "why": "Know whether the cheap local model lane is ready.",
        "wont_do": "Never pulls models, never calls cloud providers.",
        "capabilities": ["status_read", "local_model_status_read", "report_write_repo_local"],
        "runner": _recipe_local_model_check,
        "report_prefix": "local_model_readiness",
    },
    "fixture-replay-demo": {
        "title": "Fixture Replay Demo",
        "description": "Replays the claude-swarm fixture plan: real parallel scheduling, "
                       "simulation only.",
        "why": "Proves supervised planning works without launching anything.",
        "wont_do": "No agents, no provider, no external CLI.",
        "capabilities": ["fixture_read", "repo_read", "plan_render", "report_write_repo_local"],
        "runner": _recipe_fixture_replay_demo,
        "report_prefix": "fixture_replay_demo",
    },
}

ALL_SAFE_ORDER = ["project-health", "handoff-pack", "cleanup-preview",
                  "local-model-check", "fixture-replay-demo"]


def _safety_flags() -> dict:
    return {
        "no_live_actions": True,
        "provider_api_used": False,
        "agents_launched": False,
        "files_deleted": False,
        "files_moved": False,
        "external_agent_cli_executed": False,
        "accounts_touched": False,
        "localhost_only_network": True,
        "writes_repo_local_generated_only": True,
    }


def run_recipe(recipe_id: str, output_dir: Path | None, dry_run: bool, apply: bool) -> dict:
    if recipe_id not in RECIPES:
        return {"ok": False, "recipe_id": recipe_id, "mode": "error", "dry_run": dry_run,
                "report_path": None, "summary": "Unknown recipe.",
                "safety_flags": _safety_flags(), "actions_taken": [],
                "actions_blocked": [], "next_actions": ["Run --list to see valid recipes."],
                "errors": ["unknown recipe id: %s" % recipe_id], "warnings": []}

    spec = RECIPES[recipe_id]
    policy = check_recipe_policy(recipe_id, spec["capabilities"])
    if not policy["policy_check_passed"]:
        return {"ok": False, "recipe_id": recipe_id, "mode": "policy_denied",
                "dry_run": dry_run, "report_path": None,
                "summary": "Policy check denied this recipe (deny-by-default).",
                "safety_flags": _safety_flags(), "policy": policy,
                "actions_taken": ["Ran deny-by-default policy check."],
                "actions_blocked": ["Recipe execution (policy denied: %s)"
                                    % ", ".join(policy["denied_capabilities"])],
                "next_actions": ["Review 23_configs/operator_recipe_policy.example.json."],
                "errors": ["policy denied"], "warnings": []}

    result = spec["runner"]()

    target_dir = output_dir if output_dir is not None else DEFAULT_OUTPUT_DIR
    outside_repo = not _is_under_repo(target_dir)
    actions_blocked = list(STANDARD_REFUSALS)
    warnings = list(result["warnings"])
    report_path: str | None = None
    mode = "safe_local"

    report_name = "%s_%s.md" % (spec["report_prefix"], _timestamp())
    report_md = _render_report(
        title="Ghoti Recipe Report - %s" % spec["title"],
        what_happened=result["what_happened"],
        did=result["did"],
        refused=STANDARD_REFUSALS,
        created=["This report (%s)." % report_name],
        next_actions=result["next_actions"],
        body_extra=result["extra"],
    )

    if outside_repo:
        # No allowlisted external paths exist yet, so outside-repo output is
        # always preview-only in this milestone (even with --apply).
        mode = "preview_only"
        actions_blocked.append(
            "Writing report to %s (outside the repo; preview-only, no allowlisted "
            "external paths exist%s)." % (target_dir, "; --apply was set" if apply else ""))
        warnings.append("Output directory is outside the repo: report returned in JSON "
                        "only, nothing written.")
    else:
        target_dir.mkdir(parents=True, exist_ok=True)
        report_file = target_dir / report_name
        report_file.write_text(report_md, encoding="utf-8")
        report_path = str(report_file)

    actions_taken = ["Ran policy check (%s, passed)." % policy["checker"]] + result["did"]
    if report_path:
        actions_taken.append("Wrote Markdown report to %s." % report_path)

    return {
        "ok": not result["errors"],
        "recipe_id": recipe_id,
        "mode": mode,
        "dry_run": dry_run,
        "report_path": report_path,
        "summary": result["summary"],
        "safety_flags": _safety_flags(),
        "policy": policy,
        "actions_taken": actions_taken,
        "actions_blocked": actions_blocked,
        "next_actions": result["next_actions"],
        "errors": result["errors"],
        "warnings": warnings,
        "details": result["details"],
        "report_preview": report_md if outside_repo else None,
    }


def run_all_safe(output_dir: Path | None, dry_run: bool, apply: bool) -> dict:
    results = [run_recipe(rid, output_dir, dry_run, apply) for rid in ALL_SAFE_ORDER]
    all_ok = all(r["ok"] for r in results)
    target_dir = output_dir if output_dir is not None else DEFAULT_OUTPUT_DIR
    report_path: str | None = None
    summary_lines = ["# Ghoti Recipe Report - All Safe Recipes", "",
                     "Generated: " + datetime.now(timezone.utc).isoformat(), "",
                     "## What happened", "",
                     "Ghoti ran all %d safe recipes in sequence. Every run was local, "
                     "supervised, and policy-checked." % len(results), "",
                     "## Results", ""]
    for r in results:
        summary_lines.append("- **%s**: %s (%s)" % (
            r["recipe_id"], "ok" if r["ok"] else "error", r["summary"]))
        if r["report_path"]:
            summary_lines.append("  - report: %s" % r["report_path"])
    summary_lines += ["", "## What the user can do next", "",
                      "- Next action: open the individual reports listed above.", "",
                      "## What remains disabled", "", WHAT_REMAINS_DISABLED, ""]
    if _is_under_repo(target_dir):
        target_dir.mkdir(parents=True, exist_ok=True)
        report_file = target_dir / ("all_safe_summary_%s.md" % _timestamp())
        report_file.write_text("\n".join(summary_lines), encoding="utf-8")
        report_path = str(report_file)
    return {
        "ok": all_ok,
        "recipe_id": "all-safe",
        "mode": "safe_local" if report_path else "preview_only",
        "dry_run": dry_run,
        "report_path": report_path,
        "summary": "%d/%d safe recipes ok." % (sum(1 for r in results if r["ok"]), len(results)),
        "safety_flags": _safety_flags(),
        "actions_taken": ["Ran %d safe recipes in sequence." % len(results)],
        "actions_blocked": list(STANDARD_REFUSALS),
        "next_actions": ["Open the generated reports under the output folder."],
        "errors": [e for r in results for e in r["errors"]],
        "warnings": [w for r in results for w in r["warnings"]],
        "results": results,
    }


def list_recipes() -> dict:
    return {
        "ok": True,
        "count": len(RECIPES),
        "recipes": [
            {"id": rid, "title": spec["title"], "description": spec["description"],
             "why": spec["why"], "wont_do": spec["wont_do"],
             "capabilities": spec["capabilities"]}
            for rid, spec in RECIPES.items()
        ],
        "all_safe_order": ALL_SAFE_ORDER,
        "default_output_dir": str(DEFAULT_OUTPUT_DIR),
        "safety_flags": _safety_flags(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ghoti operator recipes: safe local supervised workflows.")
    parser.add_argument("--list", action="store_true", help="List available recipes")
    parser.add_argument("--run", metavar="RECIPE",
                        help="Run a recipe id, or 'all-safe' for every safe recipe")
    parser.add_argument("--output-dir", metavar="PATH", default=None,
                        help="Report output dir (repo-local by default; outside-repo "
                             "paths are preview-only)")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Dry-run mode (default true; recipes are read-only plus "
                             "repo-local report writes either way)")
    parser.add_argument("--apply", action="store_true",
                        help="Reserved for future allowlisted output paths; never "
                             "enables destructive operations")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Emit JSON")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir).expanduser() if args.output_dir else None

    if args.list:
        payload = list_recipes()
    elif args.run == "all-safe":
        payload = run_all_safe(output_dir, args.dry_run, args.apply)
    elif args.run:
        payload = run_recipe(args.run, output_dir, args.dry_run, args.apply)
    else:
        parser.print_help()
        return 2

    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        if args.list:
            print("Ghoti operator recipes (%d):" % payload["count"])
            for recipe in payload["recipes"]:
                print("  %-22s %s" % (recipe["id"], recipe["title"]))
                print("  %-22s %s" % ("", recipe["description"]))
            print("Run one: python 03_scripts/operator_recipes/ghoti_operator_recipes.py "
                  "--run <id> --json")
        else:
            print("recipe: %s" % payload["recipe_id"])
            print("ok: %s" % payload["ok"])
            print("summary: %s" % payload["summary"])
            if payload.get("report_path"):
                print("report: %s" % payload["report_path"])
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
