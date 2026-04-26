# External Operator Candidates Audit

Date: 2026-04-26
Branch: feat/ghoti-visible-operator-stack
Status label: operator_candidate_audit / research_only / not_runtime_wired

## Purpose

Compare external operator-adjacent candidates before Ghoti clones, installs, runs, or wires anything into runtime.

This audit is intentionally conservative. It treats external tools as references or future isolated-evaluation candidates only. Nothing here authorizes autonomous execution, hidden browser control, paid/cloud integrations, scraping abuse, credential use, or runtime wiring.

## Current Verdict

Ghoti should not wire any external operator candidate directly into runtime yet.

The safest implementation direction is:

1. Build Ghoti's own small operator contract first: action schema, approval gate, audit log, capability allowlist, adapter interface, and local-only state.
2. Use external tools as references or isolated experiments only.
3. Evaluate Auto Browser first if a browser-control candidate is needed.
4. Keep RUFLO research-only until its security/trust concerns are resolved by source audit and isolated testing.
5. Treat Obscura as research-only or blocked for Ghoti runtime until the project can prove legal/TOS-safe, non-stealth use.

## Candidate Ranking

| Candidate | Category | Current verdict | Why |
|---|---|---|---|
| Auto Browser (`LvcidPsyche/auto-browser`) | Supervised browser control / MCP / Playwright / noVNC | Best next external browser candidate, but still not installed | Local-first, MIT, explicit human takeover, approvals, audit trails, PII scrubbing, noVNC, host policy, and anti-stealth posture align with Ghoti better than other browser candidates |
| RUFLO (`ruvnet/ruflo`) | Multi-agent orchestration | Research only | Architecturally relevant, but critical security/trust history and broad MCP/agent surface make it unsafe to install without a separate source audit |
| Obscura (`h4ckf0r0day/obscura`) | Rust headless browser / scraping / CDP | Research only / do not integrate now | Rust + CDP is interesting, but README emphasizes stealth/anti-detect and scraping at scale, which conflicts with Ghoti's legal/TOS-aware supervised boundaries |
| Browser Use (`browser-use/browser-use`) | Browser agent framework | Research later | Mature ecosystem and MIT, but cloud/stealth/CAPTCHA/proxy positioning conflicts with Ghoti's no-bypass policy unless limited to local open-source use |
| InvenTree (`inventree/InvenTree`) | Inventory/project/hardware tracking | Use soon as separate app candidate | MIT, mature Python/Django inventory system with REST API; useful for future project parts/assets tracking, not core operator runtime |
| OpenMontage (`calesthio/OpenMontage`) | Agentic video production | Research only | Relevant to content factory workflows, but AGPLv3 and many provider/API/media rights implications require careful separation |
| Apify | Scraping/automation platform | Research later only | Useful for legitimate research/jobs/business workflows, but cloud, TOS, scraping, and paid-service risk make it unsuitable for core operator runtime |
| OpenClaw | Local multi-agent dashboard/reference | Reference only | Existing local reference direction, but not proven wired into Ghoti; evaluate separately from runtime |

## Candidate Notes

### Auto Browser

- Source: `https://github.com/LvcidPsyche/auto-browser`
- License: MIT.
- Observed purpose: MCP-native browser control plane with Playwright sessions, human takeover, reusable auth profiles, approvals, audit trails, and local-first deployment.
- Runtime requirements: Docker Compose, Python/FastAPI controller, Playwright/browser node, noVNC, localhost ports.
- Strong alignment:
  - Human takeover.
  - Approval gates.
  - Audit events.
  - PII scrubbing.
  - Local-first default.
  - Explicit "not stealth / not CAPTCHA / not unauthorized scraping" posture.
- Main risks:
  - Auth profile reuse can become credential risk.
  - MCP endpoint expands action surface.
  - Docker/browser runtime creates many artifacts.
  - "Login once, reuse later" needs strict operator consent and session-retention controls.
- Verdict: highest-priority browser-control evaluation candidate, but only after explicit isolated clone approval.

### RUFLO

- Source: `https://github.com/ruvnet/ruflo`
- License: MIT.
- Observed purpose: large Claude/Codex-adjacent multi-agent orchestration platform with CLI, MCP, memory, hooks, swarms, and provider routing.
- Strong alignment:
  - Single-purpose role agents.
  - Shared memory concepts.
  - Multi-agent coordination patterns.
- Main risks:
  - Public security concern issue reported MCP prompt injection and older obfuscated preinstall behavior.
  - Broad tool/action surface.
  - Provider/API key exposure.
  - Background hooks/workers and MCP registration risk.
  - Windows compatibility concerns.
- Verdict: architecture-reference only until a full source/dependency audit is explicitly approved.

### Obscura

- Source: `https://github.com/h4ckf0r0day/obscura`
- License: Apache-2.0.
- Observed purpose: Rust headless browser engine for AI agents and web scraping, CDP-compatible with Playwright/Puppeteer.
- Strong alignment:
  - Rust binary direction.
  - CDP compatibility.
  - Potential lightweight local browser primitive.
- Main risks:
  - README emphasizes stealth, anti-detect, anti-fingerprinting, parallel scraping, and tracker blocking.
  - Legal/TOS risk is high if used beyond authorized testing.
  - No operator approval model observed in read-only docs.
- Verdict: do not integrate into Ghoti operator path now. If ever evaluated, test only legal/authorized/non-stealth use.

### Browser Use

- Source: `https://github.com/browser-use/browser-use`
- License: MIT.
- Observed purpose: Python browser agent framework with local and cloud modes.
- Strong alignment:
  - Established browser automation ecosystem.
  - CLI and Python APIs.
  - Custom tools.
- Main risks:
  - Cloud product emphasizes stealth/proxy/CAPTCHA-solving for production.
  - Examples include shopping and applications, which are consequential and require hard approval gates.
  - API keys and external model usage likely.
- Verdict: useful reference for browser-agent UX and local APIs, but not first implementation candidate.

### InvenTree

- Source: `https://github.com/inventree/InvenTree`
- License: MIT.
- Observed purpose: open-source inventory management system with Python/Django backend, REST API, plugins, Docker/bare-metal deployment.
- Strong alignment:
  - Project inventory, hardware, assets, components, and supplies tracking.
  - Mature REST API/plugin surface.
- Main risks:
  - Full app deployment complexity.
  - Database and user/account management.
  - Not an operator runtime.
- Verdict: good future project-ops app candidate, separate from core Ghoti operator stack.

### OpenMontage

- Source: `https://github.com/calesthio/OpenMontage`
- License: AGPLv3.
- Observed purpose: agentic video production pipeline using Python tools, Remotion, FFmpeg, AI providers, media search, and markdown/YAML skills.
- Strong alignment:
  - Content factory planning.
  - Skill/pipeline architecture.
  - Human approval at creative decision points.
- Main risks:
  - AGPLv3 implications for modification/network use.
  - API keys for media/model providers.
  - Copyright/media rights/reupload risk.
  - Cost and cloud provider complexity.
- Verdict: research-only reference for content workflows; do not mix with core operator runtime.

### Apify

- Source: `https://apify.com`
- License: hosted platform, not a repo intake item by default.
- Observed purpose: scraping/automation cloud platform.
- Strong alignment:
  - Legitimate public-source research workflows.
  - Jobs/internship/business research after approval.
- Main risks:
  - Cloud/paid usage.
  - TOS and scraping compliance.
  - Easy drift into unauthorized scraping or spam lead-gen.
- Verdict: research-only; use only for legal/TOS-aware public research after explicit approval.

## Implementation Implications For Ghoti

External tools should not define Ghoti's safety model. Ghoti needs its own stable operator core:

- `ActionIntent` schema.
- `CapabilityAdapter` interface.
- Human approval gate for any write/external action.
- Action-bound and payload-bound approval consumption.
- Audit trace.
- Local-only session state.
- Adapter status dashboard.
- Read-only observations separated from actions.

Only after this exists should any external candidate be considered as an adapter.

## Sources Used

- https://github.com/LvcidPsyche/auto-browser
- https://raw.githubusercontent.com/LvcidPsyche/auto-browser/main/README.md
- https://raw.githubusercontent.com/LvcidPsyche/auto-browser/main/LICENSE
- https://raw.githubusercontent.com/LvcidPsyche/auto-browser/main/SECURITY.md
- https://github.com/ruvnet/ruflo
- https://github.com/ruvnet/ruflo/issues/1375
- https://github.com/ruvnet/ruflo/issues/1384
- https://github.com/ruvnet/ruflo/issues/615
- https://github.com/h4ckf0r0day/obscura
- https://raw.githubusercontent.com/h4ckf0r0day/obscura/main/README.md
- https://raw.githubusercontent.com/h4ckf0r0day/obscura/main/LICENSE
- https://github.com/browser-use/browser-use
- https://raw.githubusercontent.com/browser-use/browser-use/main/README.md
- https://raw.githubusercontent.com/browser-use/browser-use/main/LICENSE
- https://github.com/inventree/InvenTree
- https://raw.githubusercontent.com/inventree/InvenTree/master/README.md
- https://raw.githubusercontent.com/inventree/InvenTree/master/LICENSE
- https://github.com/calesthio/OpenMontage
- https://raw.githubusercontent.com/calesthio/OpenMontage/main/README.md
- https://raw.githubusercontent.com/calesthio/OpenMontage/main/LICENSE

## Current Status

- Audit status: `operator_candidate_audit / research_only / not_runtime_wired`
- Repos cloned: NO
- Tools installed: NO
- Runtime wired: NO
- External services connected: NO
- Approval gates changed: NO
