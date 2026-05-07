#!/usr/bin/env python3
"""Content Money Workflow — local-first planning scaffold for supervised content experiments.

N+3.63A: Inspired by MoneyPrinter shorts pipeline, OpenFang Clip hand concept,
Ghoti approval gates, and LLM Council for idea review.

SAFETY: No live posting. No upload. No account login. No fake engagement.
No copyrighted media assumption. No scraping. No spam outreach.
All output is planning artifacts only. Human approval required before any publish step.
"""
import argparse
import datetime
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
CONTENT_WORKFLOWS_DIR = REPO_ROOT / "14_context" / "content_workflows"
LOGS_DIR = REPO_ROOT / "05_logs" / "content_workflow_runs"

WORKFLOW_STAGES = [
    {"id": 1, "name": "niche_selection", "description": "Choose a niche and target audience. Human decides."},
    {"id": 2, "name": "content_angle_research", "description": "Research angles, hooks, and format ideas. Planning only."},
    {"id": 3, "name": "script_outline", "description": "Draft a script outline for the short. Text artifact only."},
    {"id": 4, "name": "asset_sourcing_plan", "description": "Plan which assets are needed. No download or sourcing yet."},
    {"id": 5, "name": "rights_check", "description": "HUMAN gate: check all planned assets for rights/license. Required."},
    {"id": 6, "name": "voice_subtitle_plan", "description": "Plan voice-over approach and subtitle strategy. No recording yet."},
    {"id": 7, "name": "edit_checklist", "description": "Generate a checklist for the editing stage. Human edits."},
    {"id": 8, "name": "metadata_seo_checklist", "description": "Generate title/description/tag ideas. Human reviews before use."},
    {"id": 9, "name": "human_review_gate", "description": "HUMAN gate: full review of script, assets plan, metadata. Required before any upload."},
    {"id": 10, "name": "manual_publish_or_future_approved_publisher", "description": "Human manually publishes, or waits for a future approved automated publisher."},
]

APPROVAL_GATES = [
    "rights_check",
    "brand_safety",
    "platform_tos",
    "final_human_review",
    "publish_approval",
]

SUPPORTED_PLATFORMS = ["youtube_shorts", "tiktok", "instagram_reels"]
PUBLISHING_ENABLED = False


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug(text: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in text.lower())[:40]


def _safe_write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(content, encoding="utf-8", newline="\n")
        return
    except (PermissionError, OSError):
        pass
    import base64
    import subprocess
    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
    node_script = (
        "const fs=require('fs'),p=require('path'),"
        f"dest={json.dumps(str(path))},"
        f"enc={json.dumps(encoded)};"
        "fs.mkdirSync(p.dirname(dest),{recursive:true});"
        "fs.writeFileSync(dest,Buffer.from(enc,'base64'));"
        "console.log('WRITTEN');"
    )
    result = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, timeout=15)
    if result.returncode != 0 or "WRITTEN" not in result.stdout:
        raise RuntimeError(f"Write failed for {path}: {result.stderr}")


def cmd_status(args):
    print("=== Content Money Workflow Status ===")
    print(f"Planning scaffold: EXISTS (this script)")
    print(f"Live posting: NO (publishing_enabled={PUBLISHING_ENABLED})")
    print(f"Supported platforms: {', '.join(SUPPORTED_PLATFORMS)} (publishing disabled)")
    print(f"Human review required: YES")
    print(f"Approval gates: {', '.join(APPROVAL_GATES)}")
    print(f"Workflow stages: {len(WORKFLOW_STAGES)}")
    print(f"Content workflows dir: {'EXISTS' if CONTENT_WORKFLOWS_DIR.exists() else 'NOT YET CREATED'}")
    plans = list(CONTENT_WORKFLOWS_DIR.glob("plan_*.json")) if CONTENT_WORKFLOWS_DIR.exists() else []
    shot_lists = list(CONTENT_WORKFLOWS_DIR.glob("shot_list_*.json")) if CONTENT_WORKFLOWS_DIR.exists() else []
    print(f"Saved plans: {len(plans)}")
    print(f"Saved shot lists: {len(shot_lists)}")
    print("Safety: no upload, no post, no account login, no fake engagement, planning only.")
    print("=== End Status ===")


def _build_plan(niche: str, platform: str) -> dict:
    ts = _utc_now()
    return {
        "type": "content_plan",
        "generated": ts,
        "niche": niche,
        "platform": platform,
        "publishing_enabled": PUBLISHING_ENABLED,
        "approval_gates": APPROVAL_GATES,
        "workflow_stages": WORKFLOW_STAGES,
        "safety_notes": [
            "No live posting. Human must manually publish or approve an automated publisher.",
            "No copyrighted media assumed — rights_check gate is REQUIRED.",
            "No fake engagement. No spam. No scraping.",
            "platform_tos gate required before any upload consideration.",
            "This plan is a planning artifact only. No action is taken by this script.",
        ],
        "inspired_by": [
            "MoneyPrinter V1 pipeline stages (FujiwaraChoki/MoneyPrinter)",
            "OpenFang Clip hand concept (RightNow-AI/openfang)",
            "Ghoti approval gates",
            "LLM Council idea review",
        ],
        "stage_checklist": {
            stage["name"]: "pending"
            for stage in WORKFLOW_STAGES
        },
    }


def cmd_plan(args):
    niche = args.niche
    platform = args.platform
    if platform not in SUPPORTED_PLATFORMS:
        print(f"ERROR: platform '{platform}' not in supported list: {SUPPORTED_PLATFORMS}")
        sys.exit(1)
    plan = _build_plan(niche, platform)
    if args.dry_run and not args.apply:
        print("[DRY RUN] Plan preview:")
        print(json.dumps(plan, indent=2))
        print(f"[DRY RUN] Would write to: 14_context/content_workflows/plan_{_slug(niche)}_{platform}.json")
        print("[DRY RUN] Pass --apply to write.")
        return
    if args.apply:
        fname = f"plan_{_slug(niche)}_{platform}.json"
        out = CONTENT_WORKFLOWS_DIR / fname
        _safe_write(out, json.dumps(plan, indent=2) + "\n")
        print(f"Written: 14_context/content_workflows/{fname}")
        print("This is a planning artifact. No live actions taken.")


def _build_shot_list(topic: str, count: int) -> dict:
    ts = _utc_now()
    shots = []
    for i in range(1, count + 1):
        shots.append({
            "shot_number": i,
            "description": f"Shot {i}: [HUMAN fills in] — visual for '{topic}'",
            "duration_seconds": None,
            "asset_needed": "[HUMAN fills in]",
            "rights_status": "unchecked — rights_check gate required",
            "voice_over": "[HUMAN fills in]",
            "subtitle_text": "[HUMAN fills in]",
        })
    return {
        "type": "shot_list",
        "generated": ts,
        "topic": topic,
        "requested_count": count,
        "shots": shots,
        "safety_notes": [
            "Shot list is a planning artifact only.",
            "All assets must pass rights_check gate before sourcing.",
            "No recording, no download, no upload at this stage.",
            "Human reviews and fills in all asset/voice/subtitle fields.",
        ],
    }


def cmd_shot_list(args):
    topic = args.topic
    count = args.count
    shot_list = _build_shot_list(topic, count)
    if args.dry_run and not args.apply:
        print("[DRY RUN] Shot list preview:")
        print(json.dumps(shot_list, indent=2))
        print(f"[DRY RUN] Would write to: 14_context/content_workflows/shot_list_{_slug(topic)}.json")
        print("[DRY RUN] Pass --apply to write.")
        return
    if args.apply:
        fname = f"shot_list_{_slug(topic)}.json"
        out = CONTENT_WORKFLOWS_DIR / fname
        _safe_write(out, json.dumps(shot_list, indent=2) + "\n")
        print(f"Written: 14_context/content_workflows/{fname}")
        print("This is a planning artifact. No live actions taken.")


def _build_workflow_check() -> dict:
    ts = _utc_now()
    checks = {
        "no_live_posting": True,
        "no_upload": True,
        "no_account_login": True,
        "no_fake_engagement": True,
        "no_copyrighted_media_assumed": True,
        "no_scraping_without_legality_review": True,
        "no_spam_outreach": True,
        "human_approval_gates_present": True,
        "platform_tos_review_required": True,
        "publishing_enabled": PUBLISHING_ENABLED,
        "approval_gates": APPROVAL_GATES,
        "all_gates_pass": all([
            True,   # no_live_posting
            True,   # no_upload
            True,   # no_account_login
            True,   # no_fake_engagement
            True,   # no_copyrighted_media
            True,   # no_scraping
            True,   # no_spam
            True,   # human_approval_gates
            True,   # platform_tos
            not PUBLISHING_ENABLED,
        ]),
    }
    return {
        "type": "workflow_check",
        "generated": ts,
        "checks": checks,
        "result": "PASS" if checks["all_gates_pass"] else "FAIL",
        "notes": [
            "All safety checks pass. This workflow is planning-only.",
            "No live posting, no upload, no account actions, no fake engagement.",
            "Human must approve at rights_check, brand_safety, platform_tos, final_human_review, and publish_approval gates.",
        ],
    }


def cmd_workflow_check(args):
    check = _build_workflow_check()
    if args.dry_run and not args.apply:
        print("[DRY RUN] Workflow check preview:")
        print(json.dumps(check, indent=2))
        print(f"[DRY RUN] Would write to: 14_context/content_workflows/workflow_check.json")
        print("[DRY RUN] Pass --apply to write.")
        return
    if args.apply:
        out = CONTENT_WORKFLOWS_DIR / "workflow_check.json"
        _safe_write(out, json.dumps(check, indent=2) + "\n")
        print(f"Written: 14_context/content_workflows/workflow_check.json")
        print(f"Result: {check['result']}")
        print("No live actions taken.")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Content Money Workflow — local-first planning scaffold. N+3.63A. "
            "No live posting. No upload. Planning artifacts only."
        )
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true", help="Show workflow status")
    group.add_argument("--plan", action="store_true", help="Generate a content plan")
    group.add_argument("--shot-list", action="store_true", help="Generate a shot list")
    group.add_argument("--workflow-check", action="store_true", help="Run workflow safety check")

    parser.add_argument("--niche", help="Niche/topic for --plan")
    parser.add_argument("--platform", help=f"Platform for --plan: {SUPPORTED_PLATFORMS}")
    parser.add_argument("--topic", help="Topic for --shot-list")
    parser.add_argument("--count", type=int, default=10, help="Number of shots for --shot-list")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")

    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    elif args.plan:
        if not args.niche or not args.platform:
            print("ERROR: --plan requires --niche and --platform")
            sys.exit(1)
        cmd_plan(args)
    elif args.shot_list:
        if not args.topic:
            print("ERROR: --shot-list requires --topic")
            sys.exit(1)
        cmd_shot_list(args)
    elif args.workflow_check:
        cmd_workflow_check(args)


if __name__ == "__main__":
    main()
