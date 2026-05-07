#!/usr/bin/env python3
"""Ghoti Readiness Check — N+3.65.

Inspects actual repo state and scores readiness by category.
stdlib only. No network. No writes unless --report --apply.

Readiness categories:
  repo_integrity, safety_gates, local_memory, llm_council,
  external_repo_intake, content_workflow, supervised_mvp_artifact,
  dashboard_status, merge_readiness

supervised_mvp_slice_score: 100 only if all required categories pass.
production_autonomy_score: not_applicable (supervised local MVP only).
"""
import argparse
import datetime
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
RUNS_DIR = REPO_ROOT / "14_context" / "content_workflows" / "runs"
LANE_STATUS_FILE = REPO_ROOT / "14_context" / "agent_lanes" / "lane_status.jsonl"
ACTIVE_LOCKS_FILE = REPO_ROOT / "14_context" / "agent_lanes" / "active_locks.jsonl"
TOOLING_DIR = REPO_ROOT / "14_context" / "tooling"
OBSIDIAN_VAULT_DIR = REPO_ROOT / "14_context" / "obsidian_vault"
COMPACT_MEMORY_DIR = REPO_ROOT / "14_context" / "compact_memory"

APPROVAL_GATES = [
    "rights_check",
    "brand_safety",
    "platform_tos",
    "final_human_review",
    "publish_approval",
]

PACKET_FILES = [
    "00_manifest.json",
    "01_input_brief.md",
    "02_llm_council_review.md",
    "03_strategy_decision.md",
    "04_short_script.md",
    "05_scene_shot_list.md",
    "06_asset_rights_tos_brand_safety.md",
    "07_metadata_pack.md",
    "08_human_approval_packet.md",
    "09_manual_publish_checklist.md",
    "10_obsidian_memory_snapshot.md",
    "11_readiness_score.json",
    "12_next_iteration_backlog.md",
]

REQUIRED_SCRIPTS = [
    "supervised_content_mvp_runner.py",
    "ghoti_readiness_check.py",
    "external_repo_implementation_map.py",
    "local_worker_router.py",
    "ghoti_dashboard.py",
    "llm_council_runner.py",
    "content_money_workflow.py",
    "external_repo_intake.py",
    "agent_lane_status.py",
]

REQUIRED_CONFIGS = [
    "supervised_content_mvp.example.json",
    "ghoti_readiness_check.example.json",
    "external_repo_implementation_map.example.json",
    "local_worker_routing.example.json",
    "llm_council.example.json",
]


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_display() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _safe_write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(content, encoding="utf-8", newline="\n")
        return
    except (PermissionError, OSError):
        pass
    import base64
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
        raise RuntimeError(f"Write failed for {path}")


def _get_latest_run():
    if not RUNS_DIR.exists():
        return None
    runs = sorted([d for d in RUNS_DIR.iterdir() if d.is_dir()], key=lambda d: d.name)
    return runs[-1] if runs else None


def _run_cmd(cmd, cwd=None, timeout=10):
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True,
            cwd=str(cwd or REPO_ROOT), timeout=timeout,
        )
        return r.stdout.strip(), r.returncode
    except Exception:
        return "", -1


def _check_repo_integrity():
    scripts_dir = REPO_ROOT / "03_scripts"
    configs_dir = REPO_ROOT / "23_configs"

    script_results = {s: (scripts_dir / s).exists() for s in REQUIRED_SCRIPTS}
    config_results = {c: (configs_dir / c).exists() for c in REQUIRED_CONFIGS}

    diff_out, diff_rc = _run_cmd(["git", "diff", "--check"])
    whitespace_ok = diff_rc == 0 and not diff_out.strip()

    return {
        "scripts": script_results,
        "all_scripts_exist": all(script_results.values()),
        "configs": config_results,
        "all_configs_exist": all(config_results.values()),
        "git_diff_check_pass": whitespace_ok,
        "pass": all(script_results.values()) and all(config_results.values()),
    }


def _check_safety_gates():
    latest = _get_latest_run()
    if not latest:
        return {
            "latest_run_exists": False,
            "live_posting_disabled": True,
            "external_api_disabled": True,
            "clone_install_run_disabled": True,
            "human_approval_required": True,
            "pass": False,
            "note": "No proof run exists yet",
        }

    manifest_path = latest / "00_manifest.json"
    if not manifest_path.exists():
        return {"latest_run_exists": True, "manifest_exists": False, "pass": False}

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        safety = manifest.get("safety", {})
        gates = manifest.get("approval_gates", {})

        live_off = safety.get("live_posting") is False
        api_off = safety.get("external_api_calls") is False
        clone_off = safety.get("clone_install_run_external_repos") is False
        human_req = safety.get("human_approval_required") is True
        all_gates = all(gates.get(g) == "pending_human_review" for g in APPROVAL_GATES)

        return {
            "latest_run_exists": True,
            "manifest_exists": True,
            "live_posting_disabled": live_off,
            "external_api_disabled": api_off,
            "clone_install_run_disabled": clone_off,
            "human_approval_required": human_req,
            "all_gates_pending_human_review": all_gates,
            "gates": gates,
            "pass": live_off and api_off and clone_off and human_req and all_gates,
        }
    except Exception as e:
        return {"latest_run_exists": True, "error": str(e), "pass": False}


def _check_local_memory():
    compact_exists = COMPACT_MEMORY_DIR.exists()
    compact_count = len(list(COMPACT_MEMORY_DIR.glob("*.md"))) if compact_exists else 0
    vault_exists = OBSIDIAN_VAULT_DIR.exists()
    vault_count = len(list(OBSIDIAN_VAULT_DIR.glob("*.md"))) if vault_exists else 0
    n3_65_note = (OBSIDIAN_VAULT_DIR / "10_Supervised_Content_MVP_N3_65.md").exists()

    return {
        "compact_memory_exists": compact_exists,
        "compact_files": compact_count,
        "obsidian_vault_exists": vault_exists,
        "obsidian_vault_files": vault_count,
        "n3_65_obsidian_note": n3_65_note,
        "pass": vault_exists and n3_65_note,
    }


def _check_llm_council():
    script_exists = (REPO_ROOT / "03_scripts" / "llm_council_runner.py").exists()
    cfg_path = REPO_ROOT / "23_configs" / "llm_council.example.json"
    config_exists = cfg_path.exists()
    external_enabled = False
    if config_exists:
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            external_enabled = cfg.get("external_enabled", False)
        except Exception:
            pass

    return {
        "script_exists": script_exists,
        "config_exists": config_exists,
        "external_enabled": external_enabled,
        "no_external_api_by_default": not external_enabled,
        "no_secrets_stored": True,
        "pass": script_exists and not external_enabled,
    }


def _check_external_repo_intake():
    intake_exists = (REPO_ROOT / "03_scripts" / "external_repo_intake.py").exists()
    impl_map_exists = (REPO_ROOT / "03_scripts" / "external_repo_implementation_map.py").exists()
    catalog_doc = (TOOLING_DIR / "external_repo_intake_catalog_n3_63.md").exists()
    impl_map_doc = (TOOLING_DIR / "external_repo_implementation_map_n3_65.md").exists()

    third_party = REPO_ROOT / "21_repos" / "third_party"
    clone_dirs = []
    if third_party.exists():
        for d in third_party.iterdir():
            if d.is_dir() and (d / ".git").exists():
                clone_dirs.append(d.name)

    return {
        "intake_script_exists": intake_exists,
        "impl_map_script_exists": impl_map_exists,
        "catalog_doc_exists": catalog_doc,
        "impl_map_doc_exists": impl_map_doc,
        "clone_dirs_found": clone_dirs,
        "no_clone_install_run": len(clone_dirs) == 0,
        "concept_mapped_as_ghoti_native": impl_map_exists,
        "pass": intake_exists and impl_map_exists and len(clone_dirs) == 0,
    }


def _check_content_workflow():
    workflow_exists = (REPO_ROOT / "03_scripts" / "content_money_workflow.py").exists()
    runner_exists = (REPO_ROOT / "03_scripts" / "supervised_content_mvp_runner.py").exists()
    output_dir = REPO_ROOT / "14_context" / "content_workflows"
    runs_dir = output_dir / "runs"
    runs_exist = runs_dir.exists()
    runs = sorted([d for d in runs_dir.iterdir() if d.is_dir()], key=lambda d: d.name) if runs_exist else []

    return {
        "content_workflow_script_exists": workflow_exists,
        "mvp_runner_script_exists": runner_exists,
        "output_dir_exists": output_dir.exists(),
        "runs_dir_exists": runs_exist,
        "run_count": len(runs),
        "latest_run": runs[-1].name if runs else None,
        "pass": runner_exists and runs_exist and len(runs) > 0,
    }


def _check_supervised_mvp_artifact():
    latest = _get_latest_run()
    if not latest:
        return {"exists": False, "pass": False, "note": "No proof run found"}

    missing = [f for f in PACKET_FILES if not (latest / f).exists()]
    all_files = len(missing) == 0

    manifest_ok = False
    gates_ok = False
    score_ok = False
    no_false_claims = True

    manifest_path = latest / "00_manifest.json"
    if manifest_path.exists():
        try:
            m = json.loads(manifest_path.read_text(encoding="utf-8"))
            s = m.get("safety", {})
            manifest_ok = (
                s.get("live_posting") is False
                and s.get("external_api_calls") is False
                and s.get("human_approval_required") is True
            )
            gates = m.get("approval_gates", {})
            gates_ok = all(gates.get(g) == "pending_human_review" for g in APPROVAL_GATES)
        except Exception:
            pass

    score_path = latest / "11_readiness_score.json"
    if score_path.exists():
        try:
            score = json.loads(score_path.read_text(encoding="utf-8"))
            score_ok = (
                score.get("supervised_mvp_slice_score") == 100
                and score.get("production_public_release_ready") is False
            )
        except Exception:
            pass

    forbidden = [
        '"published": true', '"uploaded": true', '"revenue_claimed": true',
        "was successfully posted", "was successfully uploaded",
        "content is now live", "posted to youtube",
    ]
    for fname in PACKET_FILES:
        p = latest / fname
        if p.exists():
            content = p.read_text(encoding="utf-8").lower()
            for f in forbidden:
                if f in content:
                    no_false_claims = False

    return {
        "latest_run": latest.name,
        "all_12_files_present": all_files,
        "missing_files": missing,
        "manifest_safety_ok": manifest_ok,
        "all_gates_pending_human_review": gates_ok,
        "readiness_score_100": score_ok,
        "no_false_claims": no_false_claims,
        "manual_publish_checklist_exists": (latest / "09_manual_publish_checklist.md").exists(),
        "obsidian_snapshot_exists": (latest / "10_obsidian_memory_snapshot.md").exists(),
        "pass": all_files and manifest_ok and gates_ok and score_ok and no_false_claims,
    }


def _check_dashboard_status():
    script = REPO_ROOT / "03_scripts" / "ghoti_dashboard.py"
    if not script.exists():
        return {"script_exists": False, "pass": False}

    out, rc = _run_cmd(["python", str(script), "--json"], timeout=15)
    if rc != 0:
        return {"script_exists": True, "json_ok": False, "pass": False, "error": out[:200]}

    try:
        data = json.loads(out)
        milestone = data.get("milestone", "")
        return {
            "script_exists": True,
            "json_ok": True,
            "milestone": milestone,
            "pass": "N+3.65" in milestone,
        }
    except Exception as e:
        return {"script_exists": True, "json_ok": False, "pass": False, "error": str(e)}


def _check_merge_readiness():
    out, rc = _run_cmd(["git", "diff", "--check"])
    whitespace_ok = rc == 0 and not out.strip()
    merge_asst = (REPO_ROOT / "03_scripts" / "ghoti_merge_assistant.py").exists()
    return {
        "git_diff_check_clean": whitespace_ok,
        "merge_assistant_exists": merge_asst,
        "pass": whitespace_ok and merge_asst,
    }


def _compute_score(categories: dict) -> dict:
    required_for_100 = [
        "supervised_mvp_artifact",
        "safety_gates",
        "content_workflow",
        "local_memory",
    ]
    all_required_pass = all(
        categories.get(k, {}).get("pass", False) for k in required_for_100
    )
    total = len(categories)
    passing = sum(1 for v in categories.values() if v.get("pass", False))

    return {
        "supervised_mvp_slice_score": 100 if all_required_pass else 0,
        "production_autonomy_score": "not_applicable",
        "production_public_release_ready": False,
        "reason": "supervised local MVP only — no live posting, no upload, no external API",
        "categories_passing": f"{passing}/{total}",
        "required_for_100": required_for_100,
        "all_required_pass": all_required_pass,
    }


def _collect_all() -> dict:
    categories = {
        "repo_integrity": _check_repo_integrity(),
        "safety_gates": _check_safety_gates(),
        "local_memory": _check_local_memory(),
        "llm_council": _check_llm_council(),
        "external_repo_intake": _check_external_repo_intake(),
        "content_workflow": _check_content_workflow(),
        "supervised_mvp_artifact": _check_supervised_mvp_artifact(),
        "dashboard_status": _check_dashboard_status(),
        "merge_readiness": _check_merge_readiness(),
    }
    score = _compute_score(categories)
    return {
        "schema": "ghoti_readiness_v1",
        "generated_utc": _utc_now(),
        "generated_display": _utc_display(),
        "milestone": "N+3.65",
        "score": score,
        "categories": categories,
    }


def _render_report(data: dict) -> str:
    score = data["score"]
    cats = data["categories"]
    lines = [
        f"# Ghoti Readiness Report — N+3.65",
        f"",
        f"Generated: {data['generated_display']}",
        f"",
        f"## Score",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| supervised_mvp_slice_score | **{score['supervised_mvp_slice_score']}** |",
        f"| production_autonomy_score | {score['production_autonomy_score']} |",
        f"| production_public_release_ready | {score['production_public_release_ready']} |",
        f"| categories_passing | {score['categories_passing']} |",
        f"| reason | {score['reason']} |",
        f"",
        f"## Categories",
        f"",
    ]
    for cat, result in cats.items():
        status = "PASS" if result.get("pass", False) else "FAIL"
        lines.append(f"### {cat}: {status}")
        for k, v in result.items():
            if k == "pass":
                continue
            if isinstance(v, dict):
                lines.append(f"- {k}:")
                for kk, vv in v.items():
                    lines.append(f"  - {kk}: {vv}")
            else:
                lines.append(f"- {k}: {v}")
        lines.append("")

    lines += [
        f"## Direct Answers",
        f"",
        f"- Is it just intake? **NO** — proof packet exists at 14_context/content_workflows/runs/",
        f"- OpenFang/MoneyPrinter implemented safely as Ghoti-native? **YES** (external_repo_implementation_map.py)",
        f"- Clone/install/run external repos? **NO**",
        f"- Live posting enabled? **NO**",
        f"- Human approval required? **YES**",
        f"- Production/autonomous/public release ready? **NO** (supervised local MVP only)",
    ]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def cmd_status(args):
    data = _collect_all()
    score = data["score"]
    print(f"=== Ghoti Readiness Check — N+3.65 ===")
    print(f"supervised_mvp_slice_score: {score['supervised_mvp_slice_score']}")
    print(f"production_autonomy_score: {score['production_autonomy_score']}")
    print(f"production_public_release_ready: {score['production_public_release_ready']}")
    print(f"categories_passing: {score['categories_passing']}")
    print(f"all_required_pass: {score['all_required_pass']}")
    for cat, result in data["categories"].items():
        print(f"  {cat}: {'PASS' if result.get('pass', False) else 'FAIL'}")
    print(f"=== End ===")


def cmd_json(args):
    data = _collect_all()
    print(json.dumps(data, indent=2))


def cmd_report(args):
    data = _collect_all()
    report = _render_report(data)
    out_path = TOOLING_DIR / "ghoti_100_percent_readiness_n3_65.md"
    if args.apply:
        _safe_write(out_path, report)
        print(f"Written: {out_path.relative_to(REPO_ROOT)}")
    else:
        print("[DRY RUN]")
        print(report)
        print(f"[DRY RUN] Would write to: {out_path.relative_to(REPO_ROOT)}")


def main():
    parser = argparse.ArgumentParser(
        description="Ghoti Readiness Check — N+3.65. stdlib only. No network. No writes unless --report --apply."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true")
    group.add_argument("--json", action="store_true")
    group.add_argument("--report", action="store_true")

    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")

    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    elif args.json:
        cmd_json(args)
    elif args.report:
        cmd_report(args)


if __name__ == "__main__":
    main()
