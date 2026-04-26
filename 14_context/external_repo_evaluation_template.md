# External Repo / Tool Evaluation Template

Date: 2026-04-26
Branch: feat/ghoti-visible-operator-stack
Status label: evaluation_template_created / verification_only / not_runtime_wired

## Purpose

Use this template before cloning, installing, running, paying for, deploying, or wiring any external repo, tool, service, model, MCP server, or agent framework into Ghoti.

This is an evaluation workflow only. It does not approve integration, does not authorize runtime use, and does not weaken Ghoti's supervised/manual/approval-gated boundaries.

## Evaluation Record

### Basic Identity

- Repo/tool name:
- Source URL:
- Vendor / owner:
- Category:
- Date evaluated:
- Evaluator:
- Status label:

### Purpose Truth

- Claimed purpose:
- Real purpose after inspection:
- What Ghoti capability this might support:
- What it does not do:
- Is it runtime-wired today? NO unless proven:

### License / Ownership

- License:
- Commercial-use clarity:
- Copyleft/AGPL implications:
- Attribution requirements:
- Unknowns:

### Risk Review

- Security risk:
- TOS/legal risk:
- Privacy/PII risk:
- Supply-chain risk:
- Abuse risk:
- Autonomous-action risk:
- Paid/cloud-service risk:

### Runtime Requirements

- Operating system support:
- Windows compatibility:
- Rust requirements:
- Python requirements:
- Node requirements:
- Docker requirements:
- GPU/model requirements:
- Background service requirements:
- Browser requirements:
- Other native dependencies:

### Account / Auth / Secrets

- Accounts required:
- API keys required:
- OAuth/browser login required:
- Paid plan required:
- Data sent outside local machine:
- Local-only feasibility:
- Secret-handling plan:

### Approval Gates

- Clone approval required:
- Install approval required:
- Run approval required:
- Account/auth approval required:
- Paid/cloud approval required:
- Runtime-integration approval required:
- Approval queue / manual review needed before any external action:

### Test Plan

- Read-only docs/license review:
- Isolated clone path:
- Dependency audit:
- Offline/local smoke test:
- Network access test:
- Windows compatibility test:
- Safety-boundary test:
- Rollback test:
- Generated/runtime artifact handling:

### Decisions

- Clone/install decision: `not_decided | approved_to_clone | approved_to_install | denied`
- Integration decision: `not_runtime_wired | research_only | prototype_only | candidate_for_supervised_integration | blocked`
- Final verdict: `use now | use soon | research only | blocked`
- Required next milestone:

### Rollback Plan

- Files/directories created:
- Services/processes started:
- Environment variables changed:
- Accounts/tokens used:
- Cleanup command(s):
- Gitignore/update needed:

## Required Final Verdict Labels

Use one:

- `use now` — safe to use as-is for operator-side research/docs with no runtime wiring.
- `use soon` — promising, but needs a narrow approved follow-up.
- `research only` — keep as reference; no clone/install/runtime wiring yet.
- `blocked` — do not use because of safety, legal, TOS, license, privacy, or operational risk.

## Non-Negotiable Boundaries

- No cloning or installing without explicit operator approval.
- No runtime wiring in the evaluation milestone.
- No autonomous external actions.
- No hidden browser control, stealth, cap bypass, fake engagement, spam, credential abuse, or unauthorized scraping.
- No paid/cloud service connection without explicit approval.
- No personal-data collection unless legal, necessary, minimal, and approved.
- No staging runtime artifacts, generated output, screenshots, third-party repo contents, secrets, or local scratch files.

## Current Status

- Template status: `evaluation_template_created / verification_only / not_runtime_wired`
- Repos cloned by this template: NO
- Tools installed by this template: NO
- Runtime wired by this template: NO
