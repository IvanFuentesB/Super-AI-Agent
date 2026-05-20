#!/usr/bin/env python3
"""Model council and tool intake registry for Ghoti N+5.2A."""
from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = REPO_ROOT / "14_context" / "model_council_tool_intake" / "runs"


def slug_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ_model_council_tool_intake")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def read_doc(path: str) -> str:
    file_path = REPO_ROOT / path
    return file_path.read_text(encoding="utf-8") if file_path.exists() else f"# Missing\n\n{path} is not present yet.\n"


def registry() -> list[dict]:
    return [
        {"slug": "hermes-agent", "status": "priority_local_bootstrap", "runtime_wiring": False, "notes": "Candidate agent operating layer; local install pending human approval."},
        {"slug": "graphify", "status": "evaluate", "runtime_wiring": False, "notes": "Knowledge graph/token-efficiency candidate."},
        {"slug": "claude skills", "status": "recover_and_verify", "runtime_wiring": False, "notes": "Detect installed skills before relying on prompts."},
        {"slug": "claude skills missing/recovery", "status": "documented_plan", "runtime_wiring": False, "notes": "Recovery plan required before using unavailable skills."},
        {"slug": "vercel-labs/agent-browser", "status": "high_priority_intake", "runtime_wiring": False, "notes": "Browser QA candidate; no autonomous browsing wired."},
        {"slug": "browser-harness", "status": "high_priority_intake", "runtime_wiring": False, "notes": "Compliant browser harness candidate."},
        {"slug": "gemma/ollama", "status": "local_worker_candidate", "runtime_wiring": False, "notes": "Cheap local summarization/classification worker lane."},
        {"slug": "chatgpt/openai", "status": "manual_council_brain", "runtime_wiring": False, "notes": "Planning/product reasoning lane; no API keys committed."},
        {"slug": "claude-code", "status": "implementation_lane", "runtime_wiring": False, "notes": "Human-started implementation lane when credits are available."},
        {"slug": "codex", "status": "preferred_audit_and_possible_provider", "runtime_wiring": False, "notes": "Preferred verification lane; Hermes provider support pending/not verified."},
        {"slug": "postgres", "status": "data_layer_candidate", "runtime_wiring": False, "notes": "Default relational store candidate."},
        {"slug": "supabase", "status": "default_backend_candidate", "runtime_wiring": False, "notes": "Postgres/auth/storage where practical."},
        {"slug": "vercel", "status": "frontend_deploy_candidate", "runtime_wiring": False, "notes": "Frontend/deploy default candidate."},
        {"slug": "stripe", "status": "payments_candidate", "runtime_wiring": False, "notes": "Payments only after separate audited payment milestone."},
        {"slug": "claude-api", "status": "provider_candidate", "runtime_wiring": False, "notes": "No live provider launch in this milestone."},
        {"slug": "github", "status": "repo_ops_candidate", "runtime_wiring": False, "notes": "Repo/profile operations remain human-approved."},
        {"slug": "resend", "status": "email_candidate", "runtime_wiring": False, "notes": "Email provider candidate; no live email action."},
        {"slug": "clerk", "status": "auth_candidate", "runtime_wiring": False, "notes": "Alternative to Supabase Auth; choose one per project."},
        {"slug": "dns/namecheap/cloudflare-style provider", "status": "domain_dns_candidate", "runtime_wiring": False, "notes": "Domain/DNS setup remains manual."},
        {"slug": "posthog", "status": "analytics_candidate", "runtime_wiring": False, "notes": "Analytics after privacy review."},
        {"slug": "sentry", "status": "errors_candidate", "runtime_wiring": False, "notes": "Error monitoring candidate."},
        {"slug": "upstash", "status": "queues_cache_candidate", "runtime_wiring": False, "notes": "Queues/cache/rate limiting candidate."},
        {"slug": "pinecone", "status": "optional_vector_db", "runtime_wiring": False, "notes": "Use only if local/Supabase pgvector is insufficient."},
        {"slug": "azure", "status": "later_heavy_cloud_option", "runtime_wiring": False, "notes": "Enterprise/heavier cloud option, not default."},
        {"slug": "terraform/opentofu IaC", "status": "blueprint_only", "runtime_wiring": False, "notes": "Infrastructure-as-code direction with placeholders only."},
        {"slug": "blueprint.am", "status": "planning_intake", "runtime_wiring": False, "notes": "Architecture blueprint inspiration only."},
        {"slug": "awesome-matlab-robotics / mthworks-robotics", "status": "portfolio_reference", "runtime_wiring": False, "notes": "Robotics learning/reference lane."},
        {"slug": "picoclaw", "status": "hardware_reference", "runtime_wiring": False, "notes": "Robotics/hardware reference only."},
        {"slug": "ai-factory repo", "status": "repo_pattern_reference", "runtime_wiring": False, "notes": "Architecture pattern intake only."},
        {"slug": "insforge", "status": "backend_reference", "runtime_wiring": False, "notes": "Backend/infrastructure reference only."},
        {"slug": "openwa", "status": "messaging_reference_blocked_runtime", "runtime_wiring": False, "notes": "No live messaging/account automation."},
        {"slug": "cloak/browser bot-detection", "status": "BLOCKED", "runtime_wiring": False, "notes": "Bot-detection bypass/captcha bypass is blocked."},
        {"slug": "GitHub profile/repo upgrades", "status": "portfolio_side_lane", "runtime_wiring": False, "notes": "Pinned repos, topics, GIFs, Actions, releases, templates."},
        {"slug": "repo branding/images", "status": "portfolio_side_lane", "runtime_wiring": False, "notes": "Every important repo should have a safe branded asset."},
    ]


def manifest() -> dict:
    return {
        "local_only": True,
        "external_repos_installed": False,
        "external_repos_executed": False,
        "live_api_used": False,
        "secrets_required": False,
        "human_review_required": True,
        "runtime_wiring_enabled": False,
        "bot_detection_bypass_enabled": False,
        "tool_count": len(registry()),
    }


def scan() -> dict:
    tools = registry()
    return {
        "ok": True,
        "action": "scan",
        "manifest": manifest(),
        "registry": tools,
        "blocked_entries": [item for item in tools if item["status"] == "BLOCKED"],
    }


def latest_run() -> Path | None:
    if not RUN_ROOT.exists():
        return None
    runs = [item for item in RUN_ROOT.iterdir() if item.is_dir()]
    return sorted(runs, key=lambda item: item.name)[-1] if runs else None


def make_run_dir() -> Path:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    path = RUN_ROOT / slug_now()
    suffix = 2
    while path.exists():
        path = RUN_ROOT / f"{slug_now()}_{suffix}"
        suffix += 1
    path.mkdir(parents=True)
    return path


def write_report() -> dict:
    out_dir = make_run_dir()
    data = scan()
    write_json(out_dir / "00_manifest.json", data["manifest"])
    (out_dir / "01_model_council_architecture.md").write_text(read_doc("docs/HERMES_AGENT_MODEL_COUNCIL_INTAKE.md"), encoding="utf-8")
    write_json(out_dir / "02_tool_intake_registry.json", {"registry": data["registry"]})
    (out_dir / "03_token_efficiency_plan.md").write_text(read_doc("docs/TOKEN_EFFICIENT_COMPUTER_USE_ROADMAP.md"), encoding="utf-8")
    (out_dir / "04_computer_use_strategy.md").write_text(read_doc("docs/AGENT_BROWSER_BROWSER_HARNESS_INTAKE.md"), encoding="utf-8")
    (out_dir / "05_local_worker_model_plan.md").write_text(read_doc("docs/HERMES_LOCAL_INSTALL_AND_PROVIDER_PLAN.md"), encoding="utf-8")
    (out_dir / "06_cloud_infrastructure_plan.md").write_text(read_doc("docs/CLOUD_INFRASTRUCTURE_BLUEPRINT.md"), encoding="utf-8")
    (out_dir / "07_iac_blueprint.md").write_text(read_doc("infra/iac_blueprint.yaml"), encoding="utf-8")
    (out_dir / "08_safety_and_tos_review.md").write_text(read_doc("docs/BLOCKED_UNSAFE_AUTOMATION.md"), encoding="utf-8")
    backlog = [
        {"milestone": "N+5.2B", "title": "Model Council Router MVP", "status": "planned"},
        {"milestone": "N+5.2C", "title": "Gemma Local Worker Lane", "status": "planned"},
        {"milestone": "N+5.2D", "title": "Provider Registry", "status": "planned"},
        {"milestone": "N+5.3A", "title": "Hermes Adapter Sandbox Evaluation", "status": "planned"},
    ]
    write_json(out_dir / "09_roadmap_backlog.json", {"items": backlog})
    (out_dir / "10_preview.html").write_text(
        "<!doctype html><meta charset='utf-8'><title>Model Council Tool Intake</title>"
        "<h1>Model Council Tool Intake</h1>"
        f"<p>Tools: {len(data['registry'])}</p>"
        f"<p>Runtime wiring enabled: {html.escape(str(data['manifest']['runtime_wiring_enabled']))}</p>"
        f"<p>Unsafe browser bypass enabled: {html.escape(str(data['manifest']['bot_detection_bypass_enabled']))}</p>",
        encoding="utf-8",
    )
    data["run_dir"] = rel(out_dir)
    return data


def latest() -> dict:
    run = latest_run()
    if not run:
        return {"ok": False, "error": "no model council intake runs found"}
    manifest_path = run / "00_manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    return {"ok": True, "action": "latest", "run_dir": rel(run), "manifest": data}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Model council tool intake")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--latest", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.write_report:
        data = write_report()
    elif args.latest:
        data = latest()
    elif args.scan:
        data = scan()
    else:
        data = {"ok": True, "action": "status", "manifest": manifest(), "registry": registry()}

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(f"model_council_tool_intake ok={data.get('ok')} action={data.get('action')}")
    return 0 if data.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
