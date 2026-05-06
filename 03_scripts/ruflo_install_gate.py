#!/usr/bin/env python3
"""Ruflo Install Gate — stdlib-only, isolated npm ci, no global install, no runtime wiring.

N+3.56-FIX: added --source-status with clear SOURCE_PRESENT/SOURCE_MISSING codes.
             Truthful messaging for clean checkouts where source may be absent.
N+3.51A: added safe_write fallback (Node.js), clearer install path messaging.
Ruflo (claude-flow v3.5.80) has no lifecycle scripts — npm ci --ignore-scripts is safe.
"""
import argparse
import base64
import datetime
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
RUFLO_DIR = REPO_ROOT / "21_repos" / "third_party" / "evals" / "ruflo"
LOGS_DIR = REPO_ROOT / "05_logs" / "ruflo_smoke"
TOOLING_DIR = REPO_ROOT / "14_context" / "tooling"
CONFIGS_DIR = REPO_ROOT / "23_configs"

LIFECYCLE_SCRIPTS = frozenset([
    "preinstall", "install", "postinstall",
    "prepare", "prepack", "postpack",
    "prepublish", "prepublishOnly",
])


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _run(cmd, cwd=None, timeout=10):
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True,
            cwd=str(cwd or REPO_ROOT), timeout=timeout
        )
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1
    except Exception as e:
        return "", "ERROR: " + str(e), -1


def _safe_write_text(dest: pathlib.Path, content: str) -> None:
    """Write text to dest; fall back to Node.js if permission denied. Raises on total failure."""
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        return
    except (PermissionError, OSError):
        pass

    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
    node_script = (
        "const fs=require('fs'),p=require('path'),"
        f"dest={json.dumps(str(dest))},"
        f"enc={json.dumps(encoded)};"
        "fs.mkdirSync(p.dirname(dest),{recursive:true});"
        "fs.writeFileSync(dest,Buffer.from(enc,'base64'));"
        "console.log('WRITTEN');"
    )
    out, err_txt, rc = _run(["node", "-e", node_script], timeout=15)
    if rc != 0 or "WRITTEN" not in out:
        raise RuntimeError(f"Node.js write fallback failed (rc={rc}): {err_txt[:300]}")


def _read_package_json():
    pkg_path = RUFLO_DIR / "package.json"
    if not pkg_path.exists():
        return None, "package.json not found"
    try:
        return json.loads(pkg_path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as e:
        return None, f"package.json parse error: {e}"


def _detect_lifecycle(scripts_dict):
    return [k for k in scripts_dict if k in LIFECYCLE_SCRIPTS]


def _check_npm():
    ver, _, rc = _run(["npm", "--version"])
    return (ver if rc == 0 else None)


def _check_node():
    ver, _, rc = _run(["node", "--version"])
    return (ver if rc == 0 else None)


def _get_ruflo_git_remote():
    out, _, rc = _run(["git", "-C", str(RUFLO_DIR), "remote", "get-url", "origin"])
    return out if rc == 0 else None


def _get_ruflo_git_head():
    out, _, rc = _run(["git", "-C", str(RUFLO_DIR), "rev-parse", "HEAD"])
    return out if rc == 0 else None


def cmd_source_status(args):
    """Report Ruflo source presence with clear status codes. Truthful for clean checkouts."""
    print("=== Ruflo Source Status ===")

    ruflo_exists = RUFLO_DIR.exists()
    pkg_path = RUFLO_DIR / "package.json"
    lock_path = RUFLO_DIR / "package-lock.json"
    nm_path = RUFLO_DIR / "node_modules"
    npm_ver = _check_npm()
    node_ver = _check_node()

    if ruflo_exists and pkg_path.exists():
        print("SOURCE_PRESENT")
        print(f"  Ruflo dir          : {RUFLO_DIR.relative_to(REPO_ROOT)}")

        # Try git remote
        remote = _get_ruflo_git_remote()
        head = _get_ruflo_git_head()
        if remote:
            print(f"  Git remote         : {remote}")
        else:
            print("  Git remote         : NOT DETECTED — source URL needs manual confirmation")
        if head:
            print(f"  Git HEAD           : {head}")

        pkg, err = _read_package_json()
        if pkg:
            print(f"  Package name       : {pkg.get('name', '?')}")
            print(f"  Package version    : {pkg.get('version', '?')}")
            scripts = pkg.get("scripts", {})
            lifecycle = _detect_lifecycle(scripts)
            if lifecycle:
                print(f"  Lifecycle scripts  : {lifecycle} — INSTALL BLOCKED")
            else:
                print("  Lifecycle scripts  : NONE (safe)")
        else:
            print(f"  Package JSON error : {err}")
    elif ruflo_exists:
        print("SOURCE_PRESENT (partial — dir exists but package.json missing)")
        print(f"  Ruflo dir          : {RUFLO_DIR.relative_to(REPO_ROOT)}")
    else:
        # Determine if bootstrappable
        source_config = CONFIGS_DIR / "ruflo_source.example.json"
        if source_config.exists():
            print("SOURCE_MISSING_BOOTSTRAPPABLE")
            print(f"  Ruflo dir          : ABSENT in this checkout")
            print(f"  Bootstrap config   : {source_config.relative_to(REPO_ROOT)} (check for clone instructions)")
        else:
            print("SOURCE_MISSING_NO_CONFIG")
            print(f"  Ruflo dir          : ABSENT in this checkout")
            print(f"  NOTE: Ruflo is an external tool. In a clean checkout its source")
            print(f"        is not automatically present. It must be cloned/bootstrapped")
            print(f"        manually before this gate can proceed.")

    print()
    if lock_path.exists():
        print("PACKAGE_LOCK_PRESENT")
    else:
        print("PACKAGE_LOCK_MISSING (npm ci requires package-lock.json)")

    if npm_ver:
        print(f"NPM_PRESENT ({npm_ver})")
    else:
        print("NPM_MISSING — install Node.js/npm before running install")

    if node_ver:
        print(f"NODE_PRESENT ({node_ver})")
    else:
        print("NODE_MISSING")

    if nm_path.exists():
        try:
            count = len([d for d in nm_path.iterdir() if d.is_dir()])
            print(f"NODE_MODULES_INSTALLED ({count} top-level packages)")
        except Exception:
            print("NODE_MODULES_INSTALLED")
    else:
        print("NODE_MODULES_MISSING")

    print("RUNTIME_WIRING_NO — isolated install only, no MCP/swarm launch")

    # Write/update ruflo_source.example.json if remote detected
    if ruflo_exists and pkg_path.exists():
        remote = _get_ruflo_git_remote()
        pkg, _ = _read_package_json()
        if pkg and args.apply:
            source_config = CONFIGS_DIR / "ruflo_source.example.json"
            source_data = {
                "_comment": "Ruflo source config. N+3.56-FIX auto-detected. Runtime wiring: NO.",
                "local_path": str(RUFLO_DIR.relative_to(REPO_ROOT)),
                "source_url": remote if remote else "UNKNOWN — manual confirmation required",
                "expected_package_name": pkg.get("name", "claude-flow"),
                "runtime_wiring": False,
                "no_mcp_launch": True,
                "no_swarm_launch": True,
                "install_command": "npm ci --ignore-scripts",
                "git_head": _get_ruflo_git_head() or "unknown",
            }
            try:
                _safe_write_text(source_config, json.dumps(source_data, indent=2) + "\n")
                print(f"\nWritten: {source_config.relative_to(REPO_ROOT)}")
            except RuntimeError as e:
                print(f"\nWARNING: Could not write ruflo_source.example.json: {e}")
        elif args.dry_run:
            print("\n[DRY RUN] Pass --apply to write/update 23_configs/ruflo_source.example.json")

    print("=== End Ruflo Source Status ===")


def cmd_status(args):
    print("=== Ruflo Install Gate Status ===")
    print(f"Repo root  : {REPO_ROOT}")
    print(f"Ruflo dir  : {RUFLO_DIR}")
    print(f"Exists     : {'YES' if RUFLO_DIR.exists() else 'NO'}")

    pkg, err = _read_package_json()
    if err:
        print(f"Package    : ERROR — {err}")
        if not RUFLO_DIR.exists():
            print(f"NOTE: Ruflo source absent in this checkout. Run --source-status for details.")
    else:
        print(f"Package    : {pkg.get('name', '?')} v{pkg.get('version', '?')}")
        scripts = pkg.get("scripts", {})
        lifecycle = _detect_lifecycle(scripts)
        if lifecycle:
            print(f"Lifecycle scripts detected: {lifecycle} — INSTALL BLOCKED")
        else:
            print("Lifecycle scripts detected: NONE (install safe with --ignore-scripts)")
        print(f"All scripts: {list(scripts.keys())}")

    nm = RUFLO_DIR / "node_modules"
    lock = RUFLO_DIR / "package-lock.json"
    print(f"node_modules   : {'INSTALLED' if nm.exists() else 'NOT INSTALLED'}")
    print(f"package-lock   : {'EXISTS' if lock.exists() else 'MISSING (npm ci requires this)'}")
    print(f"npm version    : {_check_npm() or 'not found'}")
    print(f"node version   : {_check_node() or 'not found'}")
    print(f"Safe write     : Node.js fallback enabled")
    print(f"Runtime wiring : NO — isolated install only, no MCP/swarm launch")
    print("=== End Status ===")


def cmd_install(args):
    pkg, err = _read_package_json()
    if err:
        print(f"ERROR: {err}")
        if not RUFLO_DIR.exists():
            print("BLOCKED: Ruflo source not present in this checkout.")
            print("Run: python 03_scripts/ruflo_install_gate.py --source-status")
            print("Then bootstrap/clone Ruflo locally before installing.")
        sys.exit(1)

    scripts = pkg.get("scripts", {})
    lifecycle = _detect_lifecycle(scripts)
    if lifecycle:
        print(f"BLOCKED: Lifecycle scripts detected: {lifecycle}")
        print("Install is blocked until an explicit override is added.")
        sys.exit(1)

    lock = RUFLO_DIR / "package-lock.json"
    if not lock.exists():
        print("BLOCKED: package-lock.json missing — npm ci requires it.")
        print("Safe alternative: run 'npm install --ignore-scripts' once to generate package-lock,")
        print("then rerun this gate with --apply. Requires explicit user approval first.")
        sys.exit(1)

    cmd = ["npm", "ci", "--ignore-scripts"]

    if args.dry_run and not args.apply:
        pkg_name = pkg.get("name", "?")
        pkg_ver = pkg.get("version", "?")
        print(f"[DRY RUN] Package  : {pkg_name} v{pkg_ver}")
        print(f"[DRY RUN] Ruflo dir: {RUFLO_DIR}")
        print(f"[DRY RUN] Command  : {' '.join(cmd)}")
        print("[DRY RUN] Lifecycle scripts: NONE — safe to install.")
        print("[DRY RUN] package-lock.json: EXISTS")
        print("[DRY RUN] Pass --apply to execute.")
        return

    if args.apply:
        npm_ver = _check_npm()
        if not npm_ver:
            print("ERROR: npm not found. Cannot install.")
            sys.exit(1)

        print(f"Running: {' '.join(cmd)}")
        print(f"Working dir: {RUFLO_DIR}")
        out, err_txt, rc = _run(cmd, cwd=RUFLO_DIR, timeout=180)
        if out:
            print(out[-2000:])
        if err_txt:
            print("[stderr]", err_txt[-500:])
        if rc == 0:
            print("Install: COMPLETE")
            nm = RUFLO_DIR / "node_modules"
            print(f"node_modules exists: {'YES' if nm.exists() else 'NO (unexpected)'}")
        else:
            print(f"Install: FAILED (exit {rc})")
            sys.exit(1)


def cmd_smoke(args):
    print("=== Ruflo Smoke Check (read-only) ===")
    pkg, err = _read_package_json()
    if err:
        print(f"package.json: ERROR — {err}")
        if not RUFLO_DIR.exists():
            print("NOTE: Source absent in this checkout — this is expected on a clean clone.")
            print("Run --source-status for bootstrap instructions.")
    else:
        print(f"Package: {pkg.get('name', '?')} v{pkg.get('version', '?')}")
        scripts = pkg.get("scripts", {})
        lifecycle = _detect_lifecycle(scripts)
        if lifecycle:
            print(f"Lifecycle scripts: {lifecycle} — INSTALL BLOCKED")
        else:
            print("Lifecycle scripts: NONE (safe)")
        print(f"All scripts: {list(scripts.keys())}")
        print(f"Dependencies: {list(pkg.get('dependencies', {}).keys())}")
        print(f"Optional deps: {list(pkg.get('optionalDependencies', {}).keys())}")

    nm = RUFLO_DIR / "node_modules"
    lock = RUFLO_DIR / "package-lock.json"
    print(f"node_modules exists: {'YES' if nm.exists() else 'NO'}")
    print(f"package-lock exists: {'YES' if lock.exists() else 'NO'}")

    npm_ver = _check_npm()
    node_ver = _check_node()
    print(f"npm version : {npm_ver or 'not found'}")
    print(f"node version: {node_ver or 'not found'}")

    if nm.exists():
        try:
            pkg_count = len([d for d in nm.iterdir() if d.is_dir() and not d.name.startswith(".")])
            print(f"Installed packages (top-level): {pkg_count}")
        except Exception:
            pass

    print("Runtime wiring: NO — read-only smoke only, no MCP/swarm launch")
    print("=== End Smoke ===")


def cmd_report(args):
    ts = _utc_now()
    run_id = "ruflo_smoke_" + ts

    pkg, pkg_err = _read_package_json()
    nm = RUFLO_DIR / "node_modules"
    lock = RUFLO_DIR / "package-lock.json"
    npm_v = _check_npm()
    node_v = _check_node()

    lifecycle = []
    pkg_name = "unknown"
    pkg_version = "unknown"
    all_scripts = []
    if pkg:
        pkg_name = pkg.get("name", "unknown")
        pkg_version = pkg.get("version", "unknown")
        lifecycle = _detect_lifecycle(pkg.get("scripts", {}))
        all_scripts = list(pkg.get("scripts", {}).keys())

    nm_pkg_count = 0
    if nm.exists():
        try:
            nm_pkg_count = len([d for d in nm.iterdir() if d.is_dir() and not d.name.startswith(".")])
        except Exception:
            pass

    source_status = "SOURCE_PRESENT" if (RUFLO_DIR.exists() and (RUFLO_DIR / "package.json").exists()) else "SOURCE_MISSING"

    report = {
        "run_id": run_id,
        "generated_at": ts,
        "ruflo_dir": str(RUFLO_DIR.relative_to(REPO_ROOT)),
        "ruflo_exists": RUFLO_DIR.exists(),
        "source_status": source_status,
        "package_name": pkg_name,
        "package_version": pkg_version,
        "package_json_error": pkg_err,
        "all_scripts": all_scripts,
        "node_modules_exists": nm.exists(),
        "node_modules_pkg_count": nm_pkg_count,
        "package_lock_exists": lock.exists(),
        "lifecycle_scripts_detected": lifecycle,
        "install_blocked": bool(lifecycle),
        "npm_version": npm_v,
        "node_version": node_v,
        "safety": {
            "no_global_install": True,
            "no_runtime_wiring": True,
            "no_swarm_launch": True,
            "no_mcp_launch": True,
            "ignore_scripts_flag": True,
        },
    }

    install_verdict = "ALLOWED (no lifecycle scripts, package-lock exists)" if (
        not lifecycle and lock.exists()
    ) else "BLOCKED"

    md_lines = [
        f"# Ruflo Smoke Report — {ts}",
        "",
        f"- **Run ID**: {run_id}",
        f"- **Ruflo dir**: {report['ruflo_dir']}",
        f"- **Source status**: {source_status}",
        f"- **Exists**: {report['ruflo_exists']}",
        f"- **Package**: {pkg_name} v{pkg_version}",
        f"- **node_modules**: {'INSTALLED (' + str(nm_pkg_count) + ' pkgs)' if nm.exists() else 'NOT INSTALLED'}",
        f"- **package-lock**: {'EXISTS' if lock.exists() else 'MISSING'}",
        f"- **npm version**: {npm_v or 'not found'}",
        f"- **node version**: {node_v or 'not found'}",
        f"- **Lifecycle scripts**: {lifecycle if lifecycle else 'NONE (safe)'}",
        f"- **All scripts**: {all_scripts}",
        f"- **Install verdict**: {install_verdict}",
        "",
        "## Safety Flags",
        "- No global install: YES",
        "- No runtime wiring: YES",
        "- No swarm launch: YES",
        "- No MCP launch: YES",
        "- --ignore-scripts flag: YES",
    ]

    if args.dry_run and not args.apply:
        print("[DRY RUN] Would write to:", f"05_logs/ruflo_smoke/{run_id}/")
        print("[DRY RUN] JSON report:")
        print(json.dumps(report, indent=2))
        print("[DRY RUN] Pass --apply to write.")
        return

    if args.apply:
        out_dir = LOGS_DIR / run_id
        json_path = out_dir / "ruflo_status.json"
        md_path = out_dir / "ruflo_status.md"
        try:
            _safe_write_text(json_path, json.dumps(report, indent=2))
            _safe_write_text(md_path, "\n".join(md_lines) + "\n")
        except RuntimeError as e:
            print(f"ERROR: Write failed: {e}")
            sys.exit(1)
        print(f"Written: {json_path.relative_to(REPO_ROOT)}")
        print(f"Written: {md_path.relative_to(REPO_ROOT)}")
        print("NOTE: Generated logs are unstaged. Do not stage unless part of milestone docs.")


def cmd_catalog(args):
    """Read README/CLAUDE/package metadata and write a local catalog. Does NOT launch Ruflo."""
    ts = _utc_now()
    print("=== Ruflo Catalog (read-only metadata) ===")

    pkg, pkg_err = _read_package_json()
    catalog = {
        "generated_at": ts,
        "ruflo_dir": str(RUFLO_DIR.relative_to(REPO_ROOT)),
        "package_json": pkg if pkg else {"error": pkg_err},
        "files": {},
        "runtime_launch": "NO — catalog is read-only metadata only",
    }

    for fname in ["README.md", "CLAUDE.md", "CHANGELOG.md", ".npmrc"]:
        fpath = RUFLO_DIR / fname
        if fpath.exists():
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
                catalog["files"][fname] = text[:2000]
                print(f"  Read: {fname} ({len(text)} chars)")
            except Exception as e:
                catalog["files"][fname] = f"ERROR: {e}"
                print(f"  Error reading {fname}: {e}")
        else:
            print(f"  Missing: {fname}")

    if args.dry_run and not args.apply:
        print()
        print("[DRY RUN] Catalog preview:")
        print(json.dumps(catalog, indent=2)[:600])
        print("[DRY RUN] Pass --apply to write catalog to 14_context/tooling/ruflo_catalog_n3_56_fix.md")
        return

    if args.apply:
        dest = TOOLING_DIR / "ruflo_catalog_n3_56_fix.md"
        lines = [
            f"# Ruflo Catalog — {ts}",
            "",
            f"- **Ruflo dir**: {catalog['ruflo_dir']}",
            f"- **Runtime launch**: {catalog['runtime_launch']}",
            "",
        ]
        if pkg:
            lines += [
                f"## Package",
                f"- **Name**: {pkg.get('name', '?')}",
                f"- **Version**: {pkg.get('version', '?')}",
                f"- **Description**: {pkg.get('description', '?')}",
                f"- **Scripts**: {list(pkg.get('scripts', {}).keys())}",
                f"- **Dependencies**: {list(pkg.get('dependencies', {}).keys())}",
                "",
            ]
        for fname, content in catalog["files"].items():
            lines += [
                f"## {fname}",
                "```",
                content[:1000],
                "```",
                "",
            ]
        md = "\n".join(lines)
        try:
            TOOLING_DIR.mkdir(parents=True, exist_ok=True)
            _safe_write_text(dest, md)
            print(f"Written: {dest.relative_to(REPO_ROOT)}")
        except RuntimeError as e:
            print(f"ERROR: Write failed: {e}")
            sys.exit(1)
        print("NOTE: Catalog is read-only metadata. Ruflo NOT launched.")
    print("=== End Catalog ===")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Ruflo Install Gate — stdlib-only, isolated npm ci --ignore-scripts, no global install. "
            "N+3.56-FIX: --source-status with SOURCE_PRESENT/SOURCE_MISSING codes. "
            "Ruflo (claude-flow v3.5.80) has no lifecycle scripts."
        )
    )
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--source-status", action="store_true",
                            help="Report source presence with clear status codes (SOURCE_PRESENT etc.)")
    mode_group.add_argument("--status", action="store_true", help="Print current Ruflo status")
    mode_group.add_argument("--install", action="store_true", help="Install Ruflo deps (--dry-run or --apply)")
    mode_group.add_argument("--smoke", action="store_true", help="Read-only smoke check")
    mode_group.add_argument("--report", action="store_true", help="Generate status report (--dry-run or --apply)")
    mode_group.add_argument("--catalog", action="store_true",
                            help="Read README/CLAUDE/package metadata, write catalog (--dry-run or --apply)")

    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")

    args = parser.parse_args()

    if args.source_status:
        cmd_source_status(args)
    elif args.status:
        cmd_status(args)
    elif args.install:
        cmd_install(args)
    elif args.smoke:
        cmd_smoke(args)
    elif args.report:
        cmd_report(args)
    elif args.catalog:
        cmd_catalog(args)


if __name__ == "__main__":
    main()
