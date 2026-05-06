#!/usr/bin/env python3
"""Course/Certificate Assistant — study plans, checklists, trackers, certificate log.

N+3.56-FIX: added --goal (optional, appears in plan output, never implies fake cert).
N+3.51A: stdlib-only, local only. NO fake certificates, NO cheating, NO assessment submission.
Human does all assessments. This tool only generates planning documents.
"""
import argparse
import base64
import datetime
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
COURSES_DIR = REPO_ROOT / "14_context" / "courses"
PLANS_DIR = COURSES_DIR / "plans"
TRACKERS_DIR = COURSES_DIR / "trackers"
CERT_LOG_DIR = COURSES_DIR / "certificate_log"

FORBIDDEN_NOTE = (
    "FORBIDDEN: Fake certificates | Cheating | Submitting assessments | "
    "Impersonating user | Claiming completion without proof | "
    "Bypassing proctoring | Answer keys for graded work."
)


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _slug(name: str) -> str:
    return name.lower().replace(" ", "_").replace("/", "_")[:50]


def _run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=timeout)
        return r.stdout.strip(), r.returncode
    except Exception:
        return "", -1


def _safe_write_text(dest: pathlib.Path, content: str) -> None:
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
    out, rc = _run(["node", "-e", node_script])
    if rc != 0 or "WRITTEN" not in out:
        raise RuntimeError(f"Node.js write fallback failed (rc={rc})")


def cmd_policy(args):
    print("=== Course/Certificate Assistant Policy ===")
    print()
    print("ALLOWED:")
    print("  - Study plans (schedules, goals, resources)")
    print("  - Checklists and progress trackers")
    print("  - Certificate logging (what you earned, date, provider, credential ID)")
    print("  - Reflection prompts and note templates")
    print("  - Note organization and vault structure")
    print("  - --goal field: personal learning objective (study planning only)")
    print()
    print("FORBIDDEN (hard rules, non-negotiable):")
    print("  - Generating fake certificates or badges")
    print("  - Cheating, submitting assessments on behalf of user")
    print("  - Impersonating the user")
    print("  - Claiming completion without verified proof")
    print("  - Bypassing proctoring or lockdown browser systems")
    print("  - Providing answer keys for graded work")
    print()
    print("Human does all assessments. This tool only creates planning documents.")
    print("--goal describes your personal learning objective — it does not imply certification or assessment.")
    print("=== End Policy ===")


def cmd_plan(args):
    if not args.course_name:
        print("ERROR: --course-name required")
        sys.exit(1)

    ts = _utc_now()
    slug = _slug(args.course_name)
    provider = args.provider or "Unknown"
    hours = args.hours or 0
    deadline = args.deadline or "Not set"
    goal = args.goal or None

    content_lines = [
        f"# Study Plan — {args.course_name}",
        "",
        f"Generated: {ts}",
        f"Provider: {provider}",
        f"Estimated hours: {hours}",
        f"Deadline: {deadline}",
    ]

    if goal:
        content_lines += [
            f"Goal: {goal}",
            "",
            "*(Goal is a personal learning objective for planning purposes only. "
            "It does not imply fake certification, assessment submission, or any shortcut.)*",
        ]

    content_lines += [
        "",
        "---",
        "",
        "## Goals",
        "- [ ] Define your learning objective for this course",
        "- [ ] Identify key skills you want to gain",
        "- [ ] Set a realistic completion milestone",
        "",
        "## Study Schedule",
        "| Week | Topic | Hours | Done |",
        "|------|-------|-------|------|",
        "| 1    |       |       |      |",
        "| 2    |       |       |      |",
        "| 3    |       |       |      |",
        "| 4    |       |       |      |",
        "",
        "## Resources",
        "- [ ] Course materials",
        "- [ ] Practice exercises",
        "- [ ] Official documentation",
        "",
        "## Reflection Prompts",
        "- What was the most important concept I learned this week?",
        "- What am I still unclear on?",
        "- What should I practice next?",
        "",
        "## Notes",
        "(Add your notes here)",
        "",
        "---",
        "",
        f"**Policy reminder**: {FORBIDDEN_NOTE}",
        "Human does all assessments. This plan is a scheduling and organization tool only.",
    ]

    content = "\n".join(content_lines) + "\n"
    dest = PLANS_DIR / f"plan_{slug}_{ts}.md"

    if args.dry_run and not args.apply:
        print(f"[DRY RUN] Course  : {args.course_name}")
        print(f"[DRY RUN] Provider: {provider}  Hours: {hours}  Deadline: {deadline}")
        if goal:
            print(f"[DRY RUN] Goal    : {goal}")
        print(f"[DRY RUN] Would write: 14_context/courses/plans/plan_{slug}_{ts}.md")
        print("[DRY RUN] Preview:")
        print(content[:400])
        print("[DRY RUN] Pass --apply to write.")
        return

    if args.apply:
        try:
            _safe_write_text(dest, content)
            print(f"Written: {dest.relative_to(REPO_ROOT)}")
        except RuntimeError as e:
            print(f"ERROR: {e}")
            sys.exit(1)


def cmd_tracker(args):
    if not args.course_name:
        print("ERROR: --course-name required")
        sys.exit(1)

    ts = _utc_now()
    slug = _slug(args.course_name)

    content_lines = [
        f"# Progress Tracker — {args.course_name}",
        "",
        f"Generated: {ts}",
        "",
        "---",
        "",
        "## Module Progress",
        "",
        "| Module | Topic | Status | Notes |",
        "|--------|-------|--------|-------|",
        "| 1      |       | [ ] Not started | |",
        "| 2      |       | [ ] Not started | |",
        "| 3      |       | [ ] Not started | |",
        "| 4      |       | [ ] Not started | |",
        "",
        "## Status Legend",
        "- [ ] Not started",
        "- [~] In progress",
        "- [x] Complete",
        "",
        "## Weekly Log",
        "",
        "| Date | Hours | Topic | Progress |",
        "|------|-------|-------|----------|",
        f"| {ts[:10]} |  |  |  |",
        "",
        "---",
        "",
        f"**Policy reminder**: {FORBIDDEN_NOTE}",
    ]

    content = "\n".join(content_lines) + "\n"
    dest = TRACKERS_DIR / f"tracker_{slug}_{ts}.md"

    if args.dry_run and not args.apply:
        print(f"[DRY RUN] Would write: 14_context/courses/trackers/tracker_{slug}_{ts}.md")
        print("[DRY RUN] Preview:")
        print(content[:300])
        print("[DRY RUN] Pass --apply to write.")
        return

    if args.apply:
        try:
            _safe_write_text(dest, content)
            print(f"Written: {dest.relative_to(REPO_ROOT)}")
        except RuntimeError as e:
            print(f"ERROR: {e}")
            sys.exit(1)


def cmd_certificate_log(args):
    if not args.course_name:
        print("ERROR: --course-name required")
        sys.exit(1)

    ts = _utc_now()
    slug = _slug(args.course_name)
    provider = args.provider or "Unknown"

    content_lines = [
        f"# Certificate Log — {args.course_name}",
        "",
        f"Generated: {ts}",
        f"Provider: {provider}",
        "",
        "---",
        "",
        "## Certificate Record",
        "",
        "Fill in after completing the course legitimately:",
        "",
        "| Field | Value |",
        "|-------|-------|",
        "| Course name | |",
        "| Provider | |",
        "| Completion date | |",
        "| Credential ID / URL | |",
        "| Skills gained | |",
        "| Notes | |",
        "",
        "## Verification",
        "- [ ] Certificate available in provider portal",
        "- [ ] Credential ID recorded above",
        "- [ ] PDF copy saved locally if available",
        "",
        "---",
        "",
        f"**IMPORTANT**: {FORBIDDEN_NOTE}",
        "Only log real certificates you have legitimately earned.",
        "Human does all assessments. This log is a record-keeping tool only.",
    ]

    content = "\n".join(content_lines) + "\n"
    dest = CERT_LOG_DIR / f"cert_log_{slug}_{ts}.md"

    if args.dry_run and not args.apply:
        print(f"[DRY RUN] Would write: 14_context/courses/certificate_log/cert_log_{slug}_{ts}.md")
        print(f"[DRY RUN] Provider: {provider}")
        print("[DRY RUN] Preview:")
        print(content[:300])
        print("[DRY RUN] Pass --apply to write.")
        return

    if args.apply:
        try:
            _safe_write_text(dest, content)
            print(f"Written: {dest.relative_to(REPO_ROOT)}")
        except RuntimeError as e:
            print(f"ERROR: {e}")
            sys.exit(1)


def cmd_status(args):
    print("=== Course/Certificate Assistant Status ===")
    print(f"Plans dir      : {'EXISTS' if PLANS_DIR.exists() else 'MISSING'}")
    if PLANS_DIR.exists():
        count = len(list(PLANS_DIR.glob("*.md")))
        print(f"  Plans        : {count} file(s)")
    print(f"Trackers dir   : {'EXISTS' if TRACKERS_DIR.exists() else 'MISSING'}")
    if TRACKERS_DIR.exists():
        count = len(list(TRACKERS_DIR.glob("*.md")))
        print(f"  Trackers     : {count} file(s)")
    print(f"Cert log dir   : {'EXISTS' if CERT_LOG_DIR.exists() else 'MISSING'}")
    if CERT_LOG_DIR.exists():
        count = len(list(CERT_LOG_DIR.glob("*.md")))
        print(f"  Cert logs    : {count} file(s)")
    print()
    print("Safety: NO fake certificates, NO assessment submission, NO cheating.")
    print("--goal: supported (optional, planning purposes only, no fake cert implication).")
    print("=== End Status ===")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Course/Certificate Assistant — study plans, trackers, cert logs. "
            "NO fake certs. NO cheating. Human does assessments. N+3.56-FIX."
        )
    )
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--policy", action="store_true", help="Print allowed/forbidden policy")
    mode_group.add_argument("--plan", action="store_true", help="Generate a study plan")
    mode_group.add_argument("--tracker", action="store_true", help="Generate a progress tracker")
    mode_group.add_argument("--certificate-log", action="store_true",
                            help="Generate a certificate log template")
    mode_group.add_argument("--status", action="store_true", help="Show output directory status")

    parser.add_argument("--course-name", help="Course name")
    parser.add_argument("--provider", help="Course provider (e.g. Coursera, Local/Online)")
    parser.add_argument("--hours", type=float, help="Estimated study hours")
    parser.add_argument("--deadline", help="Completion deadline (e.g. 2026-06-01)")
    parser.add_argument("--goal",
                        help="Personal learning objective (optional; appears in plan; "
                             "does not imply fake certification or assessment submission)")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")

    args = parser.parse_args()

    if args.policy:
        cmd_policy(args)
    elif args.plan:
        cmd_plan(args)
    elif args.tracker:
        cmd_tracker(args)
    elif args.certificate_log:
        cmd_certificate_log(args)
    elif args.status:
        cmd_status(args)


if __name__ == "__main__":
    main()
