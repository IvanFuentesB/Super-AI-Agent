"""Safe repo intake: clone-and-static-inspect unknown repos, never execute them.

Dry-run by default: it does NOT clone. With --apply it shallow-clones into a
gitignored sandbox and collects metadata only - it never runs install scripts,
build steps, or any code from the repo. Output is a JSON+MD report under
14_context/tool_intake/reports/ with a conservative decision.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SANDBOX = REPO_ROOT / "14_context" / "tool_intake" / "repo_sandbox"
REPORTS = REPO_ROOT / "14_context" / "tool_intake" / "reports"

_URL_RE = re.compile(r"^(https://|git@)[A-Za-z0-9._:/\-]+(\.git)?$")
SUSPICIOUS = ("postinstall", "preinstall", "curl ", "wget ", "eval(", "base64 -d",
              "rm -rf", "Invoke-Expression", "powershell -enc", "child_process",
              "os.system", "subprocess", "/etc/", "~/.ssh", "AWS_SECRET")
NET_BROWSER_ACCOUNT = ("requests", "httpx", "fetch(", "axios", "playwright",
                       "puppeteer", "selenium", "oauth", "api_key", "token",
                       "stripe", "smtp", "imap")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _slug(repo: str) -> str:
    base = repo.rstrip("/").split("/")[-1].replace(".git", "")
    return re.sub(r"[^A-Za-z0-9._-]", "_", base) or "repo"


def _validate_target(repo: str) -> str | None:
    if _URL_RE.match(repo):
        return repo
    # bare owner/name form -> only allow github shorthand, never local paths
    if re.match(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$", repo):
        return "https://github.com/%s" % repo
    return None


def intake(repo: str, apply: bool = False) -> dict:
    stamp = _now()
    url = _validate_target(repo)
    if url is None:
        return {"ok": False, "action": "repo-intake", "error": "invalid repo url/name",
                "given": repo}
    slug = _slug(url)
    base = {
        "ok": True, "action": "repo-intake", "mode": "apply" if apply else "dry-run",
        "repo": url, "slug": slug, "generated_at": stamp,
        "cloned": False, "executed_anything": False,
    }
    if not apply:
        base.update({
            "decision": "inspect_more",
            "message": "Dry-run: nothing cloned or executed. Re-run with --apply to "
                       "shallow-clone into the gitignored sandbox for static inspection.",
            "planned_sandbox": (SANDBOX / slug).relative_to(REPO_ROOT).as_posix(),
        })
        return base

    SANDBOX.mkdir(parents=True, exist_ok=True)
    dest = SANDBOX / slug
    if dest.exists():
        return {**base, "error": "sandbox path already exists; inspect or remove it first",
                "sandbox": dest.relative_to(REPO_ROOT).as_posix()}
    try:
        # Shallow clone, no submodules, no hooks executed by clone itself.
        subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "clone", "--depth", "1",
                        "--no-single-branch", url, str(dest)],
                       capture_output=True, text=True, timeout=180, shell=False, check=True)
    except Exception as error:
        return {**base, "error": "clone failed: %s" % str(error)[:200]}

    report = _inspect(dest, url, slug, stamp)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / ("%s_%s.json" % (slug, stamp))).write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (REPORTS / ("%s_%s.md" % (slug, stamp))).write_text(_render(report), encoding="utf-8")
    report["report_json"] = ("14_context/tool_intake/reports/%s_%s.json" % (slug, stamp))
    report["cloned"] = True
    return report


def _inspect(root: Path, url: str, slug: str, stamp: str) -> dict:
    files = [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]
    names = [p.name for p in files]
    license_file = next((n for n in names if n.lower().startswith("license")), None)
    pkg_files = [n for n in ("package.json", "pyproject.toml", "Cargo.toml",
                             "setup.py", "requirements.txt") if n in names]
    scripts = _extract_scripts(root, pkg_files)
    readme = next((p for p in files if p.name.lower().startswith("readme")), None)
    readme_snip = ""
    if readme:
        try:
            readme_snip = readme.read_text(encoding="utf-8", errors="replace")[:500]
        except OSError:
            pass
    suspicious = _scan(files, SUSPICIOUS)
    indicators = _scan(files, NET_BROWSER_ACCOUNT)
    decision = "safe_to_adapt"
    if suspicious:
        decision = "risky"
    if len(suspicious) >= 5:
        decision = "reject"
    return {
        "ok": True, "action": "repo-intake", "mode": "apply", "repo": url, "slug": slug,
        "generated_at": stamp, "executed_anything": False,
        "license": license_file, "package_files": pkg_files, "scripts": scripts,
        "readme_snippet": readme_snip.replace("\r", " ").replace("\n", " ")[:300],
        "file_count": len(files),
        "suspicious_hits": suspicious[:20], "suspicious_count": len(suspicious),
        "network_browser_account_indicators": sorted(set(i["pattern"] for i in indicators))[:20],
        "decision": decision,
        "safety": {"executed": False, "install_scripts_run": False, "network_used_beyond_clone": False},
    }


def _extract_scripts(root: Path, pkg_files: list[str]) -> dict:
    scripts = {}
    pkg = root / "package.json"
    if "package.json" in pkg_files and pkg.is_file():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8", errors="replace"))
            scripts["npm"] = list((data.get("scripts") or {}).keys())[:30]
        except Exception:
            scripts["npm"] = ["<unparseable>"]
    return scripts


def _scan(files: list[Path], patterns: tuple) -> list[dict]:
    hits = []
    for p in files:
        if p.suffix.lower() not in (".py", ".js", ".ts", ".json", ".sh", ".ps1",
                                    ".toml", ".cfg", ".yml", ".yaml", ".md", ""):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        low = text.lower()
        for pat in patterns:
            if pat.lower() in low:
                hits.append({"file": p.name, "pattern": pat})
    return hits


def _render(r: dict) -> str:
    return "\n".join([
        "# Repo Intake Report - %s" % r["slug"], "",
        "Repo: %s" % r["repo"], "Generated: %s" % r["generated_at"],
        "Decision: **%s**" % r["decision"], "Executed anything: %s" % r["executed_anything"],
        "", "## Metadata", "",
        "- License: %s" % r.get("license"),
        "- Package files: %s" % ", ".join(r.get("package_files") or []) or "- none",
        "- File count: %s" % r.get("file_count"),
        "- npm scripts: %s" % ", ".join(r.get("scripts", {}).get("npm", [])),
        "", "## Safety scan", "",
        "- Suspicious hits: %s" % r.get("suspicious_count"),
        "- Net/browser/account indicators: %s" % ", ".join(r.get("network_browser_account_indicators") or []),
        "", "## README snippet", "", r.get("readme_snippet", ""), "",
        "## Decision guidance", "",
        "inspect_more -> read more before adapting; safe_to_adapt -> low-risk static reuse; "
        "risky -> isolate, do not run; reject -> do not adapt. Nothing was executed.", "",
    ])


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    apply = "--apply" in args
    repo = next((a for a in args if not a.startswith("--")), None)
    if not repo:
        print(json.dumps({"ok": True, "action": "repo-intake", "mode": "dry-run",
                          "message": "Provide a repo url/name. Dry-run does not clone.",
                          "cloned": False, "executed_anything": False}, indent=2))
        return 0
    print(json.dumps(intake(repo, apply), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
