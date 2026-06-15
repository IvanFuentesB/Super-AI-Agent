"""Ghoti acceleration tool stack - one CLI to check/install-safe/template/intake.

Composes the helper modules: detection (check_tool_stack), safe install planning
(install_safe_tools), MCP templates (mcp_config_writer), skills registry
(skills_config_writer), and repo intake (repo_intake). Everything is local and
safe: default dry-run, no secrets, no unknown-repo execution, no live accounts.

Usage:
  python 03_scripts/tool_stack/ghoti_tool_stack.py --status --json
  python 03_scripts/tool_stack/ghoti_tool_stack.py --check --json
  python 03_scripts/tool_stack/ghoti_tool_stack.py --install-safe --dry-run --json
  python 03_scripts/tool_stack/ghoti_tool_stack.py --install-safe --apply --json
  python 03_scripts/tool_stack/ghoti_tool_stack.py --write-mcp-templates --json
  python 03_scripts/tool_stack/ghoti_tool_stack.py --write-skills-templates --json
  python 03_scripts/tool_stack/ghoti_tool_stack.py --repo-intake [REPO] --dry-run --json
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import check_tool_stack  # noqa: E402
import install_safe_tools  # noqa: E402
import mcp_config_writer  # noqa: E402
import skills_config_writer  # noqa: E402
import repo_intake  # noqa: E402

import subprocess  # noqa: E402

REPO_ROOT = SCRIPT_DIR.parents[1]
REGISTRY = REPO_ROOT / "14_context" / "tool_intake" / "tool_registry.json"
RUST_GUARD_CANDIDATES = [
    REPO_ROOT / "rust" / "target" / "release" / "tool_stack_guard.exe",
    REPO_ROOT / "rust" / "target" / "release" / "tool_stack_guard",
    REPO_ROOT / "rust" / "target" / "debug" / "tool_stack_guard.exe",
    REPO_ROOT / "rust" / "target" / "debug" / "tool_stack_guard",
]
RUST_MANIFEST = REPO_ROOT / "rust" / "Cargo.toml"
TEMPLATE_DIR = REPO_ROOT / "14_context" / "mcp_connectors" / "config_templates"
SKILLS_REGISTRY = REPO_ROOT / "14_context" / "tool_stack" / "skills_registry.json"
STATUS_MD = REPO_ROOT / "14_context" / "operator_reports" / "generated" / "acceleration_stack_status.md"
STATUS_JSON = REPO_ROOT / "14_context" / "operator_reports" / "generated" / "acceleration_stack_status.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_registry() -> dict:
    try:
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    except Exception:
        return {"tools": []}


def _run_rust_guard() -> dict:
    """Invoke the Rust tool_stack_guard if built; else report unavailable.

    Returns {status: available|missing|failed, ...}. Prefers a prebuilt binary;
    falls back to `cargo run` (offline) only if cargo is present. Never installs.
    """
    args = ["--check", "--json"]
    binary = next((c for c in RUST_GUARD_CANDIDATES if c.is_file()), None)
    cmd = None
    if binary is not None:
        cmd = [str(binary), *args]
    elif shutil.which("cargo") and RUST_MANIFEST.is_file():
        cmd = [shutil.which("cargo"), "run", "--quiet", "--offline", "--manifest-path",
               str(RUST_MANIFEST), "--bin", "tool_stack_guard", "--", *args]
    if cmd is None:
        return {"status": "missing",
                "message": "Rust tool_stack_guard not built. Build with: "
                           "cargo build --release --manifest-path rust/Cargo.toml "
                           "--bin tool_stack_guard"}
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT),
                              timeout=120, shell=False)
        report = json.loads(proc.stdout)
        return {"status": "available" if report.get("ok") else "failed",
                "blocker_count": report.get("blocker_count", 0),
                "finding_count": report.get("finding_count", 0),
                "fingerprints": report.get("fingerprints", {}),
                "used_binary": binary is not None}
    except Exception as error:
        return {"status": "failed", "message": str(error)[:200]}


def cmd_check() -> dict:
    payload = check_tool_stack.check_local_basics()
    payload["action"] = "check"
    rust = _run_rust_guard()
    payload["rust_tool_stack_guard"] = rust["status"]
    payload["rust_guard_detail"] = rust
    # The Rust validator's verdict gates overall check ok-ness when it ran.
    if rust["status"] == "failed":
        payload["ok"] = False
    payload["generated_at"] = _now()
    return payload


def cmd_install_safe(apply: bool) -> dict:
    payload = install_safe_tools.plan(apply=apply)
    install_safe_tools.write_installed_snapshot()
    payload["generated_at"] = _now()
    return payload


def cmd_write_mcp_templates() -> dict:
    payload = mcp_config_writer.write_templates()
    payload["generated_at"] = _now()
    return payload


def cmd_write_skills_templates() -> dict:
    payload = skills_config_writer.write_registry()
    payload["generated_at"] = _now()
    return payload


def cmd_repo_intake(repo: str | None, apply: bool) -> dict:
    if not repo:
        return {"ok": True, "action": "repo-intake", "mode": "apply" if apply else "dry-run",
                "cloned": False, "executed_anything": False,
                "message": "No repo given. Dry-run never clones; pass a repo url/name and "
                           "--apply to shallow-clone into the gitignored sandbox for inspection.",
                "generated_at": _now()}
    payload = repo_intake.intake(repo, apply=apply)
    payload["generated_at"] = _now()
    return payload


def _registry_counts(reg: dict) -> dict:
    tools = reg.get("tools", [])
    by_priority = {}
    for t in tools:
        by_priority[t.get("priority", "?")] = by_priority.get(t.get("priority", "?"), 0) + 1
    return {
        "total": len(tools),
        "P0": by_priority.get("P0", 0), "P1": by_priority.get("P1", 0),
        "P2": by_priority.get("P2", 0), "defer": by_priority.get("defer", 0),
        "reject": by_priority.get("reject", 0),
        "source_needed": sum(1 for t in tools if t.get("source_needed")),
    }


def cmd_status(write: bool = True) -> dict:
    detected = check_tool_stack.check_local_basics()
    reg = _load_registry()
    counts = _registry_counts(reg)
    mcp_ready = len(list(TEMPLATE_DIR.glob("*.template.json"))) if TEMPLATE_DIR.is_dir() else 0
    skills_ready = 0
    if SKILLS_REGISTRY.is_file():
        try:
            skills_ready = json.loads(SKILLS_REGISTRY.read_text(encoding="utf-8")).get("skill_count", 0)
        except Exception:
            skills_ready = 0
    manual_required = sum(1 for t in reg.get("tools", [])
                          if t.get("status") in ("needs_source", "candidate")
                          or t.get("source_needed"))
    payload = {
        "ok": True,
        "action": "status",
        "product": "Ghoti Acceleration Tool Stack",
        "installed_safe_tools": detected["present"],
        "installed_count": detected["present_count"],
        "missing_tools": detected["missing"],
        "missing_count": detected["missing_count"],
        "mcp_templates_ready": mcp_ready,
        "skills_registered": skills_ready,
        "registry_total": counts["total"],
        "priority_counts": {k: counts[k] for k in ("P0", "P1", "P2", "defer", "reject")},
        "source_needed_count": counts["source_needed"],
        "manual_setup_required_count": manual_required,
        "blocked_rejected_count": counts["reject"],
        "repo_intake_queue_count": _intake_queue_count(),
        "rust_tool_stack_guard": _run_rust_guard()["status"],
        "safety": {"secrets_in_repo": False, "live_account_actions": False,
                   "all_mcp_templates_disabled": True, "network_used": False},
        "generated_at": _now(),
    }
    if write:
        _write_status(payload)
    return payload


def _intake_queue_count() -> int:
    reg = _load_registry()
    return sum(1 for t in reg.get("tools", [])
               if t.get("implementation_type") == "inspect_first")


def _write_status(payload: dict) -> None:
    STATUS_JSON.parent.mkdir(parents=True, exist_ok=True)
    STATUS_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Ghoti Acceleration Stack - Status", "",
        "Generated: %s" % payload["generated_at"], "",
        "- Installed safe tools (%d): %s" % (payload["installed_count"],
                                             ", ".join(payload["installed_safe_tools"])),
        "- Missing (%d): %s" % (payload["missing_count"], ", ".join(payload["missing_tools"]) or "none"),
        "- MCP templates ready: %d (all disabled)" % payload["mcp_templates_ready"],
        "- Skills registered: %d" % payload["skills_registered"],
        "- Registry total: %d" % payload["registry_total"],
        "- Priorities: P0=%d P1=%d P2=%d defer=%d reject=%d" % (
            payload["priority_counts"]["P0"], payload["priority_counts"]["P1"],
            payload["priority_counts"]["P2"], payload["priority_counts"]["defer"],
            payload["priority_counts"]["reject"]),
        "- Manual setup required: %d" % payload["manual_setup_required_count"],
        "- Repo intake queue (inspect_first): %d" % payload["repo_intake_queue_count"],
        "", "Safety: no secrets, no live account actions, all MCP templates disabled.", "",
    ]
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ghoti acceleration tool stack CLI.")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--install-safe", action="store_true")
    parser.add_argument("--write-mcp-templates", action="store_true")
    parser.add_argument("--write-skills-templates", action="store_true")
    parser.add_argument("--repo-intake", nargs="?", const="", metavar="REPO")
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--apply", action="store_true", default=False)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if args.check:
        payload = cmd_check()
    elif args.install_safe:
        payload = cmd_install_safe(apply=args.apply)
    elif args.write_mcp_templates:
        payload = cmd_write_mcp_templates()
    elif args.write_skills_templates:
        payload = cmd_write_skills_templates()
    elif args.repo_intake is not None:
        payload = cmd_repo_intake(args.repo_intake or None, apply=args.apply)
    elif args.status:
        payload = cmd_status()
    else:
        parser.print_help()
        return 2

    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        print("Ghoti tool stack - %s: ok=%s" % (payload.get("action"), payload.get("ok")))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
