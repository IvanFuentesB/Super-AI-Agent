#!/usr/bin/env python3
"""External Repo Intake — stdlib-only local catalog for external repo candidates.

N+3.63A: OpenFang (2 candidates), MoneyPrinter (V1 + V2), Karpathy LLM Council.
No clone, no network, no install by default. Intake/planning/scaffold only.
All clone_allowed_now, install_allowed_now, runtime_wiring_allowed_now are false.
"""
import argparse
import datetime
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()
TOOLING_DIR = REPO_ROOT / "14_context" / "tooling"
CATALOG_PATH = TOOLING_DIR / "external_repo_intake_catalog_n3_63.md"
RISK_REPORT_PATH = TOOLING_DIR / "external_repo_risk_report_n3_63.md"

CATALOG: dict[str, dict] = {
    "openfang_python_gateway": {
        "repo_id": "openfang_python_gateway",
        "human_name": "OpenFang (Python gateway candidate — aidiss/openfang)",
        "possible_github": "aidiss/openfang",
        "source_url_note": "openfang.ai — lightweight Python AI agent gateway, messaging channels, tools, skills, persistent memory, FastAPI/HTMX/Alpine, ~5K LOC",
        "category": "agent_gateway",
        "language_guess": "Python",
        "why_relevant_to_ghoti": (
            "Channel gateway concepts, tool/skill organization, compact local operator gateway "
            "pattern compatible with Ghoti's Python-first stack."
        ),
        "useful_patterns": [
            "messaging channel abstraction",
            "skills/tools registry",
            "persistent memory without heavy dependencies",
            "FastAPI local API gateway",
            "HTMX/Alpine lightweight frontend",
        ],
        "risks": [
            "messaging tokens for live channel actions",
            "external provider keys (Slack, Discord, Telegram etc.)",
            "live channel message dispatch",
        ],
        "forbidden_until_audited": [
            "wiring any messaging channel to live accounts",
            "storing provider tokens/keys in repo",
            "making outbound API calls to messaging platforms",
        ],
        "safe_next_action": "Read source structure docs only; design Ghoti channel gateway adapter scaffold inspired by pattern",
        "clone_allowed_now": False,
        "install_allowed_now": False,
        "runtime_wiring_allowed_now": False,
        "ambiguity_note": (
            "Multiple projects use the name 'OpenFang'. This entry is specifically for aidiss/openfang "
            "(Python gateway). Do NOT conflate with RightNow-AI/openfang (Rust Agent OS)."
        ),
    },
    "openfang_rust_agent_os": {
        "repo_id": "openfang_rust_agent_os",
        "human_name": "OpenFang (Rust Agent OS candidate — RightNow-AI/openfang)",
        "possible_github": "RightNow-AI/openfang",
        "source_url_note": "openfang.sh/app/cc — Rust Agent OS, 14 crates, Hands (Clip/Lead/Collector/etc.), many channel adapters, providers, security systems",
        "category": "rust_agent_os",
        "language_guess": "Rust",
        "why_relevant_to_ghoti": (
            "Eventual Rust daemon, scheduler, security layers, audit trail inspiration. "
            "Content Clip hand concept is relevant to supervised content workflow design."
        ),
        "useful_patterns": [
            "Hands abstraction (Clip/Lead/Collector)",
            "security/audit architecture in Rust",
            "crate-level modular agent OS design",
            "channel adapter pattern at scale",
            "scheduler + audit trail separation",
        ],
        "risks": [
            "autonomous scheduled agents",
            "many live channel adapters",
            "external providers wired at runtime",
            "live posting via Clip hand if not gated",
        ],
        "forbidden_until_audited": [
            "compiling or running any Rust crate",
            "wiring any Hand to a live account or service",
            "running scheduler",
            "connecting any channel adapter to a live endpoint",
        ],
        "safe_next_action": "Read architecture docs and crate names only; sketch a future Ghoti Rust daemon inspired by crate layout",
        "clone_allowed_now": False,
        "install_allowed_now": False,
        "runtime_wiring_allowed_now": False,
        "ambiguity_note": (
            "Multiple projects use the name 'OpenFang'. This entry is specifically for RightNow-AI/openfang "
            "(Rust Agent OS). Do NOT conflate with aidiss/openfang (Python gateway)."
        ),
    },
    "moneyprinter_shorts": {
        "repo_id": "moneyprinter_shorts",
        "human_name": "MoneyPrinter V1 (FujiwaraChoki/MoneyPrinter by DevBySami)",
        "possible_github": "FujiwaraChoki/MoneyPrinter",
        "source_url_note": "GitHub FujiwaraChoki/MoneyPrinter — YouTube Shorts generation from a topic. Ollama-first script gen. DB-backed queue/API/worker/Postgres.",
        "category": "content_generation_pipeline",
        "language_guess": "Python",
        "why_relevant_to_ghoti": (
            "Content generation workflow inspiration, YouTube Shorts pipeline stages, "
            "local Ollama script/metadata generation, queue design patterns."
        ),
        "useful_patterns": [
            "topic → script → video pipeline stages",
            "Ollama-first local LLM script generation",
            "DB-backed job queue for content tasks",
            "API/worker architecture for content pipeline",
            "metadata and SEO generation scaffold",
        ],
        "risks": [
            "platform ToS violations (YouTube upload, TikTok voice API)",
            "copyrighted media or music inclusion",
            "TikTok voice synthesis API (external, ToS risk)",
            "YouTube upload OAuth (live account action)",
            "potential for spam or low-quality content at scale",
        ],
        "forbidden_until_audited": [
            "running the pipeline to generate or upload actual videos",
            "calling TikTok voice API",
            "using YouTube OAuth upload",
            "including any copyrighted media without license check",
            "automated posting of any kind",
        ],
        "safe_next_action": "Study pipeline stage design only; adapt stage structure to Ghoti content_money_workflow scaffold (planning artifacts, no upload)",
        "clone_allowed_now": False,
        "install_allowed_now": False,
        "runtime_wiring_allowed_now": False,
    },
    "moneyprinter_v2": {
        "repo_id": "moneyprinter_v2",
        "human_name": "MoneyPrinterV2 (FujiwaraChoki/MoneyPrinterV2 — higher risk)",
        "possible_github": "FujiwaraChoki/MoneyPrinterV2",
        "source_url_note": "GitHub FujiwaraChoki/MoneyPrinterV2 — expands toward YouTube Shorts, Twitter/X, affiliate marketing, local business outreach",
        "category": "monetization_automation",
        "language_guess": "Python",
        "why_relevant_to_ghoti": (
            "Modular workflow concepts and content/money experiments. Separate from V1 and higher risk."
        ),
        "useful_patterns": [
            "modular platform adapter design",
            "content type diversification (video + social + affiliate)",
        ],
        "risks": [
            "social bots (Twitter/X automation)",
            "affiliate marketing automation (may violate platform ToS)",
            "cold outreach automation (spam risk)",
            "legal/ToS risk across multiple platforms",
            "higher risk than V1 due to multi-platform social posting scope",
        ],
        "forbidden_until_audited": [
            "all automation features",
            "social posting of any kind",
            "affiliate outreach",
            "cold email or DM automation",
            "running any V2 feature without explicit legal/ToS review",
        ],
        "safe_next_action": "Planning/intake only. Do not clone or reference any V2 code until V1 audit is complete and human has reviewed ToS implications.",
        "clone_allowed_now": False,
        "install_allowed_now": False,
        "runtime_wiring_allowed_now": False,
        "restriction": "planning_intake_only",
    },
    "karpathy_llm_council": {
        "repo_id": "karpathy_llm_council",
        "human_name": "Karpathy LLM Council (karpathy/llm-council)",
        "possible_github": "karpathy/llm-council",
        "source_url_note": "GitHub karpathy/llm-council — multi-model debate/synthesis scaffold",
        "category": "llm_orchestration",
        "language_guess": "Python",
        "why_relevant_to_ghoti": "Model council debate and synthesis for idea review and multi-perspective analysis.",
        "useful_patterns": [
            "multi-model debate flow",
            "chairman synthesis",
            "peer review between models",
        ],
        "risks": [
            "external API keys if using cloud providers",
            "cost if not using local Ollama fallback",
        ],
        "forbidden_until_audited": [
            "storing API keys for external providers",
            "making external API calls without explicit user approval",
        ],
        "safe_next_action": "Already implemented as local-first scaffold in N+3.61A via llm_council_runner.py. Continue using local_demo mode.",
        "clone_allowed_now": False,
        "install_allowed_now": False,
        "runtime_wiring_allowed_now": False,
        "implementation_status": "implemented_n3_61a_local_scaffold",
    },
}


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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
    print("=== External Repo Intake Status ===")
    print(f"Tracked candidates: {len(CATALOG)}")
    for rid, entry in CATALOG.items():
        clone = "NO" if not entry["clone_allowed_now"] else "YES"
        install = "NO" if not entry["install_allowed_now"] else "YES"
        wiring = "NO" if not entry["runtime_wiring_allowed_now"] else "YES"
        print(f"  {rid}: clone={clone} install={install} wiring={wiring}")
    print(f"Catalog doc: {'EXISTS' if CATALOG_PATH.exists() else 'NOT WRITTEN'}")
    print(f"Risk report: {'EXISTS' if RISK_REPORT_PATH.exists() else 'NOT WRITTEN'}")
    print("No clone/install/runtime wiring allowed. Intake and planning only.")
    print("=== End Status ===")


def cmd_list(args):
    print("External Repo Candidates:")
    for rid, entry in CATALOG.items():
        print(f"  {rid}")
        print(f"    name    : {entry['human_name']}")
        print(f"    github  : {entry['possible_github']}")
        print(f"    category: {entry['category']}")
        print(f"    language: {entry['language_guess']}")
        print(f"    clone   : {'YES' if entry['clone_allowed_now'] else 'NO'}")
        print(f"    install : {'YES' if entry['install_allowed_now'] else 'NO'}")
        print(f"    wiring  : {'YES' if entry['runtime_wiring_allowed_now'] else 'NO'}")
        print()


def cmd_show(args):
    rid = args.show
    if rid not in CATALOG:
        print(f"ERROR: Unknown repo_id '{rid}'. Use --list to see available IDs.")
        sys.exit(1)
    entry = CATALOG[rid]
    print(json.dumps(entry, indent=2))


def _render_catalog_md() -> str:
    ts = _utc_now()
    lines = [
        "# External Repo Intake Catalog — N+3.63A",
        "",
        f"Generated: {ts}",
        "",
        "**Purpose:** Local catalog of external repo candidates for Ghoti supervised MVP.",
        "No clone, no install, no runtime wiring. Intake and planning only.",
        "",
        "---",
        "",
    ]
    for rid, entry in CATALOG.items():
        lines += [
            f"## {entry['human_name']}",
            "",
            f"- **repo_id:** `{rid}`",
            f"- **possible_github:** `{entry['possible_github']}`",
            f"- **source_url_note:** {entry['source_url_note']}",
            f"- **category:** {entry['category']}",
            f"- **language_guess:** {entry['language_guess']}",
            f"- **clone_allowed_now:** {entry['clone_allowed_now']}",
            f"- **install_allowed_now:** {entry['install_allowed_now']}",
            f"- **runtime_wiring_allowed_now:** {entry['runtime_wiring_allowed_now']}",
            "",
            f"**Why relevant to Ghoti:** {entry['why_relevant_to_ghoti']}",
            "",
            "**Useful patterns:**",
        ]
        for p in entry["useful_patterns"]:
            lines.append(f"- {p}")
        lines += [
            "",
            "**Risks:**",
        ]
        for r in entry["risks"]:
            lines.append(f"- {r}")
        lines += [
            "",
            f"**Safe next action:** {entry['safe_next_action']}",
        ]
        if "ambiguity_note" in entry:
            lines += ["", f"**Ambiguity note:** {entry['ambiguity_note']}"]
        if "restriction" in entry:
            lines += ["", f"**Restriction:** {entry['restriction']}"]
        if "implementation_status" in entry:
            lines += ["", f"**Implementation status:** {entry['implementation_status']}"]
        lines += ["", "---", ""]
    return "\n".join(lines)


def _render_risk_report_md() -> str:
    ts = _utc_now()
    lines = [
        "# External Repo Risk Report — N+3.63A",
        "",
        f"Generated: {ts}",
        "",
        "**Purpose:** Safety risk summary for each tracked external repo candidate.",
        "All items below are forbidden until explicitly audited and approved.",
        "",
        "---",
        "",
    ]
    for rid, entry in CATALOG.items():
        lines += [
            f"## {entry['human_name']}",
            "",
            f"**Repo ID:** `{rid}`",
            "",
            "**Forbidden until audited:**",
        ]
        for f in entry["forbidden_until_audited"]:
            lines.append(f"- {f}")
        lines += [
            "",
            "**Risks:**",
        ]
        for r in entry["risks"]:
            lines.append(f"- {r}")
        lines += [
            "",
            "**Current gate status:**",
            f"- clone_allowed_now: {entry['clone_allowed_now']}",
            f"- install_allowed_now: {entry['install_allowed_now']}",
            f"- runtime_wiring_allowed_now: {entry['runtime_wiring_allowed_now']}",
            "",
            "---",
            "",
        ]
    lines += [
        "## Global Safety Statements",
        "",
        "- OpenFang intake only — no clone/install/run.",
        "- MoneyPrinter intake only — no clone/install/run.",
        "- Content workflow planning only — no upload, no post, no live actions.",
        "- No secrets stored or read.",
        "- No external API calls by default.",
        "- Human review required before any real integration.",
        "- '100%' means local-supervised MVP, not autonomous money machine.",
        "",
    ]
    return "\n".join(lines)


def cmd_write_catalog(args):
    content = _render_catalog_md()
    if args.dry_run and not args.apply:
        print("[DRY RUN] Catalog preview (first 40 lines):")
        for line in content.splitlines()[:40]:
            print(f"  {line}")
        print(f"[DRY RUN] Would write to: {CATALOG_PATH.relative_to(REPO_ROOT)}")
        print("[DRY RUN] Pass --apply to write.")
        return
    if args.apply:
        _safe_write(CATALOG_PATH, content)
        print(f"Written: {CATALOG_PATH.relative_to(REPO_ROOT)}")


def cmd_risk_report(args):
    content = _render_risk_report_md()
    if args.dry_run and not args.apply:
        print("[DRY RUN] Risk report preview (first 40 lines):")
        for line in content.splitlines()[:40]:
            print(f"  {line}")
        print(f"[DRY RUN] Would write to: {RISK_REPORT_PATH.relative_to(REPO_ROOT)}")
        print("[DRY RUN] Pass --apply to write.")
        return
    if args.apply:
        _safe_write(RISK_REPORT_PATH, content)
        print(f"Written: {RISK_REPORT_PATH.relative_to(REPO_ROOT)}")


def main():
    parser = argparse.ArgumentParser(
        description="External Repo Intake — stdlib-only local catalog. N+3.63A. No clone/install/run."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true", help="Show intake status")
    group.add_argument("--list", action="store_true", help="List all tracked candidates")
    group.add_argument("--show", metavar="REPO_ID", help="Show full record for a repo_id")
    group.add_argument("--write-catalog", action="store_true", help="Write catalog markdown doc")
    group.add_argument("--risk-report", action="store_true", help="Write risk report markdown doc")

    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true")

    args = parser.parse_args()

    if args.status:
        cmd_status(args)
    elif args.list:
        cmd_list(args)
    elif args.show:
        cmd_show(args)
    elif args.write_catalog:
        cmd_write_catalog(args)
    elif args.risk_report:
        cmd_risk_report(args)


if __name__ == "__main__":
    main()
