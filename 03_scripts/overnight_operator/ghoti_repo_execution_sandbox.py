#!/usr/bin/env python3
"""Ghoti Repo Execution Sandbox (N+6.19A).

Where Ghoti starts actually USING external open-source repos instead of only
documenting them - safely. Every external repo is listed in
14_context/overnight_operator/allowlists/allowed_repos_n6_19a.json, every command
class is listed in allowed_commands_n6_19a.json, and the static-scan risk patterns are
data (loaded from that allowlist) so this script holds no risky literal tokens.

Actions:
  * --list                     list the allowlisted repos and whether each is present.
  * --repo X --static-scan     read-only safety scan of a present repo's files.
  * --repo X --clone           shallow git clone of an allowlisted URL into the
                               sandbox (network), only if the repo allows it.
  * --repo X --run-allowlisted read-only git metadata + license/readme detection on a
                               cloned repo.

Safety posture (enforced by construction):
  * Standard library only. Every subprocess call is an argument list with a timeout;
    there is no shell string, no PowerShell expression invocation, and no privileged or container
    command. Clone destinations must be under 21_repos/third_party_runtime_sandbox/.
  * Cloned repo contents are git-ignored and never committed. No editable install,
    CLI run, or test runs here; those stay deferred behind a feature flag.
  * No secrets are read or passed. Reports go under repo_execution_reports/generated/
    (git-ignored).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

MILESTONE = "N+6.19A"

REPO_ROOT = Path(__file__).resolve().parents[2]
OP_DIR = REPO_ROOT / "14_context" / "overnight_operator"
ALLOWED_REPOS = OP_DIR / "allowlists" / "allowed_repos_n6_19a.json"
ALLOWED_COMMANDS = OP_DIR / "allowlists" / "allowed_commands_n6_19a.json"
REPORTS_DIR = OP_DIR / "repo_execution_reports"
GENERATED_REPORTS = REPORTS_DIR / "generated"
SANDBOX_PREFIX = "21_repos/third_party_runtime_sandbox/"
SANDBOX_ROOT = REPO_ROOT / "21_repos" / "third_party_runtime_sandbox"

TEXT_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".toml", ".cfg", ".ini", ".txt",
    ".md", ".sh", ".ps1", ".yml", ".yaml", ".rs", ".go", ".rb", ".java", ".c", ".h",
    ".cpp", ".bat", ".cmd",
}
SCAN_FILE_CAP = 6000
SCAN_BYTES_CAP = 400000

SAFETY = {
    "local_only": True,
    "clones_committed": False,
    "runtime_execution_default": False,
    "uses_shell_string_subprocess": False,
    "system_python_install": False,
    "container_runtime_used": False,
    "browser_automation": False,
    "reads_secret_values": False,
    "writes_only_inside_sandbox_and_reports": True,
}


def _load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _repo_entry(name):
    data = _load_json(ALLOWED_REPOS) or {}
    if not name:
        return None
    lowered = str(name).lower()
    for repo in data.get("repos", []):
        if name in (repo.get("name"), repo.get("slug")) or lowered == str(repo.get("slug", "")).lower():
            return repo
    return None


def _resolve_repo_dir(entry):
    for key in ("sandbox_clone_path", "local_static_path"):
        rel = entry.get(key)
        if rel:
            path = REPO_ROOT / rel
            if path.is_dir():
                return path, key
    return None, None


def _risk_patterns():
    data = _load_json(ALLOWED_COMMANDS) or {}
    compiled = []
    for item in data.get("static_scan_risk_patterns", []):
        try:
            compiled.append((item["id"], re.compile(item["regex"]), item.get("severity", "review")))
        except (re.error, KeyError):
            continue
    return compiled


def _run(argv, cwd, timeout):
    """Run an argument-list command with a timeout. No shell string is ever used."""
    try:
        proc = subprocess.run(
            argv, cwd=str(cwd), capture_output=True, text=True, timeout=timeout
        )
        return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, "", exc.__class__.__name__


def _static_scan(repo_dir):
    patterns = _risk_patterns()
    findings = {}
    files_scanned = 0
    for path in repo_dir.rglob("*"):
        if files_scanned >= SCAN_FILE_CAP:
            break
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_EXTS and path.name not in {
            "LICENSE", "LICENSE.md", "LICENSE.txt", "README", "README.md",
            "Dockerfile", "Makefile",
        }:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")[:SCAN_BYTES_CAP]
        except OSError:
            continue
        files_scanned += 1
        for pid, rx, sev in patterns:
            if rx.search(text):
                rec = findings.setdefault(pid, {"id": pid, "severity": sev, "files": 0})
                rec["files"] += 1
    has_high = any(f["severity"] == "high" for f in findings.values())
    has_review = any(f["severity"] == "review" for f in findings.values())
    verdict = "blocked" if has_high else ("needs_review" if has_review else "safe")
    return {"files_scanned": files_scanned, "findings": list(findings.values()), "verdict": verdict}


def _detect_license(repo_dir):
    for fname in ("LICENSE", "LICENSE.md", "LICENSE.txt"):
        path = repo_dir / fname
        if path.is_file():
            try:
                text = path.read_text(encoding="utf-8", errors="replace").lower()
            except OSError:
                continue
            if "mit license" in text or "permission is hereby granted, free of charge" in text:
                return "MIT"
            if "apache license" in text:
                return "Apache-2.0"
            if "bsd " in text:
                return "BSD"
            return "present_unclassified"
    return None


def _write_report(report):
    GENERATED_REPORTS.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    slug = re.sub(r"[^a-z0-9]+", "-", str(report.get("repo", "repo")).lower()).strip("-")
    path = GENERATED_REPORTS / "{0}_{1}_{2}.json".format(stamp, slug, report.get("action", "action"))
    try:
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return path.relative_to(REPO_ROOT).as_posix()
    except OSError:
        return None


def _err(reason, action=None, repo=None):
    return {"ok": False, "milestone": MILESTONE, "action": action, "repo": repo,
            "error": reason, "safety": dict(SAFETY)}


def do_list():
    data = _load_json(ALLOWED_REPOS) or {}
    repos = []
    for repo in data.get("repos", []):
        repo_dir, kind = _resolve_repo_dir(repo)
        repos.append({
            "name": repo.get("name"),
            "slug": repo.get("slug"),
            "source_url": repo.get("source_url"),
            "source_url_required": bool(repo.get("source_url_required")),
            "allowed_actions": repo.get("allowed_actions", []),
            "present_locally": repo_dir is not None,
            "present_path_kind": kind,
            "sandbox_clone_path": repo.get("sandbox_clone_path"),
            "runtime_execution_allowed": bool(repo.get("runtime_execution_allowed")),
        })
    return {"ok": True, "milestone": MILESTONE, "action": "list",
            "repo_count": len(repos), "repos": repos, "safety": dict(SAFETY)}


def do_static_scan(name):
    entry = _repo_entry(name)
    if not entry:
        return _err("repo not allowlisted: {0}".format(name), "static_scan", name)
    if "static_scan" not in entry.get("allowed_actions", []):
        return _err("static_scan not allowed for {0}".format(entry.get("name")), "static_scan", entry.get("name"))
    repo_dir, kind = _resolve_repo_dir(entry)
    report = {
        "ok": True, "milestone": MILESTONE, "repo": entry.get("name"), "action": "static_scan",
        "command_preview": "in-process read-only file scan", "executed": repo_dir is not None,
        "exit_code": None, "timeout": None, "cwd": str(repo_dir) if repo_dir else None,
        "files_touched": [], "present": repo_dir is not None,
    }
    if repo_dir is None:
        report["safety_verdict"] = "not_present"
        if "clone" in entry.get("allowed_actions", []) and entry.get("source_url"):
            report["next_action"] = "clone first with --clone, then re-run --static-scan"
        else:
            report["next_action"] = ("the N+6.12A static clone lives in the primary worktree and "
                                      "is not present in this runtime worktree")
    else:
        scan = _static_scan(repo_dir)
        report["present_path_kind"] = kind
        report["scan"] = scan
        report["safety_verdict"] = scan["verdict"]
        report["next_action"] = {
            "safe": "read-only metadata commands are cleared; install/run still deferred behind a flag",
            "needs_review": "human review of the flagged patterns before any install or run",
            "blocked": "do not install or run; a high-risk pattern was found",
        }[scan["verdict"]]
    report["report_path"] = _write_report(report)
    report["safety"] = dict(SAFETY)
    return report


def do_clone(name):
    entry = _repo_entry(name)
    if not entry:
        return _err("repo not allowlisted: {0}".format(name), "clone", name)
    if "clone" not in entry.get("allowed_actions", []):
        return _err("clone not allowed for {0}".format(entry.get("name")), "clone", entry.get("name"))
    url = entry.get("source_url")
    if not url or entry.get("source_url_required"):
        return _err("no confident source_url for {0}; will not guess".format(entry.get("name")), "clone", entry.get("name"))
    dest_rel = entry.get("sandbox_clone_path")
    if not dest_rel or not str(dest_rel).startswith(SANDBOX_PREFIX):
        return _err("clone destination must be under the sandbox root", "clone", entry.get("name"))
    dest = REPO_ROOT / dest_rel
    commands = _load_json(ALLOWED_COMMANDS) or {}
    clone_timeout = 300
    for cls in commands.get("allowed_command_classes", []):
        if cls.get("id") == "git_clone_shallow":
            clone_timeout = int(cls.get("timeout_seconds", 300))
    preview = "git clone --depth 1 {0} {1}".format(url, dest_rel)
    report = {
        "ok": False, "milestone": MILESTONE, "repo": entry.get("name"), "action": "clone",
        "command_preview": preview, "timeout": clone_timeout, "cwd": str(SANDBOX_ROOT),
        "files_touched": [dest_rel],
    }
    if dest.exists():
        report.update({"executed": False, "exit_code": None, "already_present": True,
                       "safety_verdict": "already_cloned",
                       "next_action": "run --static-scan then --run-allowlisted", "ok": True})
    else:
        SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)
        argv = ["git", "clone", "--depth", "1", url, str(dest)]
        rc, _out, err = _run(argv, SANDBOX_ROOT, clone_timeout)
        cloned = rc == 0 and dest.exists()
        report.update({
            "executed": True, "exit_code": rc,
            "safety_verdict": "cloned" if cloned else "clone_failed",
            "stderr_tail": (err or "")[-300:],
            "next_action": "run --static-scan then --run-allowlisted" if cloned else "clone failed; check network/URL",
            "ok": cloned,
        })
    report["report_path"] = _write_report(report)
    report["safety"] = dict(SAFETY)
    return report


def do_run_allowlisted(name):
    entry = _repo_entry(name)
    if not entry:
        return _err("repo not allowlisted: {0}".format(name), "run_allowlisted", name)
    if "run_allowlisted_if_cloned" not in entry.get("allowed_actions", []):
        return _err("run_allowlisted not allowed for {0}".format(entry.get("name")), "run_allowlisted", entry.get("name"))
    dest_rel = entry.get("sandbox_clone_path")
    dest = REPO_ROOT / dest_rel if dest_rel else None
    if not dest or not dest.is_dir():
        return _err("repo not cloned yet; run --clone first", "run_allowlisted", entry.get("name"))

    steps = []
    rc_head, head_out, _ = _run(["git", "rev-parse", "HEAD"], dest, 30)
    steps.append({"command_preview": "git rev-parse HEAD", "executed": True,
                  "exit_code": rc_head, "output": head_out[:80]})
    rc_log, log_out, _ = _run(["git", "log", "-1", "--oneline"], dest, 30)
    steps.append({"command_preview": "git log -1 --oneline", "executed": True,
                  "exit_code": rc_log, "output": log_out[:160]})
    top_level = sorted(p.name for p in dest.iterdir() if p.name != ".git")[:80]
    steps.append({"command_preview": "list top-level files (in-process)", "executed": True,
                  "exit_code": 0, "output": "{0} entries".format(len(top_level))})

    metadata_present = [
        fname for fname in (
            "LICENSE", "LICENSE.md", "LICENSE.txt", "README.md", "README",
            "pyproject.toml", "setup.py", "setup.cfg", "package.json",
        ) if (dest / fname).is_file()
    ]
    package_pyproject = None
    candidate = dest / "packages" / "markitdown" / "pyproject.toml"
    if candidate.is_file():
        package_pyproject = "packages/markitdown/pyproject.toml"

    report = {
        "ok": True, "milestone": MILESTONE, "repo": entry.get("name"), "action": "run_allowlisted",
        "command_preview": "git rev-parse HEAD; git log -1 --oneline; list files; read metadata",
        "executed": True, "exit_code": 0, "timeout": 30, "cwd": str(dest),
        "files_touched": [dest_rel], "head_commit": head_out[:80] if rc_head == 0 else None,
        "latest_commit": log_out[:160] if rc_log == 0 else None,
        "top_level_files": top_level, "metadata_present": metadata_present,
        "license_detected": _detect_license(dest), "package_pyproject": package_pyproject,
        "safety_verdict": "read_only_metadata_ok",
        "next_action": ("venv + editable install + `markitdown --help` are prepared but "
                        "deferred behind markitdown_sandbox_enabled (install only into an "
                        "isolated sandbox venv, never system Python)"),
        "steps": steps,
    }
    report["report_path"] = _write_report(report)
    report["safety"] = dict(SAFETY)
    return report


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Ghoti Repo Execution Sandbox (N+6.19A) - allowlisted, local-first."
    )
    parser.add_argument("--list", action="store_true", help="List allowlisted repos.")
    parser.add_argument("--repo", help="Allowlisted repo name or slug.")
    parser.add_argument("--static-scan", action="store_true", help="Read-only safety scan.")
    parser.add_argument("--clone", action="store_true", help="Shallow clone into the sandbox.")
    parser.add_argument("--run-allowlisted", action="store_true",
                        help="Run read-only git metadata commands on a cloned repo.")
    parser.add_argument("--json", action="store_true", help="Emit JSON (default).")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    if args.list:
        result = do_list()
    elif args.repo and args.static_scan:
        result = do_static_scan(args.repo)
    elif args.repo and args.clone:
        result = do_clone(args.repo)
    elif args.repo and args.run_allowlisted:
        result = do_run_allowlisted(args.repo)
    else:
        result = {"ok": False, "milestone": MILESTONE,
                  "error": "specify --list, or --repo <name> with --static-scan / --clone / --run-allowlisted",
                  "safety": dict(SAFETY)}
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
