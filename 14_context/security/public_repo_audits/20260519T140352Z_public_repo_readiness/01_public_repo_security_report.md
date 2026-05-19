# Public Repo Security Report

- Total checks: 136
- Passed: 110
- Failed: 0
- Warnings: 26
- safe_to_make_public: true
- human_review_required: true

## Blocking Findings
- None.

## Warning Findings
- browser profile/session scan at 04_docs/plans/assistant-stack-options.md:96 value=[REDACTED]
- browser profile/session scan at 04_docs/plans/github-plan.md:80 value=[REDACTED]
- browser profile/session scan at 14_context/00_main_memory/local-vs-sync-boundaries.md:8 value=[REDACTED]
- browser profile/session scan at 14_context/codex_cua_sandbox_profile_review_n3_5.md:76 value=[REDACTED]
- browser profile/session scan at 14_context/codex_n3_14_paperclip_source_audit.md:162 value=[REDACTED]
- browser profile/session scan at 14_context/codex_openfang_screenpipe_audit_n3_3.md:45 value=[REDACTED]
- browser profile/session scan at 14_context/codex_openfang_screenpipe_audit_n3_3.md:84 value=[REDACTED]
- browser profile/session scan at 14_context/codex_openfang_screenpipe_audit_n3_3.md:93 value=[REDACTED]
- browser profile/session scan at 14_context/computer_use_candidate_ranking_n3_2_codex.md:39 value=[REDACTED]
- browser profile/session scan at 14_context/computer_use_candidate_ranking_n3_2_codex.md:86 value=[REDACTED]
- browser profile/session scan at 14_context/cua_image_digest_gate_n3_11.md:94 value=[REDACTED]
- browser profile/session scan at 14_context/security/public_repo_audits/20260519T134917Z_public_repo_readiness/01_public_repo_security_report.md:14 value=[REDACTED]
- browser profile/session scan at 14_context/security/public_repo_audits/20260519T134917Z_public_repo_readiness/01_public_repo_security_report.md:15 value=[REDACTED]
- browser profile/session scan at 14_context/security/public_repo_audits/20260519T134917Z_public_repo_readiness/01_public_repo_security_report.md:16 value=[REDACTED]
- browser profile/session scan at 14_context/security/public_repo_audits/20260519T134917Z_public_repo_readiness/01_public_repo_security_report.md:17 value=[REDACTED]
- browser profile/session scan at 14_context/security/public_repo_audits/20260519T134917Z_public_repo_readiness/01_public_repo_security_report.md:18 value=[REDACTED]
- browser profile/session scan at 14_context/security/public_repo_audits/20260519T134917Z_public_repo_readiness/01_public_repo_security_report.md:19 value=[REDACTED]
- browser profile/session scan at 14_context/security/public_repo_audits/20260519T134917Z_public_repo_readiness/01_public_repo_security_report.md:20 value=[REDACTED]
- browser profile/session scan at 14_context/security/public_repo_audits/20260519T134917Z_public_repo_readiness/01_public_repo_security_report.md:21 value=[REDACTED]
- browser profile/session scan at 14_context/security/public_repo_audits/20260519T134917Z_public_repo_readiness/01_public_repo_security_report.md:22 value=[REDACTED]
- DB dump scan at 03_scripts/public_repo_security_audit.py:32 value=[REDACTED]
- SQLite runtime DB scan at .gitignore:13 value=[REDACTED]
- SQLite runtime DB scan at .gitignore:14 value=[REDACTED]
- SQLite runtime DB scan at .gitignore:58 value=[REDACTED]
- SQLite runtime DB scan at 01_projects/runtime_mvp/tests/test_n5_1a_public_github_readiness_image_backed_presentation.py:138 value=[REDACTED]
- SQLite runtime DB scan at 01_projects/runtime_mvp/tests/test_n5_1a_public_github_readiness_image_backed_presentation.py:139 value=[REDACTED]
- SQLite runtime DB scan at 03_scripts/public_repo_security_audit.py:32 value=[REDACTED]
- SQLite runtime DB scan at 14_context/loc_count_crosscheck_n3_2_codex.md:77 value=[REDACTED]
- markdown secret scan at 01_projects/runtime_mvp/tests/test_n4_4b_desktop_operator_dashboard_action_center.py:123 value=[REDACTED]
- markdown secret scan at 01_projects/runtime_mvp/tests/test_n4_4b_desktop_operator_dashboard_action_center.py:124 value=[REDACTED]
- markdown secret scan at 01_projects/runtime_mvp/tests/test_n4_4c_desktop_operator_recipe_runner_preview_polish.py:150 value=[REDACTED]
- markdown secret scan at 03_scripts/desktop_operator_control_plane.py:629 value=[REDACTED]
- markdown secret scan at 14_context/autobrowser_isolated_clone_audit.md:87 value=[REDACTED]
- docs credential scan at .claude/settings.json:25 value=[REDACTED]
- docs credential scan at .gitignore:1 value=[REDACTED]
- docs credential scan at .gitignore:5 value=[REDACTED]
- docs credential scan at .gitignore:6 value=[REDACTED]
- docs credential scan at 01_projects/dashboard_mvp/public/index.html:494 value=[REDACTED]
- docs credential scan at 01_projects/dashboard_mvp/public/index.html:742 value=[REDACTED]
- docs credential scan at 01_projects/dashboard_mvp/server.js:235 value=[REDACTED]
- docs credential scan at 01_projects/dashboard_mvp/server.js:6335 value=[REDACTED]
- docs credential scan at 01_projects/dashboard_mvp/server.js:6336 value=[REDACTED]
- docs credential scan at 01_projects/runtime_mvp/src/super_ai_agent/action_audit.py:5 value=[REDACTED]
- docs credential scan at 01_projects/runtime_mvp/src/super_ai_agent/action_intent.py:38 value=[REDACTED]
- docs credential scan at 01_projects/runtime_mvp/src/super_ai_agent/action_intent.py:62 value=[REDACTED]
- docs credential scan at 01_projects/runtime_mvp/src/super_ai_agent/multi_agent_mvp.py:26 value=[REDACTED]
- docs credential scan at 01_projects/runtime_mvp/src/super_ai_agent/multi_agent_mvp.py:232 value=[REDACTED]
- docs credential scan at 01_projects/runtime_mvp/src/super_ai_agent/publishability.py:14 value=[REDACTED]
- docs credential scan at 01_projects/runtime_mvp/src/super_ai_agent/publishability.py:105 value=[REDACTED]
- docs credential scan at 01_projects/runtime_mvp/src/super_ai_agent/publishability.py:115 value=[REDACTED]
- docs credential scan at 01_projects/runtime_mvp/src/super_ai_agent/publishability.py:119 value=[REDACTED]
- docs credential scan at 01_projects/runtime_mvp/src/super_ai_agent/publishability.py:184 value=[REDACTED]
- docs credential scan at 01_projects/runtime_mvp/src/super_ai_agent/wait_resume_supervisor.py:377 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T134917Z_public_repo_readiness/01_public_repo_security_report.md:153 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T134917Z_public_repo_readiness/02_public_repo_security_report.json:2234 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135124Z_public_repo_readiness/01_public_repo_security_report.md:67 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135124Z_public_repo_readiness/01_public_repo_security_report.md:68 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135124Z_public_repo_readiness/01_public_repo_security_report.md:153 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135124Z_public_repo_readiness/02_public_repo_security_report.json:436 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135124Z_public_repo_readiness/02_public_repo_security_report.json:444 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135124Z_public_repo_readiness/02_public_repo_security_report.json:2682 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135234Z_public_repo_readiness/01_public_repo_security_report.md:67 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135234Z_public_repo_readiness/01_public_repo_security_report.md:68 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135234Z_public_repo_readiness/01_public_repo_security_report.md:69 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135234Z_public_repo_readiness/01_public_repo_security_report.md:70 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135234Z_public_repo_readiness/01_public_repo_security_report.md:71 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135234Z_public_repo_readiness/01_public_repo_security_report.md:72 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135234Z_public_repo_readiness/01_public_repo_security_report.md:73 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135234Z_public_repo_readiness/01_public_repo_security_report.md:74 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135234Z_public_repo_readiness/01_public_repo_security_report.md:153 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135234Z_public_repo_readiness/02_public_repo_security_report.json:436 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135234Z_public_repo_readiness/02_public_repo_security_report.json:444 value=[REDACTED]
- Docker secrets scan at 14_context/security/public_repo_audits/20260519T135234Z_public_repo_readiness/02_public_repo_security_report.json:452 value=[REDACTED]
- GitHub Actions secrets scan at 03_scripts/approved_adapter_runner.py:207 value=[REDACTED]
- GitHub Actions secrets scan at 03_scripts/approved_adapter_runner.py:209 value=[REDACTED]
- command history scan at 14_context/security/public_repo_audits/20260519T134917Z_public_repo_readiness/01_public_repo_security_report.md:155 value=[REDACTED]
- command history scan at 14_context/security/public_repo_audits/20260519T134917Z_public_repo_readiness/02_public_repo_security_report.json:2250 value=[REDACTED]
- command history scan at 14_context/security/public_repo_audits/20260519T135124Z_public_repo_readiness/01_public_repo_security_report.md:71 value=[REDACTED]
- command history scan at 14_context/security/public_repo_audits/20260519T135124Z_public_repo_readiness/01_public_repo_security_report.md:72 value=[REDACTED]
- command history scan at 14_context/security/public_repo_audits/20260519T135124Z_public_repo_readiness/01_public_repo_security_report.md:155 value=[REDACTED]

## Check Summary
| ID | Status | Category | Name |
|---:|---|---|---|
| 1 | PASS | env | .env.example exists |
| 2 | PASS | env | .env.example has placeholders only |
| 3 | PASS | env | .env not tracked |
| 4 | PASS | env | .env.local not tracked |
| 5 | PASS | env | .env.production not tracked |
| 6 | PASS | gitignore | .gitignore exists |
| 7 | PASS | gitignore | .env files ignored |
| 8 | PASS | gitignore | .gitignore covers env files |
| 9 | PASS | gitignore | .gitignore covers logs |
| 10 | PASS | gitignore | .gitignore covers temp files |
| 11 | PASS | gitignore | .gitignore covers cache folders |
| 12 | PASS | gitignore | .gitignore covers node_modules |
| 13 | PASS | gitignore | .gitignore covers Python venvs |
| 14 | PASS | gitignore | .gitignore covers runtime_data |
| 15 | PASS | gitignore | .gitignore covers output |
| 16 | PASS | gitignore | .gitignore covers third_party sandbox |
| 17 | PASS | gitignore | .gitignore covers human imported stuff |
| 18 | PASS | gitignore | .gitignore covers archive files |
| 19 | PASS | gitignore | .gitignore covers model weights |
| 20 | PASS | gitignore | .gitignore covers screenshots/raw imports |
| 21 | PASS | human_imports | human imported raw files not tracked |
| 22 | PASS | env | no hidden .env committed |
| 23 | PASS | files | large files scan |
| 24 | PASS | files | binary files scan |
| 25 | PASS | files | archive scan |
| 26 | PASS | files | model weights scan |
| 27 | PASS | files | copyrighted video/media tracked file scan |
| 28 | PASS | files | runtime DB/dump tracked file scan |
| 29 | PASS | files | key/certificate tracked file scan |
| 1 | PASS | secrets | OpenAI key pattern scan |
| 2 | PASS | secrets | Anthropic key pattern scan |
| 3 | PASS | secrets | Gemini/Google key pattern scan |
| 4 | PASS | secrets | GitHub token pattern scan |
| 5 | PASS | secrets | AWS key pattern scan |
| 6 | PASS | secrets | Azure key pattern scan |
| 7 | PASS | secrets | Supabase key pattern scan |
| 8 | PASS | secrets | Firebase key pattern scan |
| 9 | PASS | secrets | Stripe key pattern scan |
| 10 | PASS | secrets | Discord token pattern scan |
| 11 | PASS | secrets | Telegram token pattern scan |
| 12 | PASS | secrets | OAuth secret scan |
| 13 | PASS | secrets | private key scan |
| 14 | PASS | secrets | SSH key scan |
| 15 | PASS | secrets | PEM scan |
| 16 | PASS | secrets | certificate scan |
| 17 | PASS | privacy | cookie/session scan |
| 18 | WARN | privacy | browser profile/session scan |
| 19 | WARN | privacy | DB dump scan |
| 20 | WARN | privacy | SQLite runtime DB scan |
| 21 | PASS | secrets | JSON token scan |
| 22 | PASS | secrets | YAML secret scan |
| 23 | WARN | secrets | markdown secret scan |
| 24 | WARN | secrets | docs credential scan |
| 25 | PASS | secrets | .npmrc token scan |
| 26 | PASS | secrets | pip config scan |
| 27 | WARN | secrets | Docker secrets scan |
| 28 | WARN | secrets | GitHub Actions secrets scan |
| 29 | WARN | privacy | command history scan |
| 30 | PASS | privacy | PowerShell history warning |
| 31 | WARN | privacy | clipboard dump scan |
| 32 | WARN | privacy | transcript dump scan |
| 33 | WARN | media | copyrighted video/media scan |
| 34 | WARN | media | raw YouTube download scan |
| 35 | WARN | media | video downloader wrapper scan |
| 36 | WARN | runtime | live API URL warning |
| 37 | WARN | runtime | unsafe JS child process option scan |
| 38 | PASS | runtime | execSync scan |
| 39 | WARN | runtime | child_process usage review |
| 40 | WARN | runtime | subprocess shell option scan |
| 41 | PASS | runtime | os.system scan |
| 42 | WARN | runtime | eval scan |
| 43 | PASS | runtime | broad taskkill scan |
| 44 | WARN | runtime | rm recursive force scan |
| 45 | WARN | runtime | deletion command scan |
| 46 | WARN | runtime | external repo runtime wiring scan |
| 47 | WARN | runtime | UI-TARS click/type/control claim scan |
| 48 | WARN | runtime | live account action claim scan |
| 49 | WARN | runtime | money/trading claim scan |
| 50 | WARN | runtime | posting/upload claim scan |
| 51 | WARN | runtime | autonomous Claude/Codex launch claim scan |
| 1 | PASS | docs | README.md exists |
| 2 | PASS | docs | LICENSE exists |
| 3 | PASS | docs | .env.example exists |
| 4 | PASS | docs | .gitignore exists |
| 5 | PASS | docs | SECURITY.md exists |
| 6 | PASS | docs | CONTRIBUTING.md exists |
| 7 | PASS | docs | docs/PUBLIC_RELEASE_SECURITY_CHECKLIST.md exists |
| 8 | PASS | docs | docs/HUMAN_IMPORTED_STUFF_POLICY.md exists |
| 9 | PASS | docs | docs/DIAGRAM_UPDATE_RULE.md exists |
| 10 | PASS | docs | docs/FUTURE_MILESTONE_DOCS_CHECKLIST.md exists |
| 11 | PASS | docs | docs/GITHUB_PRESENTATION_CHECKLIST.md exists |
| 12 | PASS | docs | docs/assets/github/README.md exists |
| 13 | PASS | readme | README truthfulness scan |
| 14 | PASS | readme | README says not open source |
| 15 | PASS | license | LICENSE exists |
| 16 | PASS | license | LICENSE is not permissive open source |
| 17 | PASS | security | SECURITY.md exists |
| 18 | PASS | contributing | CONTRIBUTING.md exists |
| 19 | PASS | docs | docs folder exists |
| 20 | PASS | docs | public release checklist exists |
| 21 | PASS | docs | human imported stuff policy exists |
| 22 | PASS | docs | diagram update rule exists |
| 23 | PASS | docs | future milestone docs checklist exists |
| 24 | PASS | docs | GitHub presentation checklist exists |
| 25 | PASS | readme | GitHub presentation checklist present |
| 26 | PASS | readme | quickstart present |
| 27 | PASS | readme | dashboard command present |
| 28 | PASS | readme | safety section present |
| 29 | PASS | readme | limitations section present |
| 30 | PASS | readme | roadmap present |
| 31 | PASS | readme | approval gate docs present |
| 32 | PASS | readme | audit log docs present |
| 33 | PASS | readme | public repo description suggestion present |
| 34 | PASS | readme | GitHub topics suggestion present |
| 35 | PASS | docs | issue template suggestion |
| 36 | PASS | docs | PR template suggestion |
| 37 | PASS | docs | dependency lockfile review |
| 38 | PASS | docs | package scripts review |
| 39 | PASS | docs | Python requirements review |
| 40 | PASS | docs | generated artifact policy |
| 41 | PASS | docs | sandbox clone policy |
| 42 | PASS | docs | adapter execution policy |
| 43 | PASS | privacy | raw user private data scan |
| 44 | PASS | privacy | school/private docs accidental commit scan |
| 45 | PASS | privacy | CV/private docs accidental commit scan |
| 46 | PASS | privacy | account screenshots accidental commit scan |
| 47 | PASS | assets | curated docs/assets images only |
| 48 | PASS | assets | README image links valid |
| 49 | PASS | assets | no API keys in copied images filenames/metadata names |
| 50 | PASS | reports | no secrets printed in security reports |
| 51 | PASS | readiness | readiness stays 100 if script validators exist |
| 52 | PASS | docs | docs/PUBLIC_RELEASE_SECURITY_CHECKLIST.md tracked or staged |
| 53 | PASS | docs | docs/HUMAN_IMPORTED_STUFF_POLICY.md tracked or staged |
| 54 | PASS | docs | docs/DIAGRAM_UPDATE_RULE.md tracked or staged |
| 55 | PASS | docs | docs/FUTURE_MILESTONE_DOCS_CHECKLIST.md tracked or staged |
| 56 | PASS | docs | docs/GITHUB_PRESENTATION_CHECKLIST.md tracked or staged |
