#!/usr/bin/env python3
"""Rust Readiness Probe — N+3.58A: check whether Rust tools exist locally.

Decide whether Rust should be introduced now or later.
No install by default. No global changes. Stdlib only.
"""
import argparse
import datetime
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
TOOLING_DIR = REPO_ROOT / "14_context" / "tooling"
REPORT_PATH = TOOLING_DIR / "rust_readiness_n3_58.md"


def _run(cmd, timeout=5):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.returncode
    except FileNotFoundError:
        return "", 127
    except Exception:
        return "", -1


def _tracked_rust():
    try:
        r = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True,
            cwd=str(REPO_ROOT), timeout=10
        )
        files = r.stdout.splitlines()
        rs_files = [f for f in files if f.endswith(".rs")]
        cargo_files = [f for f in files if f.endswith("Cargo.toml") or f.endswith("Cargo.lock")]
        return rs_files, cargo_files
    except Exception:
        return [], []


def _collect():
    rustc_out, rustc_rc = _run(["rustc", "--version"])
    cargo_out, cargo_rc = _run(["cargo", "--version"])
    rustup_out, rustup_rc = _run(["rustup", "--version"])

    rustc_found = rustc_rc == 0
    cargo_found = cargo_rc == 0
    rustup_found = rustup_rc == 0

    rs_files, cargo_files = _tracked_rust()

    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "rust_toolchain": {
            "rustc": {"found": rustc_found, "version": rustc_out if rustc_found else None},
            "cargo": {"found": cargo_found, "version": cargo_out if cargo_found else None},
            "rustup": {"found": rustup_found, "version": rustup_out if rustup_found else None},
            "any_found": rustc_found or cargo_found or rustup_found,
            "fully_installed": rustc_found and cargo_found and rustup_found,
        },
        "tracked_rust": {
            "rs_files": rs_files,
            "rs_file_count": len(rs_files),
            "cargo_manifest_files": cargo_files,
            "rust_present_in_repo": len(rs_files) > 0 or len(cargo_files) > 0,
        },
        "recommendation": {
            "rewrite_now": False,
            "statement": "Do not rewrite Python/Node MVP into Rust yet.",
            "future_statement": "Introduce Rust later for stable runtime core only.",
            "good_uses": [
                "approval gate engine — fast, safe, auditable decision logic",
                "durable job runner — reliable task execution with crash recovery",
                "safe plugin/tool sandbox boundary — memory-safe isolation for tool calls",
                "file watcher/event loop — efficient OS-level event monitoring",
                "future desktop/operator daemon — lightweight background service",
            ],
            "do_not_do": [
                "do not rewrite ghoti_dashboard.py in Rust",
                "do not rewrite Python operators in Rust yet",
                "do not add unused Rust crate just to affect GitHub language stats",
                "do not introduce Rust before the Python MVP is stable",
            ],
        },
        "install_instructions_doc_only": {
            "note": "These are documentation-only. Do not execute without operator approval.",
            "winget": "winget install Rustlang.Rustup",
            "set_default": "rustup default stable",
            "verify_rustc": "rustc --version",
            "verify_cargo": "cargo --version",
        },
    }


def cmd_status(args):
    s = _collect()
    tc = s["rust_toolchain"]
    tr = s["tracked_rust"]
    rec = s["recommendation"]
    print("=== Rust Readiness Probe — Status ===")
    print(f"rustc  : {'FOUND — ' + tc['rustc']['version'] if tc['rustc']['found'] else 'NOT FOUND'}")
    print(f"cargo  : {'FOUND — ' + tc['cargo']['version'] if tc['cargo']['found'] else 'NOT FOUND'}")
    print(f"rustup : {'FOUND — ' + tc['rustup']['version'] if tc['rustup']['found'] else 'NOT FOUND'}")
    install_label = "YES (fully)" if tc["fully_installed"] else ("PARTIAL" if tc["any_found"] else "NO")
    print(f"Rust installed: {install_label}")
    rs_label = "NONE" if tr["rs_file_count"] == 0 else str(tr["rs_file_count"])
    cargo_label = "NONE" if not tr["cargo_manifest_files"] else str(tr["cargo_manifest_files"])
    print(f"Tracked .rs files   : {rs_label}")
    print(f"Tracked Cargo files : {cargo_label}")
    print(f"Rust present in repo: {'YES' if tr['rust_present_in_repo'] else 'NO'}")
    print("")
    print(f"Recommendation: {rec['statement']}")
    print(f"Future:         {rec['future_statement']}")
    print("=== End Status ===")


def cmd_json(args):
    s = _collect()
    print(json.dumps(s, indent=2))


def cmd_bootstrap_plan(args):
    s = _collect()
    tc = s["rust_toolchain"]
    tr = s["tracked_rust"]
    rec = s["recommendation"]

    rust_label = "NONE" if tr["rs_file_count"] == 0 else str(tr["rs_file_count"])
    cargo_label = tr["cargo_manifest_files"] or "NONE"
    good_uses = "\n".join(f"- {u}" for u in rec["good_uses"])
    do_not = "\n".join(f"- {u}" for u in rec["do_not_do"])

    report = f"""# Rust Readiness Probe — N+3.58A

Generated: {s['generated_at']}

## Current Rust Toolchain Status

| Tool   | Status | Version |
|--------|--------|---------|
| rustc  | {'FOUND' if tc['rustc']['found'] else 'NOT FOUND'} | {tc['rustc']['version'] or 'N/A'} |
| cargo  | {'FOUND' if tc['cargo']['found'] else 'NOT FOUND'} | {tc['cargo']['version'] or 'N/A'} |
| rustup | {'FOUND' if tc['rustup']['found'] else 'NOT FOUND'} | {tc['rustup']['version'] or 'N/A'} |

Fully installed: {'YES' if tc['fully_installed'] else 'NO'}

## Tracked Rust Code in Ghoti

Tracked .rs files: **{rust_label}**
Tracked Cargo manifest files: {cargo_label}

## Recommendation

**{rec['statement']}**
**{rec['future_statement']}**

## What Rust Is Good For in Ghoti (Future Use)

{good_uses}

## What NOT To Do

{do_not}

## Optional Future Install (Documentation Only — Do Not Execute Without Operator Approval)

```powershell
winget install Rustlang.Rustup
rustup default stable
rustc --version
cargo --version
```

## Current Runtime Stack (Truthful)

- Python — primary orchestration and scripts
- Node.js / JavaScript — dashboard MVP
- PowerShell — Windows operator scripts
- Rust — NOT present; future stable-core option only
"""

    if args.dry_run and not args.apply:
        print("[DRY RUN] Bootstrap plan preview:")
        print(report)
        print(f"[DRY RUN] Would write to: {REPORT_PATH.relative_to(REPO_ROOT)}")
        print("[DRY RUN] Pass --apply to write.")
        return
    if args.apply:
        TOOLING_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(report, encoding="utf-8")
        print(f"Written: {REPORT_PATH.relative_to(REPO_ROOT)}")


def main():
    parser = argparse.ArgumentParser(
        description="Rust Readiness Probe — N+3.58A. No install by default. Stdlib only."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true", help="Print Rust toolchain and repo status")
    group.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    group.add_argument("--bootstrap-plan", action="store_true", help="Generate bootstrap plan report")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    elif args.json:
        cmd_json(args)
    elif args.bootstrap_plan:
        cmd_bootstrap_plan(args)


if __name__ == "__main__":
    main()
