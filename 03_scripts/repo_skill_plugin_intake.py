#!/usr/bin/env python3
"""Repo / Skill / Plugin Intake Registry -- N+4.2A.

Metadata catalog for all external tool/repo/skill candidates.
No clone, no install, no runtime wiring. Intake / planning only.
Validation fails if any entry has current_runtime_wiring, clone_install_run_enabled,
or live_account_action_enabled set to True.

stdlib-only. No external API calls.
"""
from __future__ import annotations

import argparse
import json
import sys

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

CATALOG: dict[str, dict] = {
    "ui_tars": {
        "name": "UI-TARS",
        "type": "computer_use_agent",
        "category": "vision_ui_automation",
        "value_hypothesis": "Vision-based UI interaction for desktop/browser automation; complement to Claude computer-use for Ghoti operator tasks.",
        "status": "intake_only",
        "allowed_actions": ["read_docs", "design_adapter_scaffold", "research_architecture"],
        "forbidden_actions": ["clone", "install", "run", "wire_to_runtime", "live_account_action", "autonomous_posting"],
        "approval_gate": "human_approval_required_before_any_clone_install_run",
        "risk_level": "medium",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "N+4.2/N+4.4 milestone target. No live screen/account access without explicit approval.",
    },
    "the_agency": {
        "name": "The Agency",
        "type": "multi_agent_framework",
        "category": "agent_orchestration",
        "value_hypothesis": "Multi-agent coordination framework; potential base layer for Ghoti agent-to-agent delegation.",
        "status": "intake_only",
        "allowed_actions": ["read_docs", "design_adapter_scaffold", "research_architecture"],
        "forbidden_actions": ["clone", "install", "run", "wire_to_runtime", "live_account_action"],
        "approval_gate": "human_approval_required_before_any_clone_install_run",
        "risk_level": "medium",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "N+4.2/N+4.4 milestone target.",
    },
    "agent_skills_eval": {
        "name": "agent-skills-eval",
        "type": "eval_framework",
        "category": "skill_evaluation",
        "value_hypothesis": "Benchmark and evaluate Claude Code skills and agent capabilities; measure skill performance.",
        "status": "intake_only",
        "allowed_actions": ["read_docs", "research_eval_methodology"],
        "forbidden_actions": ["clone", "install", "run", "wire_to_runtime"],
        "approval_gate": "human_approval_required_before_any_clone_install_run",
        "risk_level": "low",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "Useful for validating Ghoti skill quality. No live accounts needed.",
    },
    "arcads_claude_code": {
        "name": "arcads-claude-code",
        "type": "claude_code_skill",
        "category": "video_ad_generation",
        "value_hypothesis": "AI-generated video ads via Claude Code skill; potential for supervised content creation workflows.",
        "status": "intake_only",
        "allowed_actions": ["read_docs", "research_skill_interface"],
        "forbidden_actions": ["clone", "install", "run", "wire_to_runtime", "live_account_action", "autonomous_posting"],
        "approval_gate": "human_approval_required_before_any_live_action",
        "risk_level": "medium",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "No live ad posting without human approval and legal review.",
    },
    "weavy": {
        "name": "Weavy",
        "type": "collaboration_platform_sdk",
        "category": "embedded_collaboration",
        "value_hypothesis": "Embedded chat/feeds/notifications SDK; potential Ghoti dashboard collaboration layer.",
        "status": "intake_only",
        "allowed_actions": ["read_docs", "research_sdk_interface"],
        "forbidden_actions": ["clone", "install", "run", "wire_to_runtime", "live_api_call"],
        "approval_gate": "human_approval_required_before_any_api_wiring",
        "risk_level": "medium",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "Requires live API keys for any real use. No keys stored in repo.",
    },
    "manychat": {
        "name": "Manychat",
        "type": "chat_marketing_platform",
        "category": "messaging_automation",
        "value_hypothesis": "Instagram/Facebook/WhatsApp automation for supervised content promotion workflows.",
        "status": "intake_only",
        "allowed_actions": ["read_docs", "research_api_scope"],
        "forbidden_actions": ["clone", "install", "run", "wire_to_runtime", "live_account_action", "autonomous_posting"],
        "approval_gate": "human_approval_required_before_any_live_posting",
        "risk_level": "high",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "No autonomous posting. No live account access. Human approval + legal review required.",
    },
    "openfang_moneyprinter": {
        "name": "OpenFang/MoneyPrinter",
        "type": "content_generation_tool",
        "category": "automated_content_pipeline",
        "value_hypothesis": "Content generation pipeline concepts; script/video/thumbnail automation patterns for supervised workflow.",
        "status": "intake_only",
        "allowed_actions": ["read_docs", "research_architecture_patterns"],
        "forbidden_actions": ["clone", "install", "run", "wire_to_runtime", "autonomous_posting", "live_monetization"],
        "approval_gate": "human_approval_required_before_any_clone_install_run",
        "risk_level": "medium",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "Patterns only. No autonomous content publishing.",
    },
    "airllm": {
        "name": "AirLLM",
        "type": "local_llm_inference",
        "category": "local_model_runner",
        "value_hypothesis": "Extreme memory reduction for running large LLMs locally; complement to Ollama/Gemma for offline inference.",
        "status": "intake_only",
        "allowed_actions": ["read_docs", "research_architecture"],
        "forbidden_actions": ["clone", "install", "run", "wire_to_runtime"],
        "approval_gate": "human_approval_required_before_any_clone_install_run",
        "risk_level": "low",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "Local inference only, no external API. Lower risk but requires install approval.",
    },
    "mermaid": {
        "name": "Mermaid",
        "type": "diagram_generation",
        "category": "documentation_tool",
        "value_hypothesis": "Text-to-diagram for Ghoti architecture docs, workflow visualization, and Obsidian vault diagrams.",
        "status": "research_only",
        "allowed_actions": ["read_docs", "use_mermaid_live_editor", "generate_diagrams_in_docs"],
        "forbidden_actions": ["wire_to_runtime_as_live_service"],
        "approval_gate": "low_risk_no_approval_needed_for_static_diagrams",
        "risk_level": "low",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "Static diagram generation in docs is already safe. No live service wiring needed.",
    },
    "claude_cowork": {
        "name": "Claude Cowork",
        "type": "collaboration_workspace",
        "category": "ai_collaboration_platform",
        "value_hypothesis": "Claude-native team collaboration workspace; potential integration point for Ghoti operator coordination.",
        "status": "intake_only",
        "allowed_actions": ["read_docs", "research_api_scope"],
        "forbidden_actions": ["wire_to_runtime", "live_account_action", "autonomous_posting"],
        "approval_gate": "human_approval_required_before_any_api_wiring",
        "risk_level": "low",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "Anthropic-native; lower risk but still requires explicit wiring approval.",
    },
    "speckit": {
        "name": "Speckit",
        "type": "spec_generation_tool",
        "category": "product_documentation",
        "value_hypothesis": "AI-assisted spec/PRD generation; Ghoti workflow documentation and feature specification support.",
        "status": "intake_only",
        "allowed_actions": ["read_docs", "research_use_cases"],
        "forbidden_actions": ["wire_to_runtime", "live_account_action"],
        "approval_gate": "human_approval_required_before_any_wiring",
        "risk_level": "low",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "Low risk documentation tool. No autonomous publishing.",
    },
    "sigmap": {
        "name": "Sigmap",
        "type": "workflow_automation",
        "category": "signal_mapping",
        "value_hypothesis": "Signal/event mapping for agent coordination; potential Ghoti relay-loop integration.",
        "status": "intake_only",
        "allowed_actions": ["read_docs", "research_integration_patterns"],
        "forbidden_actions": ["wire_to_runtime", "live_account_action"],
        "approval_gate": "human_approval_required_before_any_wiring",
        "risk_level": "medium",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "No runtime event wiring without approval.",
    },
    "anvac": {
        "name": "Anvac",
        "type": "agent_validation",
        "category": "agent_testing",
        "value_hypothesis": "Agent behavior validation and testing framework; Ghoti agent quality assurance.",
        "status": "intake_only",
        "allowed_actions": ["read_docs", "research_testing_methodology"],
        "forbidden_actions": ["wire_to_runtime", "live_account_action"],
        "approval_gate": "human_approval_required_before_any_clone_install_run",
        "risk_level": "low",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "Testing/validation tool. Low operational risk.",
    },
    "agent_exchange_aex": {
        "name": "Agent Exchange / AEX",
        "type": "agent_marketplace",
        "category": "agent_discovery_exchange",
        "value_hypothesis": "Agent discovery and exchange platform; potential for Ghoti agent-to-agent delegation marketplace.",
        "status": "intake_only",
        "allowed_actions": ["read_docs", "research_agent_exchange_patterns"],
        "forbidden_actions": ["clone", "install", "run", "wire_to_runtime", "live_account_action"],
        "approval_gate": "human_approval_required_before_any_wiring",
        "risk_level": "medium",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "No live agent execution without approval.",
    },
    "vouch": {
        "name": "Vouch",
        "type": "video_testimonial_platform",
        "category": "video_content_platform",
        "value_hypothesis": "Video testimonial collection and management; supervised content workflow integration.",
        "status": "intake_only",
        "allowed_actions": ["read_docs", "research_api_scope"],
        "forbidden_actions": ["wire_to_runtime", "live_account_action", "autonomous_posting"],
        "approval_gate": "human_approval_required_before_any_live_action",
        "risk_level": "medium",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "No live video submission or account actions without approval.",
    },
    "claude_metatrader": {
        "name": "Claude + MetaTrader",
        "type": "trading_integration",
        "category": "financial_automation",
        "value_hypothesis": "Claude-assisted trade analysis and strategy research on MetaTrader; paper/simulation only.",
        "status": "blocked_until_approval",
        "allowed_actions": ["read_docs", "paper_simulation_only", "research_strategy_concepts"],
        "forbidden_actions": [
            "live_trading", "real_money_orders", "autonomous_trade_execution",
            "connect_live_broker_account", "wire_to_runtime"
        ],
        "approval_gate": "human_approval_required_explicit_paper_simulation_gate_only",
        "risk_level": "high",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "Paper/simulation ONLY. No real money. No live broker connection. No autonomous trade execution. Ever.",
    },
    "claude_skills_docs": {
        "name": "Claude skills docs / Anthropic skills guide",
        "type": "documentation",
        "category": "claude_code_skills_reference",
        "value_hypothesis": "Official guide for building Claude Code skills and automations; Ghoti skill creation reference.",
        "status": "research_only",
        "allowed_actions": ["read_docs", "use_as_reference", "create_ghoti_skills"],
        "forbidden_actions": ["deploy_unapproved_skills", "bypass_approval_gates"],
        "approval_gate": "low_risk_doc_reference_only",
        "risk_level": "low",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "Anthropic official docs. Safe reference. Skill creation requires normal approval flow.",
    },
    "codex_automations_skills": {
        "name": "Codex automations / Codex skills",
        "type": "automation_framework",
        "category": "codex_claude_code_integration",
        "value_hypothesis": "Codex + Claude Code automation and skill pipeline for Ghoti CI/audit workflow.",
        "status": "research_only",
        "allowed_actions": ["read_docs", "design_automation_scaffold", "research_handoff_patterns"],
        "forbidden_actions": ["deploy_unapproved_automations", "bypass_human_review"],
        "approval_gate": "human_approval_required_before_live_automation",
        "risk_level": "low",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "After N+4.2 audit. No live automation without human review gate.",
    },
    "youtube_thumbnail_title": {
        "name": "YouTube thumbnail/title iteration workflow",
        "type": "content_optimization_workflow",
        "category": "supervised_content_pipeline",
        "value_hypothesis": "AI-assisted YouTube title and thumbnail iteration for supervised content MVP; operator reviews all outputs.",
        "status": "intake_only",
        "allowed_actions": ["research_workflow_design", "design_supervised_scaffold"],
        "forbidden_actions": [
            "autonomous_posting", "upload_without_approval", "live_youtube_api_calls",
            "automated_account_management"
        ],
        "approval_gate": "human_approval_required_before_any_upload_or_api_call",
        "risk_level": "medium",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "Future workflow -- no autonomous posting. YouTube Title/Thumbnail Iteration: future workflow, no autonomous posting.",
    },
    "internship_scraper": {
        "name": "Internship scraper / application assistant",
        "type": "job_application_assistant",
        "category": "career_automation",
        "value_hypothesis": "Assisted internship discovery and application drafting; human reviews and submits all applications.",
        "status": "blocked_until_approval",
        "allowed_actions": ["research_workflow_design", "draft_application_templates"],
        "forbidden_actions": [
            "autonomous_application_submission", "automated_account_creation",
            "scraping_without_tos_review", "bypass_human_review"
        ],
        "approval_gate": "human_approval_required_for_every_application_submission",
        "risk_level": "medium",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "Internship Scraper: future workflow, human approval required. TOS review required before any scraping.",
    },
    "ethical_hacking": {
        "name": "Ethical hacking with Linux + Claude",
        "type": "security_research_tool",
        "category": "cybersecurity_research",
        "value_hypothesis": "CTF challenges, authorized penetration testing, and security education with Claude assistance.",
        "status": "blocked_until_approval",
        "allowed_actions": ["ctf_challenges", "authorized_lab_environments", "security_education_research"],
        "forbidden_actions": [
            "unauthorized_target_attack", "production_system_testing_without_written_permission",
            "malware_creation", "illegal_access"
        ],
        "approval_gate": "legal_ctf_lab_authorized_only_human_approval_required",
        "risk_level": "high",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "Ethical Hacking: legal/CTF/lab/authorized-only. No unauthorized targets ever.",
    },
    "dolphin_local_models": {
        "name": "Dolphin / local less-restricted models",
        "type": "local_llm",
        "category": "local_model_research",
        "value_hypothesis": "Legitimate school research and local-only experimentation with less-restricted local models.",
        "status": "blocked_until_approval",
        "allowed_actions": ["legitimate_school_research", "local_only_experiments"],
        "forbidden_actions": [
            "use_for_harmful_content", "bypass_safety_guardrails_for_production",
            "use_without_academic_justification"
        ],
        "approval_gate": "human_approval_required_academic_use_only",
        "risk_level": "medium",
        "current_runtime_wiring": False,
        "clone_install_run_enabled": False,
        "live_account_action_enabled": False,
        "notes": "Dolphin/local model school research only. No bypass of safety gates for production use.",
    },
}

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

_BLOCKED_FLAGS = ["current_runtime_wiring", "clone_install_run_enabled", "live_account_action_enabled"]


def validate_catalog(catalog: dict) -> tuple[bool, list[str]]:
    """Return (ok, errors). Fails if any entry has a blocked flag set to True."""
    errors: list[str] = []
    for tool_id, entry in catalog.items():
        for flag in _BLOCKED_FLAGS:
            if entry.get(flag) is True:
                errors.append(
                    f"VALIDATION_FAIL: '{tool_id}' has {flag}=True — "
                    "no approval exists for N+4.2A. Must be False."
                )
    return (len(errors) == 0), errors


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_status(json_out: bool) -> int:
    ok, errors = validate_catalog(CATALOG)
    counts: dict[str, int] = {}
    for entry in CATALOG.values():
        s = entry.get("status", "unknown")
        counts[s] = counts.get(s, 0) + 1
    data = {
        "registry": "repo_skill_plugin_intake",
        "milestone": "N+4.2A",
        "tool_count": len(CATALOG),
        "status_counts": counts,
        "validation_ok": ok,
        "validation_errors": errors,
        "current_runtime_wiring_any": False,
        "clone_install_run_any": False,
        "live_account_action_any": False,
        "external_wiring_status": "none",
        "human_approval_required": True,
    }
    if json_out:
        print(json.dumps(data, indent=2))
    else:
        print("repo_skill_plugin_intake status")
        print(f"  tool_count:                  {len(CATALOG)}")
        for status, count in sorted(counts.items()):
            print(f"  status/{status}: {count}")
        print(f"  validation_ok:               {ok}")
        if errors:
            for e in errors:
                print(f"  ERROR: {e}")
        print(f"  current_runtime_wiring_any:  False")
        print(f"  clone_install_run_any:        False")
        print(f"  live_account_action_any:      False")
        print(f"  external_wiring_status:       none")
        print(f"  human_approval_required:      true")
    return 0 if ok else 1


def cmd_list(json_out: bool) -> int:
    if json_out:
        print(json.dumps(list(CATALOG.values()), indent=2))
    else:
        print(f"{'Name':<40} {'Category':<30} {'Status':<25} {'Risk'}")
        print("-" * 105)
        for entry in CATALOG.values():
            print(
                f"{entry['name']:<40} {entry['category']:<30} {entry['status']:<25} {entry['risk_level']}"
            )
    return 0


def cmd_validate(json_out: bool) -> int:
    ok, errors = validate_catalog(CATALOG)
    data = {"validation_ok": ok, "errors": errors, "checked_flags": _BLOCKED_FLAGS}
    if json_out:
        print(json.dumps(data, indent=2))
    else:
        if ok:
            print(f"VALIDATION PASS: all {len(CATALOG)} entries have all blocked flags = False.")
            print(f"  checked_flags: {', '.join(_BLOCKED_FLAGS)}")
        else:
            print("VALIDATION FAIL:")
            for e in errors:
                print(f"  {e}")
    return 0 if ok else 1


def cmd_json_dump() -> int:
    print(json.dumps(CATALOG, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Repo/Skill/Plugin Intake Registry (N+4.2A) -- intake/planning only, no clone/install/run."
    )
    parser.add_argument("--status", action="store_true", help="Show registry summary and validation.")
    parser.add_argument("--list", action="store_true", help="List all registry entries.")
    parser.add_argument("--validate-config", action="store_true", help="Validate that no entry has blocked flags=True.")
    parser.add_argument("--json", dest="json_out", action="store_true", help="Force JSON output.")
    args = parser.parse_args()

    if args.validate_config:
        return cmd_validate(args.json_out)
    if args.list:
        return cmd_list(args.json_out)
    if args.status:
        return cmd_status(args.json_out)

    # Default: JSON dump of full catalog
    return cmd_json_dump()


if __name__ == "__main__":
    sys.exit(main())