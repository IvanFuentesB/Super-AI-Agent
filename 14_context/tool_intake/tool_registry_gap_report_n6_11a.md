# Tool Registry Gap Report N+6.11A

Origin main: `fbd64d6ebe03527107ba8f5000d84770c6cc7753`

## Summary

- Total candidates inventoried: 79
- Present in current N+6.7A registry: 17
- Missing from current N+6.7A registry: 62
- Critical/high missing candidates: 12

## Critical/High Missing

- Ruflo (critical, local_brain_bridge)
- Computer-use stack (critical, safe_computer_use)
- Hermes Agent (critical, local_coordinator)
- Obsidian (critical, durable_memory)
- Gemma/Ollama (critical, local_model)
- Llama Hermes coordinator (high, local_coordinator_model)
- TryCUA / CUA Driver (high, computer_use_driver)
- Odysseus (high, ai_workspace_patterns)
- multica-ai/andrej-karpathy-skills (high, agent_skills)
- Karpathy CLAUDE.md (high, coding_guidelines)
- Content clipping / AI video workflows (high, content_business)
- OpenFang / MoneyPrinter (high, content_business)

## All Missing

- Ruflo (critical, local_brain_bridge)
- Computer-use stack (critical, safe_computer_use)
- Hermes Agent (critical, local_coordinator)
- Obsidian (critical, durable_memory)
- Gemma/Ollama (critical, local_model)
- Llama Hermes coordinator (high, local_coordinator_model)
- TryCUA / CUA Driver (high, computer_use_driver)
- Odysseus (high, ai_workspace_patterns)
- multica-ai/andrej-karpathy-skills (high, agent_skills)
- Karpathy CLAUDE.md (high, coding_guidelines)
- Content clipping / AI video workflows (high, content_business)
- OpenFang / MoneyPrinter (high, content_business)
- Claude Design (medium, dashboard_design)
- UI/UX Pro Max Skill (medium, dashboard_design)
- Rowboat (medium, agent_orchestration)
- FreeDomain (medium, business_websites)
- Agentic OS (medium, agent_os)
- CodexBar (medium, codex_ui)
- Nvidia Locate-Anything (medium, vision)
- Dexter (medium, robotics_or_agent)
- Speckit (medium, spec_workflow)
- Paperweight (medium, agent_or_workflow)
- Phodal Routa (medium, repo_understanding)
- AIEngineer Coach (medium, learning_or_coaching)
- AI Factory (medium, agent_factory)
- Insforge (medium, backend_infra)
- NotebookLM (medium, research_memory)
- Weavy (medium, collaboration)
- Automatic AI editing repos (medium, content_video)
- PDF contact solver (medium, document_extraction)
- Free-domain websites (medium, business_websites)
- Screenpipe (medium, local_capture)
- Playwright (medium, browser_testing)
- Claw-code / OpenClaw (medium, coding_agent_reference)
- Aider (medium, coding_agent_reference)
- Whisper/Vosk offline speech (medium, offline_speech)
- Soap2Soap (later, unknown_candidate)
- Cadom (later, unknown_candidate)
- University of Michigan ROB 311 (later, robotics_learning)
- HEADRON (later, unknown_candidate)
- RuView (later, unknown_candidate)
- RMUX (later, terminal_or_mux)
- Polsia AI (later, unknown_candidate)
- Pascal Editor (later, editor)
- Google Omni (later, unknown_or_model)
- Zozo physics engine (later, simulation)
- Electronic Monk drone building (later, hardware_learning)
- Dora / robotics middleware (later, robotics)
- Unsloth (later, model_training)
- MiroFish (later, simulation_or_prediction)
- Picoclaw / robotics references (later, robotics)
- Blueprint.am (later, unknown_or_infra)
- Cloud infra stack (later, cloud_infra)
- Anus CLI (blocked, unknown_cli)
- OSINT/Kali (blocked, offensive_security)
- HTTrack / webscraper (blocked, web_scraping)
- Manychat (blocked, messaging_automation)
- Telegram bot affiliate program (blocked, business_messaging)
- AI/agent dropshipping (blocked, business_commerce)
- TikTok Shop dropshipping (blocked, business_commerce)
- Browser-use (blocked, browser_agent)
- Kronos / market model (blocked, financial_model)

## Registry Update Recommendation

Do not overwrite `tool_candidate_registry.json` automatically. Review `proposed_tool_candidate_registry_update_n6_11a.json`, then merge missing items in a dedicated registry-update milestone with tests.

## Highest Priority Gaps

- Ruflo: clone_static_inspect - Recover prior Ruflo notes, verify source/status, then static README/license/file-tree inspection only.
- Computer-use stack: blocked_review - Inventory stack only; keep observation-only fixtures; no click/type/browser actions.
- Hermes Agent: document_only - Use safe WSL/status probes and wrapper status scripts only.
- Obsidian: document_only - Keep repo-local vault and markdown handoff files; no plugin install.
- Gemma/Ollama: document_only - Keep using guarded local tasks only; no extra pulls unless approved.
- Llama Hermes coordinator: document_only - Record model availability and intended coordinator role; no daemon/live routing.
- TryCUA / CUA Driver: clone_static_inspect - Static source and platform-fit review; no desktop control.
- Odysseus: document_only - Keep idea extraction docs; no clone/install/run.
- multica-ai/andrej-karpathy-skills: clone_static_inspect - Static README/license review; compare against local skills policy.
- Karpathy CLAUDE.md: document_only - Keep as policy/guideline intake; no blind skill install.
- Content clipping / AI video workflows: clone_static_inspect - Static inspect OpenFang/MoneyPrinter/content tools; fixture-only; no posting.
- OpenFang / MoneyPrinter: clone_static_inspect - Static inspect and keep draft-only/local outputs; no posting.
