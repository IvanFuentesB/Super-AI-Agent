# N+4.2A Repo / Skill / Plugin Intake Registry

**Milestone:** N+4.2A  
**Script:** `03_scripts/repo_skill_plugin_intake.py`  
**Config:** `23_configs/repo_skill_plugin_intake.example.json`  
**Date:** 2026-05-12  
**Status:** IMPLEMENTED  

---

## Safety Summary

| Flag | Value |
|---|---|
| `current_runtime_wiring` (any entry) | **false** |
| `clone_install_run_enabled` (any entry) | **false** |
| `live_account_action_enabled` (any entry) | **false** |
| External wiring status | **none** |
| Human approval required | **yes** |
| Approval required before clone/install/run | **yes** |
| Autonomous posting | **disabled** |
| Autonomous money movement | **disabled** |

---

## Registry Entries (22 tools)

| Name | Category | Status | Risk |
|---|---|---|---|
| UI-TARS | vision_ui_automation | intake_only | medium |
| The Agency | agent_orchestration | intake_only | medium |
| agent-skills-eval | skill_evaluation | intake_only | low |
| arcads-claude-code | video_ad_generation | intake_only | medium |
| Weavy | embedded_collaboration | intake_only | medium |
| Manychat | messaging_automation | intake_only | high |
| OpenFang/MoneyPrinter | automated_content_pipeline | intake_only | medium |
| AirLLM | local_model_runner | intake_only | low |
| Mermaid | documentation_tool | research_only | low |
| Claude Cowork | ai_collaboration_platform | intake_only | low |
| Speckit | product_documentation | intake_only | low |
| Sigmap | signal_mapping | intake_only | medium |
| Anvac | agent_testing | intake_only | low |
| Agent Exchange / AEX | agent_discovery_exchange | intake_only | medium |
| Vouch | video_content_platform | intake_only | medium |
| Claude + MetaTrader | financial_automation | blocked_until_approval | high |
| Claude skills docs / Anthropic skills guide | claude_code_skills_reference | research_only | low |
| Codex automations / Codex skills | codex_claude_code_integration | research_only | low |
| YouTube thumbnail/title iteration | supervised_content_pipeline | intake_only | medium |
| Internship scraper / application assistant | career_automation | blocked_until_approval | medium |
| Ethical hacking with Linux + Claude | cybersecurity_research | blocked_until_approval | high |
| Dolphin / local model school research | local_model_research | blocked_until_approval | medium |

---

## Special Safety Notes

### Claude + MetaTrader
- **Trading / MetaTrader: paper/simulation only**
- No real money. No live broker connection. No autonomous trade execution. Ever.
- Approval gate: `human_approval_required_explicit_paper_simulation_gate_only`

### YouTube Thumbnail/Title Iteration
- **YouTube Title/Thumbnail Iteration: future workflow, no autonomous posting**
- Human reviews and approves all uploads.
- No YouTube API calls without explicit human approval.

### Internship Scraper / Application Assistant
- **Internship Scraper: future workflow, human approval required**
- Human reviews and submits every application.
- TOS review required before any scraping.

### Ethical Hacking with Linux + Claude
- **Ethical Hacking: legal/CTF/lab/authorized-only**
- No unauthorized targets. No production systems without written permission.

### Dolphin / Local Models
- Legitimate school research only.
- No bypass of safety gates for production use.

---

## Validation

```
python 03_scripts/repo_skill_plugin_intake.py --validate-config
# Expected: VALIDATION PASS: all 22 entries have all blocked flags = False.

python 03_scripts/repo_skill_plugin_intake.py --status
# Expected: tool_count: 22, validation_ok: True, external_wiring_status: none
```

---

## CLI Reference

```
python 03_scripts/repo_skill_plugin_intake.py --status
python 03_scripts/repo_skill_plugin_intake.py --list
python 03_scripts/repo_skill_plugin_intake.py --validate-config
python 03_scripts/repo_skill_plugin_intake.py --json
```