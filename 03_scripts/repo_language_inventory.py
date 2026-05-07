#!/usr/bin/env python3
"""Repo Language Inventory — N+3.58A: truthfully inspect tracked repo language files.

Explains why GitHub/UI might show Java/Rust when none is tracked.
No external APIs. No network. Stdlib only.
"""
import argparse
import datetime
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
TOOLING_DIR = REPO_ROOT / "14_context" / "tooling"
REPORT_PATH = TOOLING_DIR / "repo_language_inventory_n3_58.md"

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "05_logs", "output"}

LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".java": "Java",
    ".rs": "Rust",
    ".go": "Go",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".c": "C",
    ".sh": "Shell",
    ".ps1": "PowerShell",
    ".psm1": "PowerShell",
    ".psd1": "PowerShell",
    ".md": "Markdown",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".html": "HTML",
    ".css": "CSS",
}

GITHUB_LANGUAGE_EXPLANATION = (
    "GitHub detects repository language from ALL files in the repository tree, "
    "including untracked files, third-party content in subdirectories, "
    "generated output, and workspace files outside .gitignore. "
    "It also caches language stats and may display stale data after files are removed. "
    "The 'git ls-files' command shows only tracked files; GitHub counts more. "
    "If GitHub shows Java but 'git ls-files' shows none, "
    "the Java files are likely: untracked, in 21_repos/third_party/, "
    "in .gitignore'd output folders, or a stale GitHub language cache."
)


def _run_git(args, cwd=None):
    try:
        r = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True,
            cwd=str(cwd or REPO_ROOT), timeout=10
        )
        return r.stdout.strip(), r.returncode
    except Exception:
        return "", -1


def _tracked_files():
    out, rc = _run_git(["ls-files"])
    if rc != 0 or not out:
        return []
    return [REPO_ROOT / p for p in out.splitlines() if p.strip()]


def _count_by_extension(files):
    counts = {}
    for f in files:
        ext = f.suffix.lower()
        lang = LANGUAGE_EXTENSIONS.get(ext, ext if ext else "(no ext)")
        counts[lang] = counts.get(lang, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def _files_by_ext(files, ext):
    return [f for f in files if f.suffix.lower() == ext]


def _collect_status(include_untracked=False):
    branch, _ = _run_git(["branch", "--show-current"])
    head, _ = _run_git(["rev-parse", "--short", "HEAD"])
    tracked = _tracked_files()
    java_files = _files_by_ext(tracked, ".java")
    rust_files = _files_by_ext(tracked, ".rs")
    cargo_manifests = [f for f in tracked if f.name in ("Cargo.toml", "Cargo.lock")]
    java_build = [f for f in tracked if f.name in ("pom.xml", "build.gradle")]
    lang_counts = _count_by_extension(tracked)

    untracked_java = []
    untracked_rust = []
    if include_untracked:
        for p in REPO_ROOT.rglob("*"):
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            if not p.is_file():
                continue
            if p.suffix.lower() == ".java":
                untracked_java.append(str(p.relative_to(REPO_ROOT)))
            elif p.suffix.lower() == ".rs" or p.name in ("Cargo.toml", "Cargo.lock"):
                untracked_rust.append(str(p.relative_to(REPO_ROOT)))
            if len(untracked_java) + len(untracked_rust) > 200:
                break

    return {
        "branch": branch or "unknown",
        "head": head or "unknown",
        "tracked_file_count": len(tracked),
        "tracked_java": len(java_files),
        "tracked_java_files": [str(f.relative_to(REPO_ROOT)) for f in java_files],
        "tracked_rust": len(rust_files),
        "tracked_rust_files": [str(f.relative_to(REPO_ROOT)) for f in rust_files],
        "tracked_java_build_files": [str(f.relative_to(REPO_ROOT)) for f in java_build],
        "tracked_rust_manifest_files": [str(f.relative_to(REPO_ROOT)) for f in cargo_manifests],
        "language_summary": lang_counts,
        "github_language_explanation": GITHUB_LANGUAGE_EXPLANATION,
        "include_untracked": include_untracked,
        "untracked_java_sample": untracked_java[:20] if include_untracked else None,
        "untracked_rust_sample": untracked_rust[:20] if include_untracked else None,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
    }


def cmd_status(args):
    include_untracked = getattr(args, "include_untracked", False)
    s = _collect_status(include_untracked=include_untracked)
    print("=== Repo Language Inventory — Status ===")
    print(f"Branch      : {s['branch']}")
    print(f"HEAD        : {s['head']}")
    print(f"Tracked     : {s['tracked_file_count']} files")
    java_label = "NONE" if s["tracked_java"] == 0 else str(s["tracked_java"])
    rust_label = "NONE" if s["tracked_rust"] == 0 else str(s["tracked_rust"])
    print(f"Tracked Java: {java_label}")
    print(f"Tracked Rust: {rust_label}")
    cargo_label = "NONE" if not s["tracked_rust_manifest_files"] else str(s["tracked_rust_manifest_files"])
    build_label = "NONE" if not s["tracked_java_build_files"] else str(s["tracked_java_build_files"])
    print(f"Tracked Cargo.toml/lock : {cargo_label}")
    print(f"Tracked pom.xml/gradle  : {build_label}")
    print("")
    print("Language summary (tracked files by extension):")
    for lang, count in s["language_summary"].items():
        print(f"  {lang:<20s} {count}")
    print("")
    print("GitHub language explanation:")
    print(f"  {GITHUB_LANGUAGE_EXPLANATION}")
    if include_untracked:
        print(f"\nUntracked Java sample ({len(s['untracked_java_sample'])} found, capped at 20):")
        for f in s["untracked_java_sample"]:
            print(f"  {f}")
        print(f"Untracked Rust/Cargo sample ({len(s['untracked_rust_sample'])} found, capped at 20):")
        for f in s["untracked_rust_sample"]:
            print(f"  {f}")
    print("=== End Status ===")


def cmd_json(args):
    include_untracked = getattr(args, "include_untracked", False)
    s = _collect_status(include_untracked=include_untracked)
    print(json.dumps(s, indent=2))


def cmd_report(args):
    s = _collect_status()
    java_label = "NONE" if s["tracked_java"] == 0 else str(s["tracked_java"])
    rust_label = "NONE" if s["tracked_rust"] == 0 else str(s["tracked_rust"])
    cargo_label = s["tracked_rust_manifest_files"] or "NONE"
    build_label = s["tracked_java_build_files"] or "NONE"
    lang_rows = "\n".join(
        f"| {lang} | {count} |"
        for lang, count in s["language_summary"].items()
    )
    report = f"""# Repo Language Inventory — N+3.58A

Generated: {s['generated_at']}
Branch: `{s['branch']}` | HEAD: `{s['head']}`

## Tracked Language Summary

| Language | Tracked Files |
|----------|--------------|
{lang_rows}

## Java Truth

Tracked Java: **{java_label}**
Tracked Java build files (pom.xml/build.gradle): {build_label}

## Rust Truth

Tracked Rust: **{rust_label}**
Tracked Rust manifest files (Cargo.toml/Cargo.lock): {cargo_label}

## Why GitHub May Show Java or Rust

{GITHUB_LANGUAGE_EXPLANATION}

Likely causes in this repo:
- `21_repos/third_party/` may contain reference intake repos with Java/Rust content (read-only, not owned).
- Untracked output folders, generated files, or workspace-only content.
- Stale GitHub language cache after files were removed from tracking.

## Runtime Stack (Current — Truthful)

- **Python** — primary runtime scripts, CLI, orchestration
- **Node.js / JavaScript** — dashboard MVP server, frontend
- **PowerShell** — Windows operator scripts
- **Rust** — NOT present. Planned for future stable-core use only.
- **Java** — NOT present. No Java tracked or planned.

## Conclusion

The Ghoti repo does not use Java or Rust in its tracked codebase.
Any GitHub UI showing Java reflects external/untracked content or a stale language cache.
"""
    if args.dry_run and not args.apply:
        print("[DRY RUN] Report preview:")
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
        description="Repo Language Inventory — N+3.58A. Truthfully inspect tracked repo language files."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true", help="Print current language status")
    group.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    group.add_argument("--report", action="store_true", help="Generate markdown report")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--include-untracked", action="store_true",
                        help="Also scan untracked files (skips .git, node_modules, .venv, etc.)")
    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    elif args.json:
        cmd_json(args)
    elif args.report:
        cmd_report(args)


if __name__ == "__main__":
    main()
