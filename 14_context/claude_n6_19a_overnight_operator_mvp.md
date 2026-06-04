# Ghoti N+6.19A - Overnight Operator MVP + ECC/GBrain/Documenso Repo Extraction

## Verdict

IMPLEMENTED / READY FOR CODEX AUDIT

Branch: `feat/ghoti-agent-claude-n6-19a-overnight-operator-mvp`

Dependency: N+6.18B operator dashboard is on `origin/main` at `cf006bf841480abd131d211fefba9d056348241a`.

## Skills

Skills detected: Codex skill registry includes git worktree, verification, security/audit, documentation, Python/PowerShell, agent workflow, browser/computer-use, UI/design, cloud, deployment, data, and connector-oriented skills.

Skills used:

- `using-git-worktrees`: followed the isolated worktree pattern and continued the repo-contained worktree.
- `verification-before-completion`: validation is required before claiming completion.

Skills ignored:

- UI/UX/design skills: no broad UI work in this milestone.
- Browser/Playwright/Vercel agent-browser skills: live browser control is explicitly blocked.
- Cloud/deploy/database/payment/calendar/Notion skills: out of scope and would risk live setup or external services.
- Image/document generation skills: not needed for this repo-local milestone.

Skill instructions changed implementation by keeping work isolated, pushing feature branch only, and requiring fresh verification before success claims.

## ECC Result

ECC source: `https://github.com/affaan-m/ecc`

Clone path: `21_repos/third_party_runtime_sandbox/ecc`

Observed commit: `0f84c0e2796703fbda87d577b2636351418c7442`

ECC cloned successfully into the ignored runtime sandbox. Static scan found high-review patterns, so ECC runtime execution is blocked. Read-only metadata commands ran successfully. ECC inspector found agents, skills, rules, commands, hooks, MCP configuration surfaces, security scanner material, and prompt rules.

Reports:

- `14_context/overnight_operator/repo_execution_reports/ecc_n6_19a.md`
- `14_context/overnight_operator/repo_execution_reports/ecc_extraction_plan_n6_19a.md`
- `14_context/skills/ecc_inspired_agent_setup_n6_19a.md`

## GBrain Result

GBrain source: `https://github.com/garrytan/gbrain`

Clone path: `21_repos/third_party_runtime_sandbox/gbrain`

Observed commit: `9a0bae8d62cdd1e0dd6655e24e082fe6c69c5dac`

GBrain cloned successfully into the ignored runtime sandbox. Static scan found high-review patterns, so GBrain runtime execution is blocked. Read-only metadata commands ran successfully. Useful patterns include `gbrain.yml`, skills, docs, MCP notes, integration docs, tutorials, recipes, and brain/capture-oriented skills.

Reports:

- `14_context/overnight_operator/repo_execution_reports/gbrain_n6_19a.md`
- `14_context/overnight_operator/repo_execution_reports/gbrain_memory_extraction_plan_n6_19a.md`

## Documenso vs Overleaf

Documenso is classified as signing, approval workflow, contracts, and evidence trail tooling.

Overleaf is classified as collaborative LaTeX, technical report writing, university papers, and project documentation.

Recommendation: build Overleaf/LaTeX report helper first for university and technical reports; add Documenso later for signed agreements, approvals, and business contracts.

Doc: `docs/GHOTI_DOCUMENSO_VS_OVERLEAF_PROJECT_DOCS.md`

## MarkItDown Result

MarkItDown source: `https://github.com/microsoft/markitdown`

Clone path: `21_repos/third_party_runtime_sandbox/markitdown`

Observed commit: `e144e0a2be95b34df17433bac904e635f2c5e551`

MarkItDown cloned successfully and read-only metadata commands ran. Static scan blocks install/runtime execution for this milestone. It remains the preferred future PDF/doc-to-Markdown candidate after a separate isolated venv milestone.

Report: `14_context/overnight_operator/repo_execution_reports/markitdown_n6_19a.md`

## Prompt Packet And Clipboard Relay

Prompt packet builder can render local task JSON into Markdown packets and write local outbox packets.

Clipboard relay supports dry-run and explicit local copy only. It does not paste into apps, submit forms, focus windows, or click/type.

## What Remains Disabled

- live app paste
- auto-submit
- OS-level click/type
- live browser automation
- Telegram `/run`
- MCP setup
- live agent launch
- provider token setup
- Docker/container execution
- arbitrary command execution
- third-party package install
- Git main push/merge from the operator

## Validation

Validation commands were run during feature development and must be repeated by Codex in the N+6.19B audit merge gate:

- N+6 runtime tests
- repo sandbox list/static scans
- ECC inspector
- prompt packet builder
- clipboard relay dry-run
- overnight operator PowerShell check
- public repo security audit
- product launcher status/context/repo-map

## Next Milestone

N+6.20A approved-window copy/paste harness using ECC/GBrain-informed workflow.

The next milestone may prepare human-approved app-window paste, but must still block auto-submit and every live account action.
