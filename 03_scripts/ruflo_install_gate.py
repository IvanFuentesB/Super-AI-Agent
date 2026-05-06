#!/usr/bin/env python3
"""Ruflo Install Gate — stdlib-only, isolated npm ci, no global install, no runtime wiring."""
import argparse
import datetime
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
RUFLO_DIR = REPO_ROOT / "21_repos" / "third_party" / "evals" / "ruflo"
LOGS_DIR = REPO_ROOT / "05_logs" / "ruflo_smoke"

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


def cmd_status(args):
    print("=== Ruflo Install Gate Status ===")
    print(f"Repo root  : {REPO_ROOT}")
    print(f"Ruflo dir  : {RUFLO_DIR}")
    print(f"Exists     : {'YES' if RUFLO_DIR.exists() else 'NO'}")

    pkg, err = _read_package_json()
    if err:
        print(f"Package    : ERROR — {err}")
    else:
        print(f"Package    : {pkg.get('name', '?')} v{pkg.get('version', '?')}")
        scripts = pkg.get("scripts", {})
        lifecycle = _detect_lifecycle(scripts)
        print(f"Lifecycle scripts detected: {lifecycle if lifecycle else 'NONE (safe)'}")

    nm = RUFLO_DIR / "node_modules"
    lock = RUFLO_DIR / "package-lock.json"
    print(f"node_modules   : {'INSTALLED' if nm.exists() else 'NOT INSTALLED'}")
    print(f"package-lock   : {'EXISTS' if lock.exists() else 'MISSING'}")

    npm_v, _, rc = _run(["npm", "--version"])
    print(f"npm version    : {npm_v if rc == 0 else 'not found'}")
    print("=== End Status ===")


def cmd_install(args):
    pkg, err = _read_package_json()
    if err:
        print(f"ERROR: {err}")
        sys.exit(1)

    scripts = pkg.get("scripts", {})
    lifecycle = _detect_lifecycle(scripts)
    if lifecycle:
        print(f"BLOCKED: Lifecycle scripts detected: {lifecycle}")
        print("Install is blocked until an explicit override is added.")
        print("Do not add override in this version.")
        sys.exit(1)

    lock = RUFLO_DIR / "package-lock.json"
    cmd = ["npm", "ci", "--ignore-scripts"]

    if args.dry_run and not args.apply:
        print("[DRY RUN] Would run inside:", RUFLO_DIR)
        print("[DRY RUN] Command:", " ".join(cmd))
        print("[DRY RUN] No lifecycle scripts — safe to install.")
        print("[DRY RUN] Pass --apply to execute.")
        return

    if args.apply:
        if not lock.exists():
            print("WARNING: package-lock.json missing — npm ci requires it.")
            sys.exit(1)
        print(f"Running: {' '.join(cmd)}")
        print(f"Working dir: {RUFLO_DIR}")
        out, err_txt, rc = _run(cmd, cwd=RUFLO_DIR, timeout=120)
        if out:
            print(out)
        if err_txt:
            print("[stderr]", err_txt)
        if rc == 0:
            print("Install: COMPLETE")
        else:
            print(f"Install: FAILED (exit {rc})")
            sys.exit(1)


def cmd_smoke(args):
    print("=== Ruflo Smoke Check (read-only) ===")
    pkg, err = _read_package_json()
    if err:
        print(f"package.json: ERROR — {err}")
    else:
        print(f"Package: {pkg.get('name', '?')} v{pkg.get('version', '?')}")
        scripts = pkg.get("scripts", {})
        lifecycle = _detect_lifecycle(scripts)
        print(f"Lifecycle scripts: {lifecycle if lifecycle else 'NONE'}")
        print(f"All scripts: {list(scripts.keys())}")

    nm = RUFLO_DIR / "node_modules"
    lock = RUFLO_DIR / "package-lock.json"
    print(f"node_modules exists: {'YES' if nm.exists() else 'NO'}")
    print(f"package-lock exists: {'YES' if lock.exists() else 'NO'}")

    npm_v, _, rc = _run(["npm", "--version"])
    print(f"npm --version: {npm_v if rc == 0 else 'not found / error'}")
    print("=== End Smoke ===")


def cmd_report(args):
    ts = _utc_now()
    run_id = "ruflo_smoke_" + ts

    pkg, pkg_err = _read_package_json()
    nm = RUFLO_DIR / "node_modules"
    lock = RUFLO_DIR / "package-lock.json"
    npm_v, _, npm_rc = _run(["npm", "--version"])

    lifecycle = []
    pkg_name = "unknown"
    pkg_version = "unknown"
    if pkg:
        pkg_name = pkg.get("name", "unknown")
        pkg_version = pkg.get("version", "unknown")
        lifecycle = _detect_lifecycle(pkg.get("scripts", {}))

    report = {
        "run_id": run_id,
        "generated_at": ts,
        "ruflo_dir": str(RUFLO_DIR.relative_to(REPO_ROOT)),
        "ruflo_exists": RUFLO_DIR.exists(),
        "package_name": pkg_name,
        "package_version": pkg_version,
        "package_json_error": pkg_err,
        "node_modules_exists": nm.exists(),
        "package_lock_exists": lock.exists(),
        "lifecycle_scripts_detected": lifecycle,
        "install_blocked": bool(lifecycle),
        "npm_version": npm_v if npm_rc == 0 else None,
        "safety": {
            "no_global_install": True,
            "no_runtime_wiring": True,
            "no_swarm_launch": True,
            "ignore_scripts_flag": True,
        },
    }

    md_lines = [
        f"# Ruflo Smoke Report — {ts}",
        "",
        f"- **Run ID**: {run_id}",
        f"- **Ruflo dir**: {report['ruflo_dir']}",
        f"- **Exists**: {report['ruflo_exists']}",
        f"- **Package**: {pkg_name} v{pkg_version}",
        f"- **node_modules**: {'INSTALLED' if nm.exists() else 'NOT INSTALLED'}",
        f"- **package-lock**: {'EXISTS' if lock.exists() else 'MISSING'}",
        f"- **npm version**: {report['npm_version'] or 'not found'}",
        f"- **Lifecycle scripts**: {lifecycle if lifecycle else 'NONE (safe)'}",
        f"- **Install blocked**: {report['install_blocked']}",
        "",
        "## Safety Flags",
        "- No global install: YES",
        "- No runtime wiring: YES",
        "- No swarm launch: YES",
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
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / "ruflo_status.json"
        md_path = out_dir / "ruflo_status.md"
        json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
        print(f"Written: {json_path.relative_to(REPO_ROOT)}")
        print(f"Written: {md_path.relative_to(REPO_ROOT)}")
        print("NOTE: Generated logs are unstaged. Do not stage unless explicitly part of milestone docs.")


def main():
    parser = argparse.ArgumentParser(
        description="Ruflo Install Gate — stdlib-only, isolated npm ci --ignore-scripts, no global install."
    )
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--status", action="store_true", help="Print current Ruflo status")
    mode_group.add_argument("--install", action="store_true", help="Install Ruflo deps (--dry-run or --apply)")
    mode_group.add_argument("--smoke", action="store_true", help="Read-only smoke check")
    mode_group.add_argument("--report", action="store_true", help="Generate status report (--dry-run or --apply)")

    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")

    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    elif args.install:
        cmd_install(args)
    elif args.smoke:
        cmd_smoke(args)
    elif args.report:
        cmd_report(args)


if __name__ == "__main__":
    main()
