#!/usr/bin/env python3
"""External Tool Sandbox Manager (N+4.8A).

Safely pulls APPROVED public repos into a local sandbox, statically inspects
them, and generates Ghoti-local adapter stubs + approval packets.

SAFETY MODEL — this manager only ever:
  - clones approved-catalog repos with `git clone --depth 1`
  - runs `git rev-parse HEAD` inside a cloned repo
  - lists and READS files (README / package files / docs / LICENSE)
  - writes Ghoti-local adapter stubs, approval packets, and a status file

It NEVER: installs dependencies (npm/pnpm/pip), runs external repo code or
scripts, starts UI-TARS, calls external APIs, performs desktop control, or
performs any live account / posting / money action. Real runtime wiring of any
external tool always requires explicit human approval.
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
SANDBOX_DIR = REPO_ROOT / "21_repos" / "third_party" / "sandboxed"
ADAPTERS_DIR = REPO_ROOT / "02_automation" / "external_tool_adapters"
EXTERNAL_TOOLS_DIR = REPO_ROOT / "14_context" / "external_tools"
STATUS_FILE = EXTERNAL_TOOLS_DIR / "external_tool_sandbox_status.json"
APPROVAL_PACKETS_DIR = EXTERNAL_TOOLS_DIR / "approval_packets"

MANAGER_VERSION = "1.0.0"
MILESTONE = "N+4.8A"
CLONE_TIMEOUT_SECONDS = 240

# The APPROVED catalog is the ONLY set of repos this manager will ever clone.
# Any other slug is rejected.
APPROVED_CATALOG = [
    {
        "slug": "bytedance/UI-TARS-desktop",
        "key": "ui_tars_desktop",
        "name": "UI-TARS Desktop",
        "url": "https://github.com/bytedance/UI-TARS-desktop.git",
        "adapter": "ui_tars_desktop_adapter.py",
        "purpose": "Desktop GUI agent — screenshot capture and click/type control of the local computer.",
        "capabilities": [
            "desktop GUI automation (screenshot + click/type)",
            "visual grounding of on-screen UI elements",
            "task execution against the local desktop",
        ],
        "desktop_control_expected": True,
    },
    {
        "slug": "bytedance/UI-TARS",
        "key": "ui_tars_model",
        "name": "UI-TARS Model",
        "url": "https://github.com/bytedance/UI-TARS.git",
        "adapter": "ui_tars_model_adapter.py",
        "purpose": "UI-TARS vision-language GUI agent model and inference assets.",
        "capabilities": [
            "vision-language understanding of GUI screenshots",
            "next-action prediction from screen state",
            "model served locally or via an inference endpoint",
        ],
        "desktop_control_expected": True,
    },
    {
        "slug": "the-agency-ai/the-agency",
        "key": "the_agency",
        "name": "TheAgency",
        "url": "https://github.com/the-agency-ai/the-agency.git",
        "adapter": "the_agency_adapter.py",
        "purpose": "Multi-agent orchestration framework.",
        "capabilities": [
            "multi-agent orchestration and role routing",
            "task decomposition across agents",
        ],
        "desktop_control_expected": False,
    },
    {
        "slug": "darkrishabh/agent-skills-eval",
        "key": "agent_skills_eval",
        "name": "agent-skills-eval",
        "url": "https://github.com/darkrishabh/agent-skills-eval.git",
        "adapter": "agent_skills_eval_adapter.py",
        "purpose": "Agent skill benchmarking and evaluation harness.",
        "capabilities": [
            "agent skill benchmark suite",
            "evaluation harness for agent capabilities",
        ],
        "desktop_control_expected": False,
    },
    {
        "slug": "vouch-protocol/vouch",
        "key": "vouch",
        "name": "Vouch Protocol",
        "url": "https://github.com/vouch-protocol/vouch.git",
        "adapter": "vouch_adapter.py",
        "purpose": "Agent identity / attestation / vouching protocol.",
        "capabilities": [
            "agent identity and attestation",
            "trust / vouching protocol primitives",
        ],
        "desktop_control_expected": False,
    },
]

# Static-scan keyword sets (detection only — nothing is executed).
_INSTALL_MARKERS = {
    "npm": ["package.json"],
    "pnpm": ["pnpm-lock.yaml"],
    "yarn": ["yarn.lock"],
    "pip": ["requirements.txt", "pyproject.toml", "setup.py", "setup.cfg"],
    "cargo": ["Cargo.toml"],
    "go": ["go.mod"],
}
_API_KEY_TOKENS = [
    "api_key", "apikey", "api-key", "openai", "anthropic", "gemini",
    "access_token", "secret_key", "bearer", "huggingface", "hf_token",
]
_DESKTOP_CONTROL_TOKENS = [
    "screenshot", "pyautogui", "robotjs", "nut-tree", "nut.js", "screen capture",
    "click(", "keypress", "mouse", "keyboard control", "desktop control", "xdotool",
]
_LIVE_ACCOUNT_TOKENS = [
    "oauth", "login(", "sign in", "post to", "upload to", "tweet",
    "publish", "account credentials", "stripe", "payment",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _is_repo_local(target) -> bool:
    try:
        resolved = Path(str(target)).resolve()
        repo = REPO_ROOT.resolve()
        return resolved == repo or repo in resolved.parents
    except Exception:
        return False


def _repo_rel(target) -> str:
    try:
        return str(Path(target).resolve().relative_to(REPO_ROOT.resolve())).replace(os.sep, "/")
    except Exception:
        return str(target)


def _catalog_for(slug_or_key: str):
    for entry in APPROVED_CATALOG:
        if slug_or_key in (entry["slug"], entry["key"]):
            return entry
    return None


def _read_status() -> dict:
    try:
        if STATUS_FILE.exists():
            return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _write_status(state: dict) -> None:
    if not _is_repo_local(STATUS_FILE):
        raise ValueError("status file path is outside the repo root")
    EXTERNAL_TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _ensure_sandbox_gitignore() -> None:
    """Make sure cloned external repos can never be committed to Ghoti."""
    if not _is_repo_local(SANDBOX_DIR):
        raise ValueError("sandbox dir is outside the repo root")
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    gitignore = SANDBOX_DIR / ".gitignore"
    content = (
        "# N+4.8A external tool sandbox.\n"
        "# Cloned external repos are sandbox working data and are NEVER committed.\n"
        "*\n"
        "!.gitignore\n"
    )
    if not gitignore.exists() or gitignore.read_text(encoding="utf-8") != content:
        gitignore.write_text(content, encoding="utf-8")


def _git(args, cwd=None, timeout=CLONE_TIMEOUT_SECONDS):
    """Run a fixed-argv git command. shell=False. Never a shell string."""
    return subprocess.run(
        ["git"] + list(args),
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=False,
    )


def _clone_repo(entry: dict) -> dict:
    """Shallow-clone one approved repo. Returns a clone-result dict.

    Never installs, never runs repo code. A repo is considered cloned only
    when a `.ghoti_clone_complete` marker is present (written after a fully
    successful clone+checkout). A stale/partial clone without the marker is
    cleared and re-attempted. `core.longpaths=true` lets the checkout handle
    Windows MAX_PATH for deeply-nested repos.
    """
    dest = SANDBOX_DIR / entry["key"]
    marker = dest / ".ghoti_clone_complete"
    result = {
        "clone_status": "not_attempted",
        "clone_error": None,
        "commit": None,
        "clone_path": None,
    }
    try:
        if marker.exists() and (dest / ".git").exists():
            # Already fully cloned — reuse, just record the commit.
            rev = _git(["rev-parse", "HEAD"], cwd=dest, timeout=30)
            result["clone_status"] = "cloned"
            result["commit"] = rev.stdout.strip() if rev.returncode == 0 else None
            result["clone_path"] = _repo_rel(dest)
            return result
        # A directory without a completion marker is a stale/partial clone.
        # Report it truthfully — never force-remove external content here.
        if dest.exists():
            result["clone_status"] = "failed"
            result["clone_error"] = (
                "stale/partial clone at %s without a completion marker; "
                "manual cleanup required before re-sync" % _repo_rel(dest)
            )
            return result
        # Fresh shallow clone of an approved URL only. `-c core.longpaths=true`
        # handles Windows MAX_PATH at checkout. shell=False, fixed argv.
        proc = _git(
            ["-c", "core.longpaths=true", "clone", "--depth", "1", entry["url"], str(dest)],
            timeout=CLONE_TIMEOUT_SECONDS,
        )
        if proc.returncode != 0:
            result["clone_status"] = "failed"
            result["clone_error"] = (proc.stderr or "git clone failed").strip()[:500]
            return result
        rev = _git(["rev-parse", "HEAD"], cwd=dest, timeout=30)
        result["clone_status"] = "cloned"
        result["commit"] = rev.stdout.strip() if rev.returncode == 0 else None
        result["clone_path"] = _repo_rel(dest)
        try:
            marker.write_text("clone complete %s\n" % _now(), encoding="utf-8")
        except Exception:
            pass
    except subprocess.TimeoutExpired:
        result["clone_status"] = "failed"
        result["clone_error"] = "clone timed out after %d seconds" % CLONE_TIMEOUT_SECONDS
    except FileNotFoundError:
        result["clone_status"] = "failed"
        result["clone_error"] = "git executable not found"
    except Exception as exc:
        result["clone_status"] = "failed"
        result["clone_error"] = "clone error: %s" % exc
    return result


def _read_text_safe(path: Path, limit: int = 60000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def _scan_repo(entry: dict, dest: Path) -> dict:
    """Static capability scan of a cloned repo. Reads files only — never runs."""
    scan = {
        "scanned": False,
        "ecosystems": [],
        "install_requirements": [],
        "install_performed": False,
        "api_key_required": False,
        "api_key_evidence": [],
        "desktop_control_risk": False,
        "live_account_risk": False,
        "license": None,
        "readme_present": False,
        "top_level_entries": [],
    }
    if not (dest / ".ghoti_clone_complete").exists() or not (dest / ".git").exists():
        scan["note"] = "repo not fully cloned — scan skipped"
        return scan

    try:
        entries = sorted(p.name for p in dest.iterdir())
    except Exception:
        entries = []
    scan["top_level_entries"] = entries[:60]
    scan["scanned"] = True

    lower_entries = {e.lower() for e in entries}
    # Ecosystem + install requirements (detected, never executed).
    for tool, markers in _INSTALL_MARKERS.items():
        if any(m.lower() in lower_entries for m in markers):
            scan["install_requirements"].append(tool)
    if "package.json" in lower_entries:
        scan["ecosystems"].append("node/javascript-typescript")
    if any(m in lower_entries for m in ("pyproject.toml", "setup.py", "requirements.txt", "setup.cfg")):
        scan["ecosystems"].append("python")
    if "cargo.toml" in lower_entries:
        scan["ecosystems"].append("rust")
    if "go.mod" in lower_entries:
        scan["ecosystems"].append("go")

    # License.
    for name in entries:
        if name.lower().startswith("license"):
            text = _read_text_safe(dest / name, limit=400)
            first = next((ln.strip() for ln in text.splitlines() if ln.strip()), None)
            scan["license"] = first
            break

    # Bounded read of doc / config files for static keyword detection.
    scan_targets = []
    for name in entries:
        low = name.lower()
        if low.startswith("readme"):
            scan["readme_present"] = True
            scan_targets.append(dest / name)
        elif low in ("package.json", "pyproject.toml", "requirements.txt",
                     ".env.example", "env.example", ".env.sample"):
            scan_targets.append(dest / name)
    docs_dir = dest / "docs"
    if docs_dir.is_dir():
        try:
            for doc in sorted(docs_dir.iterdir())[:8]:
                if doc.is_file():
                    scan_targets.append(doc)
        except Exception:
            pass

    blob = ""
    for target in scan_targets[:20]:
        blob += "\n" + _read_text_safe(target)
    low_blob = blob.lower()

    for token in _API_KEY_TOKENS:
        if token in low_blob:
            scan["api_key_required"] = True
            scan["api_key_evidence"].append(token)
    for token in _DESKTOP_CONTROL_TOKENS:
        if token in low_blob:
            scan["desktop_control_risk"] = True
            break
    for token in _LIVE_ACCOUNT_TOKENS:
        if token in low_blob:
            scan["live_account_risk"] = True
            break
    # The catalog already knows which tools are desktop-control tools.
    if entry.get("desktop_control_expected"):
        scan["desktop_control_risk"] = True

    return scan


# ---------------------------------------------------------------------------
# Adapter stub generation
# ---------------------------------------------------------------------------

def _adapter_source(entry: dict) -> str:
    caps = entry["capabilities"]
    caps_py = ",\n        ".join(json.dumps(c) for c in caps)
    return '''#!/usr/bin/env python3
"""%(name)s adapter stub (N+4.8A) — SAFE STUB ONLY.

Ghoti-local adapter stub for %(name)s (%(slug)s).

This stub does NOT import or run any external repo code, does NOT execute
desktop actions, and does NOT call any external API. It only describes the
tool and the safety gates that must pass before any real runtime wiring.
Real runtime wiring requires explicit human approval.
"""

TOOL_KEY = %(key)r
TOOL_NAME = %(name)r
TOOL_SLUG = %(slug)r
REQUIRES_HUMAN_APPROVAL = True


def status() -> dict:
    """Adapter status. The adapter is a stub: not wired, local-only."""
    return {
        "tool": TOOL_NAME,
        "tool_key": TOOL_KEY,
        "slug": TOOL_SLUG,
        "adapter_kind": "safe_stub",
        "wired": False,
        "runtime_wiring": "not_wired",
        "local_only": True,
        "external_code_imported": False,
        "external_code_executed": False,
        "desktop_control_enabled": False,
        "live_api_enabled": False,
        "requires_human_approval": REQUIRES_HUMAN_APPROVAL,
    }


def capabilities() -> list:
    """Capabilities the tool WOULD provide once approved and wired."""
    return [
        %(caps)s,
    ]


def safety_gates() -> list:
    """Gates that must all pass, with human approval, before wiring."""
    return [
        "human_approval_required",
        "sandbox_static_scan_reviewed",
        "no_external_code_execution",
        "no_dependency_install_without_approval",
        "no_desktop_control_without_approval",
        "no_live_api_calls_without_approval",
        "no_live_account_actions",
    ]


if __name__ == "__main__":
    import json
    print(json.dumps({
        "status": status(),
        "capabilities": capabilities(),
        "safety_gates": safety_gates(),
    }, indent=2))
''' % {
        "name": entry["name"],
        "slug": entry["slug"],
        "key": entry["key"],
        "caps": caps_py,
    }


def cmd_generate_adapters() -> dict:
    if not _is_repo_local(ADAPTERS_DIR):
        return {"ok": False, "error": "adapters dir is outside the repo root", "generated_at": _now()}
    ADAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for entry in APPROVED_CATALOG:
        path = ADAPTERS_DIR / entry["adapter"]
        # A promoted adapter (N+4.9A+) is an execution-capable Ghoti adapter,
        # not a stub — never regenerate it back into a stub.
        promoted = False
        if path.exists():
            try:
                promoted = "ADAPTER_PROMOTED = True" in path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                promoted = False
        if promoted:
            written.append({
                "tool": entry["name"],
                "adapter": entry["adapter"],
                "path": _repo_rel(path),
                "exists": True,
                "promoted": True,
                "regenerated": False,
            })
            continue
        path.write_text(_adapter_source(entry), encoding="utf-8")
        written.append({
            "tool": entry["name"],
            "adapter": entry["adapter"],
            "path": _repo_rel(path),
            "exists": path.exists(),
            "promoted": False,
            "regenerated": True,
        })
    # A small package marker so the adapters import cleanly as a group.
    init_path = ADAPTERS_DIR / "__init__.py"
    if not init_path.exists():
        init_path.write_text(
            '"""Ghoti external tool adapter stubs (N+4.8A). Safe stubs only."""\n',
            encoding="utf-8",
        )
    return {
        "ok": True,
        "action": "generate-adapters",
        "adapters_dir": _repo_rel(ADAPTERS_DIR),
        "adapters": written,
        "count": len(written),
        "generated_at": _now(),
    }


# ---------------------------------------------------------------------------
# Commands: sync / scan / status / approval packet
# ---------------------------------------------------------------------------

def _build_repo_records(repo_filter=None) -> list:
    prior = {r.get("key"): r for r in _read_status().get("repos", [])}
    records = []
    for entry in APPROVED_CATALOG:
        if repo_filter and entry["slug"] != repo_filter and entry["key"] != repo_filter:
            # Keep the prior record untouched for non-targeted repos.
            if entry["key"] in prior:
                records.append(prior[entry["key"]])
            continue
        records.append(dict(prior.get(entry["key"], {}), **{
            "slug": entry["slug"],
            "key": entry["key"],
            "name": entry["name"],
            "purpose": entry["purpose"],
        }))
    return records


def cmd_sync_approved(repo_filter=None) -> dict:
    _ensure_sandbox_gitignore()
    repos = []
    prior = {r.get("key"): r for r in _read_status().get("repos", [])}
    for entry in APPROVED_CATALOG:
        if repo_filter and repo_filter not in (entry["slug"], entry["key"]):
            repos.append(prior.get(entry["key"], {
                "slug": entry["slug"], "key": entry["key"], "name": entry["name"],
                "clone_status": "not_attempted", "commit": None, "clone_path": None,
            }))
            continue
        clone = _clone_repo(entry)
        repos.append({
            "slug": entry["slug"],
            "key": entry["key"],
            "name": entry["name"],
            "purpose": entry["purpose"],
            "clone_status": clone["clone_status"],
            "clone_error": clone["clone_error"],
            "commit": clone["commit"],
            "clone_path": clone["clone_path"],
            "scan": prior.get(entry["key"], {}).get("scan"),
        })
    cloned = sum(1 for r in repos if r.get("clone_status") == "cloned")
    failed = sum(1 for r in repos if r.get("clone_status") == "failed")
    state = _compose_status(repos, last_sync_at=_now())
    _write_status(state)
    degraded = failed > 0
    return {
        "ok": True,
        "action": "sync-approved",
        "cloned": cloned,
        "failed": failed,
        "degraded": degraded,
        "installs_performed": False,
        "external_code_executed": False,
        "repos": repos,
        "sandbox_dir": _repo_rel(SANDBOX_DIR),
        "generated_at": _now(),
    }


def cmd_scan(repo_filter=None) -> dict:
    repos = []
    prior = {r.get("key"): r for r in _read_status().get("repos", [])}
    for entry in APPROVED_CATALOG:
        rec = dict(prior.get(entry["key"], {
            "slug": entry["slug"], "key": entry["key"], "name": entry["name"],
            "clone_status": "not_attempted", "commit": None, "clone_path": None,
        }))
        rec.setdefault("slug", entry["slug"])
        rec.setdefault("name", entry["name"])
        rec["key"] = entry["key"]
        rec["purpose"] = entry["purpose"]
        if (not repo_filter) or repo_filter in (entry["slug"], entry["key"]):
            rec["scan"] = _scan_repo(entry, SANDBOX_DIR / entry["key"])
        repos.append(rec)
    state = _compose_status(repos, last_scan_at=_now())
    _write_status(state)
    scanned = sum(1 for r in repos if (r.get("scan") or {}).get("scanned"))
    return {
        "ok": True,
        "action": "scan",
        "scanned": scanned,
        "installs_performed": False,
        "external_code_executed": False,
        "repos": repos,
        "generated_at": _now(),
    }


def cmd_write_approval_packet() -> dict:
    if not _is_repo_local(APPROVAL_PACKETS_DIR):
        return {"ok": False, "error": "approval packets dir is outside the repo root"}
    APPROVAL_PACKETS_DIR.mkdir(parents=True, exist_ok=True)
    status = _read_status()
    repos = status.get("repos", []) or _build_repo_records()
    ts = _now()
    packet_path = APPROVAL_PACKETS_DIR / ("external_tool_approval_packet_%s.md" % ts)
    lines = [
        "# External Tool Runtime-Wiring Approval Packet — %s" % MILESTONE,
        "",
        "Generated: %s" % ts,
        "",
        "This packet exists so a human can review each sandboxed external tool",
        "BEFORE any real runtime wiring. Nothing in this packet wires, installs,",
        "or runs anything. Approval is required per tool.",
        "",
        "## Hard scope (current state)",
        "",
        "- Repos cloned: sandbox static inspection only.",
        "- Installs performed: NO.",
        "- External repo code executed: NO.",
        "- Desktop control enabled: NO.",
        "- Live APIs / accounts connected: NO.",
        "- Runtime wiring into Ghoti: NONE — adapter stubs only.",
        "",
        "## Per-tool review",
        "",
    ]
    for rec in repos:
        scan = rec.get("scan") or {}
        lines.extend([
            "### %s (`%s`)" % (rec.get("name", "?"), rec.get("slug", "?")),
            "",
            "- Purpose: %s" % rec.get("purpose", "n/a"),
            "- Clone status: %s" % rec.get("clone_status", "not_attempted"),
            "- Commit: %s" % (rec.get("commit") or "n/a"),
            "- Ecosystems: %s" % (", ".join(scan.get("ecosystems", [])) or "unknown"),
            "- Install requirements (NOT installed): %s"
            % (", ".join(scan.get("install_requirements", [])) or "none detected"),
            "- API key / secret required: %s" % scan.get("api_key_required", "unknown"),
            "- Desktop-control risk: %s" % scan.get("desktop_control_risk", "unknown"),
            "- Live-account risk: %s" % scan.get("live_account_risk", "unknown"),
            "- License: %s" % (scan.get("license") or "unknown"),
            "",
            "Human approval checklist before wiring %s:" % rec.get("name", "?"),
            "- [ ] Static scan reviewed by a human",
            "- [ ] Dependency install reviewed and explicitly approved",
            "- [ ] Desktop-control / live-account risk explicitly accepted (if any)",
            "- [ ] Sandbox-only execution boundary confirmed",
            "- [ ] Operator signs off on runtime wiring",
            "",
        ])
    lines.extend([
        "## Decision",
        "",
        "- [ ] APPROVED for the next supervised wiring step",
        "- [ ] NOT approved — remain sandbox/stub only",
        "",
        "No tool is wired until a human checks the boxes above.",
        "",
    ])
    packet_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "ok": True,
        "action": "write-approval-packet",
        "approval_packet": _repo_rel(packet_path),
        "tools": len(repos),
        "generated_at": _now(),
    }


def _compose_status(repos: list, last_sync_at=None, last_scan_at=None) -> dict:
    prior = _read_status()
    adapters = []
    for entry in APPROVED_CATALOG:
        path = ADAPTERS_DIR / entry["adapter"]
        adapters.append({
            "tool": entry["name"],
            "adapter": entry["adapter"],
            "path": _repo_rel(path),
            "exists": path.exists(),
        })
    return {
        "manager": "external_tool_sandbox_manager",
        "manager_version": MANAGER_VERSION,
        "milestone": MILESTONE,
        "mode": "sandbox_static_inspection_only",
        "sandbox_dir": _repo_rel(SANDBOX_DIR),
        "sandbox_dir_repo_local": _is_repo_local(SANDBOX_DIR),
        "installs_performed": False,
        "external_code_executed": False,
        "runtime_wiring": "none",
        "desktop_control_enabled": False,
        "live_api_enabled": False,
        "live_account_actions": False,
        "human_approval_required": True,
        "approved_catalog_count": len(APPROVED_CATALOG),
        "repos": repos,
        "adapters": adapters,
        "last_sync_at": last_sync_at or prior.get("last_sync_at"),
        "last_scan_at": last_scan_at or prior.get("last_scan_at"),
        "generated_at": _now(),
    }


def cmd_status() -> dict:
    status = _read_status()
    repos = status.get("repos") or _build_repo_records()
    state = _compose_status(
        repos,
        last_sync_at=status.get("last_sync_at"),
        last_scan_at=status.get("last_scan_at"),
    )
    state["ok"] = True
    state["action"] = "status"
    state["approved_catalog"] = [
        {"slug": e["slug"], "key": e["key"], "name": e["name"]} for e in APPROVED_CATALOG
    ]
    state["adapters_generated"] = all(a["exists"] for a in state["adapters"])
    return state


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="External Tool Sandbox Manager (N+4.8A) — safe clone + static scan + adapter stubs.",
    )
    parser.add_argument("--status", action="store_true", help="show sandbox status")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    parser.add_argument("--sync-approved", action="store_true", help="clone approved repos (shallow)")
    parser.add_argument("--scan", action="store_true", help="static-scan cloned repos")
    parser.add_argument("--generate-adapters", action="store_true", help="write the safe adapter stubs")
    parser.add_argument("--write-approval-packet", action="store_true", help="write a human approval packet")
    parser.add_argument("--repo", default=None, help="limit to one approved repo (slug or key)")
    parser.add_argument("--output-dir", default=None, help="reserved; sandbox dir is fixed and repo-local")
    parser.add_argument("--allow-install", action="store_true",
                        help="even if passed, NO install is performed — install only enters the plan")
    args = parser.parse_args(argv)

    # An explicit --repo must be in the approved catalog.
    if args.repo and _catalog_for(args.repo) is None:
        result = {
            "ok": False,
            "error": "repo '%s' is not in the approved catalog" % args.repo,
            "approved_catalog": [e["slug"] for e in APPROVED_CATALOG],
            "generated_at": _now(),
        }
        print(json.dumps(result, indent=2) if args.json else "REJECTED: %s" % result["error"])
        return 1

    try:
        if args.sync_approved:
            result = cmd_sync_approved(args.repo)
        elif args.scan:
            result = cmd_scan(args.repo)
        elif args.generate_adapters:
            result = cmd_generate_adapters()
        elif args.write_approval_packet:
            result = cmd_write_approval_packet()
        else:
            result = cmd_status()
    except Exception as exc:  # never crash with a traceback
        result = {"ok": False, "error": "manager error: %s" % exc, "generated_at": _now()}

    # --allow-install is recorded but never acted on: no install is ever run.
    if args.allow_install and isinstance(result, dict):
        result["allow_install_flag"] = True
        result["install_still_performed"] = False
        result["install_note"] = "install deferred to an approved plan step; nothing was installed"

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
