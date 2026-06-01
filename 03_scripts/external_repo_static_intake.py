#!/usr/bin/env python3
"""External Repo Static Intake - N+6.12A.

Read-only static inspector for externally cloned repositories. It loads a repo
intake manifest, then for each candidate inspects the local clone path and only
reads files. It reports structural facts: presence of README / LICENSE / package
files, the detected license family, and counts of risky-file signals (install
scripts, package lifecycle hooks, shell scripts, binaries, Docker files,
browser / computer-control API references, credential / auth references, and
network / API call references).

Safety contract (true by construction):
- This tool only opens files for reading. It never runs, launches, builds, or
  imports any third-party code, and it performs no dependency bootstrapping.
- It performs no network access.
- Only the Python standard library is used.

The tool exists so Ghoti can intake external repos *properly* - inspect, check
license, and record reusable patterns and risks - instead of blindly running
them. Nothing here wires any repo into the Ghoti runtime.

Usage:
    python 03_scripts/external_repo_static_intake.py --manifest <path> --json
    python 03_scripts/external_repo_static_intake.py --manifest <path> \
        --candidate Ruflo --json
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 03_scripts/<this file> -> repo root is one level up from 03_scripts/.
REPO_ROOT = Path(__file__).resolve().parents[1]

MILESTONE = "N+6.12A"

# Directories that are never useful to walk and are often huge or vendored.
IGNORE_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "dist", "build", "out",
    "__pycache__", ".next", ".turbo", ".cache", "target", "vendor", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "coverage", ".idea", ".vscode", "site-packages",
}

# License family detection: ordered so more specific phrases win first.
LICENSE_SIGNATURES = [
    ("gnu affero general public", "AGPL-3.0"),
    ("gnu lesser general public", "LGPL"),
    ("gnu general public", "GPL"),
    ("apache license", "Apache-2.0"),
    ("mit license", "MIT"),
    ("permission is hereby granted, free of charge", "MIT"),
    ("mozilla public license", "MPL-2.0"),
    ("redistribution and use in source and binary", "BSD"),
    ("isc license", "ISC"),
    ("this is free and unencumbered software released into the public domain", "Unlicense"),
    ("boost software license", "BSL-1.0"),
]

# Package / dependency manifests (presence only; never parsed for execution).
PACKAGE_FILE_NAMES = {
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "pnpm-workspace.yaml", "pyproject.toml", "setup.py", "setup.cfg",
    "requirements.txt", "requirements-dev.txt", "pipfile", "poetry.lock",
    "cargo.toml", "cargo.lock", "go.mod", "go.sum", "gemfile", "pom.xml",
    "build.gradle", "composer.json",
}

# Standalone install / bootstrap scripts (risk: side effects when run).
INSTALL_SCRIPT_NAMES = {
    "install.sh", "install.md", "install.ps1", "install.bat", "setup.sh",
    "bootstrap.sh", "bootstrap.ps1", "make.sh", "build.sh", "get.sh",
}

SHELL_EXTENSIONS = {".sh", ".bash", ".zsh", ".ps1", ".psm1", ".bat", ".cmd"}
BINARY_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".wasm", ".o", ".a", ".node",
    ".class", ".jar", ".pyd", ".lib", ".obj",
}

# package.json lifecycle script keys that can run code on dependency setup.
LIFECYCLE_HOOK_KEYS = {
    "preinstall", "install", "postinstall", "preprepare", "prepare",
    "prepublish", "prepublishonly", "prepack", "postpack",
}

# Source-text extensions worth scanning for capability keywords (bounded).
TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".rs", ".go",
    ".json", ".md", ".txt", ".toml", ".yaml", ".yml", ".cfg", ".ini",
    ".sh", ".ps1", ".html",
}

# Capability keyword signals. These describe what a repo *can* do; they are not
# executed - the tool only counts files whose text contains them.
BROWSER_CONTROL_KEYWORDS = [
    "playwright", "puppeteer", "selenium", "pyautogui", "pynput", "xdotool",
    "chromedevtools", "devtools protocol", "cdp ", "websocket", "screenshot",
    "mouse_move", "left_click", "keyboard.press", "page.goto", "browser.new",
    "computer-use", "computer_use", "desktop control",
]
CREDENTIAL_KEYWORDS = [
    "api_key", "apikey", "api-key", "client_secret", "access_token",
    "anthropic_api_key", "openai_api_key", "bearer ", "authorization:",
    "password", "private_key", "oauth",
]
NETWORK_KEYWORDS = [
    "requests.get", "requests.post", "httpx.", "urllib.request", "aiohttp",
    "fetch(", "axios", "http.client", "websockets.connect", "socket.socket",
    "reqwest", "fetch_url",
]

MAX_FILE_BYTES = 512 * 1024     # skip files larger than this for keyword scans
MAX_SCAN_FILES = 6000           # bound the total files scanned per candidate
MAX_EXAMPLES = 5                # cap example paths reported per signal
MAX_TOP_LEVEL = 40              # cap reported top-level entries


def _lower_name(path):
    return path.name.lower()


def detect_license_family(license_path):
    """Return a best-effort SPDX-ish license family from a license file's text."""
    try:
        text = license_path.read_text(encoding="utf-8", errors="ignore")[:8000].lower()
    except OSError:
        return None
    for needle, family in LICENSE_SIGNATURES:
        if needle in text:
            return family
    return "Unknown"


def _is_docker_file(name_lower):
    return (
        name_lower == "dockerfile"
        or name_lower.startswith("dockerfile.")
        or name_lower.startswith("docker-compose")
        or name_lower.endswith(".dockerfile")
    )


def _read_lifecycle_hooks(pkg_json_path):
    """Parse package.json (data only) and list any lifecycle script keys present."""
    try:
        data = json.loads(pkg_json_path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, ValueError):
        return []
    scripts = data.get("scripts") if isinstance(data, dict) else None
    if not isinstance(scripts, dict):
        return []
    return sorted(k for k in scripts if k.lower() in LIFECYCLE_HOOK_KEYS)


def _scan_keywords(text_lower, keywords):
    return any(k in text_lower for k in keywords)


def inspect_candidate(candidate):
    """Inspect one candidate's local clone path read-only and return a report."""
    name = candidate.get("name", "unknown")
    local_path = candidate.get("local_path")
    report = {
        "name": name,
        "local_path": local_path,
        "present": False,
        "declared_source_url": candidate.get("source_url"),
        "declared_commit_sha": candidate.get("commit_sha"),
        "declared_license": candidate.get("license_detected"),
        "safe_to_run": False,
        "runtime_wired": False,
    }
    if not local_path:
        report["note"] = "no local_path declared (source-needed candidate)"
        return report

    root = (REPO_ROOT / local_path).resolve()
    if not root.is_dir():
        report["note"] = "local path not present (clone absent in this checkout)"
        return report

    report["present"] = True
    top_level = []
    readme_files = []
    license_files = []
    package_files = []
    install_scripts = []
    docker_files = []
    lifecycle_hook_packages = []
    shell_count = 0
    binary_count = 0
    files_scanned = 0
    browser_hits = []
    credential_hits = []
    network_hits = []

    try:
        top_level = sorted(p.name for p in root.iterdir())[:MAX_TOP_LEVEL]
    except OSError:
        pass

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d.lower() not in IGNORE_DIRS]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            rel = fpath.relative_to(root).as_posix()
            nl = fname.lower()
            ext = fpath.suffix.lower()

            if nl.startswith("readme"):
                if len(readme_files) < MAX_EXAMPLES:
                    readme_files.append(rel)
            if nl.startswith("licen") or nl.startswith("copying") or nl == "unlicense":
                if len(license_files) < MAX_EXAMPLES:
                    license_files.append(rel)
            if nl in PACKAGE_FILE_NAMES:
                if len(package_files) < 12:
                    package_files.append(rel)
            if nl in INSTALL_SCRIPT_NAMES:
                if len(install_scripts) < MAX_EXAMPLES:
                    install_scripts.append(rel)
            if _is_docker_file(nl):
                if len(docker_files) < MAX_EXAMPLES:
                    docker_files.append(rel)
            if ext in SHELL_EXTENSIONS:
                shell_count += 1
            if ext in BINARY_EXTENSIONS:
                binary_count += 1
            if nl == "package.json":
                hooks = _read_lifecycle_hooks(fpath)
                if hooks:
                    lifecycle_hook_packages.append({"file": rel, "hooks": hooks})

            # Bounded keyword scan of text files only.
            if files_scanned < MAX_SCAN_FILES and ext in TEXT_EXTENSIONS:
                try:
                    if fpath.stat().st_size <= MAX_FILE_BYTES:
                        files_scanned += 1
                        body = fpath.read_text(encoding="utf-8", errors="ignore").lower()
                        if _scan_keywords(body, BROWSER_CONTROL_KEYWORDS) and len(browser_hits) < MAX_EXAMPLES:
                            browser_hits.append(rel)
                        if _scan_keywords(body, CREDENTIAL_KEYWORDS) and len(credential_hits) < MAX_EXAMPLES:
                            credential_hits.append(rel)
                        if _scan_keywords(body, NETWORK_KEYWORDS) and len(network_hits) < MAX_EXAMPLES:
                            network_hits.append(rel)
                except OSError:
                    pass

    license_family = None
    if license_files:
        license_family = detect_license_family(root / license_files[0])

    report.update({
        "top_level_sample": top_level,
        "readme_found": bool(readme_files),
        "readme_files": readme_files,
        "license_found": bool(license_files),
        "license_files": license_files,
        "license_family_detected": license_family,
        "package_files": package_files,
        "files_scanned": files_scanned,
        "risky_signals": {
            "install_scripts": install_scripts,
            "package_lifecycle_hooks": lifecycle_hook_packages,
            "shell_script_count": shell_count,
            "binary_file_count": binary_count,
            "docker_files": docker_files,
            "browser_or_computer_control_refs": {
                "found": bool(browser_hits),
                "examples": browser_hits,
            },
            "credential_or_auth_refs": {
                "found": bool(credential_hits),
                "examples": credential_hits,
            },
            "network_or_api_refs": {
                "found": bool(network_hits),
                "examples": network_hits,
            },
        },
    })
    return report


def load_manifest(manifest_path):
    path = Path(manifest_path)
    if not path.is_absolute():
        path = (Path.cwd() / path)
    if not path.is_file():
        # Fall back to resolving relative to the repo root.
        alt = REPO_ROOT / manifest_path
        if alt.is_file():
            path = alt
    return json.loads(path.read_text(encoding="utf-8")), path


def build_report(manifest, manifest_path, candidate_filter):
    candidates = manifest.get("candidates", [])
    if candidate_filter:
        wanted = candidate_filter.lower()
        selected = []
        for cand in candidates:
            names = [str(cand.get("name", "")).lower()]
            names += [str(a).lower() for a in cand.get("aliases", [])]
            if any(wanted == n or wanted in n for n in names):
                selected.append(cand)
        candidates = selected
    reports = [inspect_candidate(c) for c in candidates]
    return {
        "milestone": MILESTONE,
        "tool": "external_repo_static_intake",
        "manifest": str(manifest_path),
        "static_inspection_only": True,
        "candidate_filter": candidate_filter,
        "candidates_inspected": len(reports),
        "safety": {
            "executed_third_party_code": False,
            "imported_third_party_modules": False,
            "installed_dependencies": False,
            "network_used": False,
            "only_standard_library": True,
            "read_only": True,
        },
        "reports": reports,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Static, read-only intake inspector for external repo clones.",
    )
    parser.add_argument("--manifest", required=True, help="Path to a repo intake manifest JSON.")
    parser.add_argument("--candidate", default=None, help="Filter to one candidate by name or alias.")
    parser.add_argument("--json", action="store_true", help="Emit the full JSON report.")
    args = parser.parse_args(argv)

    try:
        manifest, manifest_path = load_manifest(args.manifest)
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": f"could not load manifest: {exc}"}))
        return 2

    report = build_report(manifest, manifest_path, args.candidate)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"{report['tool']} ({report['milestone']})")
        print(f"manifest: {report['manifest']}")
        print(f"candidates inspected: {report['candidates_inspected']}")
        for rep in report["reports"]:
            state = "present" if rep.get("present") else "absent"
            lic = rep.get("license_family_detected") or rep.get("declared_license") or "?"
            print(f"  - {rep['name']}: {state}, license={lic}, "
                  f"safe_to_run={rep['safe_to_run']}, runtime_wired={rep['runtime_wired']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
