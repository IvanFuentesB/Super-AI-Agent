#!/usr/bin/env python3
"""Obsidian Probe — unified Obsidian vault and app detection. stdlib-only, read-only.

N+3.58-FIX: hardened against PermissionError/OSError on Windows path candidates.
N+3.56-FIX: created as single source of truth for Obsidian status used by helper + dashboard.
No network calls. No writes. No app launch unless -Open is explicitly requested elsewhere.
"""
import argparse
import json
import os
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
VAULT_DIR = REPO_ROOT / "14_context" / "obsidian_vault"
REQUIRED_VAULT_FILES = [
    "00_Index.md",
    "01_Current_State.md",
    "02_Next_Actions.md",
    "09_Migration_Handoff.md",
]

OBSIDIAN_EXE_CANDIDATES = [
    pathlib.Path(r"C:\Users\Navif\AppData\Local\Programs\Obsidian\Obsidian.exe"),
    pathlib.Path(r"C:\Users\ai_sandbox\AppData\Local\Programs\Obsidian\Obsidian.exe"),
    pathlib.Path(r"C:\Users\ai_sandbox\AppData\Local\Obsidian\Obsidian.exe"),
    pathlib.Path(r"C:\Program Files\Obsidian\Obsidian.exe"),
]


def safe_exists(path) -> bool:
    try:
        return path.exists()
    except (PermissionError, OSError, FileNotFoundError):
        return False


def safe_is_file(path) -> bool:
    try:
        return path.is_file()
    except (PermissionError, OSError, FileNotFoundError):
        return False


def safe_glob_md(path) -> list:
    try:
        return list(path.glob("*.md"))
    except (PermissionError, OSError, FileNotFoundError):
        return []


def safe_stat(path):
    try:
        return path.stat()
    except (PermissionError, OSError, FileNotFoundError):
        return None


def safe_check_candidate(path) -> dict:
    try:
        exists = path.exists()
        return {"path": str(path), "exists": exists, "accessible": True, "error": None}
    except PermissionError as e:
        return {"path": str(path), "exists": False, "accessible": False, "error": f"PermissionError: {e}"}
    except OSError as e:
        return {"path": str(path), "exists": False, "accessible": False, "error": f"OSError: {e}"}
    except Exception as e:
        return {"path": str(path), "exists": False, "accessible": False, "error": str(e)}


def _env_candidates():
    local_app = os.environ.get("LOCALAPPDATA", "")
    if not local_app:
        return []
    return [
        pathlib.Path(local_app) / "Programs" / "Obsidian" / "Obsidian.exe",
        pathlib.Path(local_app) / "Obsidian" / "Obsidian.exe",
    ]


def _all_exe_candidates():
    seen = set()
    result = []
    for c in OBSIDIAN_EXE_CANDIDATES + _env_candidates():
        key = str(c).lower()
        if key not in seen:
            seen.add(key)
            result.append(c)
    return result


def _run(cmd, timeout=8):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except Exception as e:
        return "", str(e), -1


def _check_winget():
    out, _, rc = _run(["winget", "--version"])
    if rc != 0:
        return False, None
    out2, _, rc2 = _run(["winget", "list", "--id", "Obsidian.Obsidian", "--exact"])
    if rc2 == 0 and "Obsidian" in out2:
        return True, out2.strip()
    return False, None


def probe() -> dict:
    probe_errors = []

    vault_exists = safe_exists(VAULT_DIR)
    vault_md_count = len(safe_glob_md(VAULT_DIR)) if vault_exists else 0

    required_files = {}
    for fname in REQUIRED_VAULT_FILES:
        fp = VAULT_DIR / fname
        required_files[fname] = safe_exists(fp)
    required_pass = all(required_files.values())

    exe_found = None
    exe_checked = []
    inaccessible_candidates = []
    for c in _all_exe_candidates():
        result = safe_check_candidate(c)
        exe_checked.append(result)
        if not result["accessible"]:
            inaccessible_candidates.append(result)
            probe_errors.append(
                f"Candidate inaccessible: {result['path']}: {result['error']}"
            )
        elif result["exists"] and exe_found is None:
            exe_found = str(c)

    winget_obsidian_found, winget_detail = _check_winget()

    return {
        "vault": {
            "path": str(VAULT_DIR.relative_to(REPO_ROOT)),
            "exists": vault_exists,
            "md_file_count": vault_md_count,
            "required_files": required_files,
            "required_files_pass": required_pass,
        },
        "app": {
            "exe_found": exe_found is not None,
            "exe_path": exe_found,
            "exe_candidates_checked": exe_checked,
            "inaccessible_candidates": inaccessible_candidates,
            "winget_found": winget_obsidian_found,
            "winget_detail": winget_detail,
        },
        "probe_errors": probe_errors,
    }


def cmd_status(args):
    result = probe()
    v = result["vault"]
    a = result["app"]
    errors = result.get("probe_errors", [])

    print("=== Obsidian Probe Status ===")
    print(f"Vault path     : {v['path']}")
    print(f"Vault exists   : {'YES' if v['exists'] else 'NO'}")
    print(f"Vault .md files: {v['md_file_count']}")
    print()
    print("Required vault files:")
    for fname, present in v["required_files"].items():
        print(f"  {'OK' if present else 'MISSING'}: {fname}")
    print(f"Required files pass: {'YES' if v['required_files_pass'] else 'NO'}")
    print()
    print("Obsidian app:")
    print(f"  Executable found  : {'YES — ' + a['exe_path'] if a['exe_found'] else 'NO'}")
    print(f"  Winget installed  : {'YES' if a['winget_found'] else 'NO'}")
    if not a["exe_found"]:
        print("  Candidates checked:")
        for c in a["exe_candidates_checked"]:
            if not c["accessible"]:
                label = "INACCESSIBLE"
            elif c["exists"]:
                label = "FOUND"
            else:
                label = "not found"
            print(f"    {label}: {c['path']}")
    if a.get("inaccessible_candidates"):
        print(
            f"\n  WARNING: {len(a['inaccessible_candidates'])} candidate path(s) "
            "were inaccessible (PermissionError/OSError)."
        )
        for ic in a["inaccessible_candidates"]:
            print(f"    {ic['path']}: {ic['error']}")
    if errors:
        print(f"\nProbe warnings ({len(errors)}):")
        for e in errors:
            print(f"  WARNING: {e}")
    print("=== End Obsidian Probe ===")


def cmd_json(args):
    result = probe()
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Obsidian Probe — unified vault and app detection. "
            "Read-only. No launch. No writes. N+3.58-FIX."
        )
    )
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--status", action="store_true", help="Print human-readable Obsidian status"
    )
    mode_group.add_argument("--json", action="store_true", help="Print JSON status")

    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    elif args.json:
        cmd_json(args)


if __name__ == "__main__":
    main()
