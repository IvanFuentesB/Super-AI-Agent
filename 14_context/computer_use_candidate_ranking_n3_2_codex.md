# Computer-Use Candidate Ranking - N+3.2 Codex

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Status label: ranking_only / no_runtime_changes / not_runtime_wired

## Ranking Summary

| Rank | Candidate | Recommendation | Why |
|---:|---|---|---|
| 1 | TryCUA / CUA Driver | research only now; strongest long-term sandbox candidate | Best aligned with full computer-use direction if sandbox-first and approval-bound. Exact source/version still needs verification before use. |
| 2 | AutoBrowser | use soon after isolated evaluation | Narrower browser-control surface than desktop control; best near-term supervised browser adapter candidate. |
| 3 | Claude computer use | research/use later behind gates | Powerful provider capability, but must sit behind ActionIntent, consent, allowlists, and audit trail. |
| 4 | Browser Use | research/reference fallback | Useful browser-agent reference, but not yet evaluated as Ghoti runtime dependency. |
| 5 | Obscura | research only | Browser/CDP potential, but stealth/scraping positioning requires strict legal/TOS gates. |
| 6 | RUFLO | research only for orchestration, not first computer-use runtime | Multi-agent orchestration reference with high trust/security surface; not the first computer-use adapter. |

## 1. TryCUA / CUA Driver

- Purpose: computer-use agent driver and sandbox direction.
- Fit for Ghoti: potentially very strong long-term fit if it provides explicit sandboxing, visible sessions, and bounded desktop/browser control.
- Current truth: not installed, not cloned by this Codex lane, not runtime-wired. Exact source/version must be verified before use.
- Likely install/runtime requirements: likely native dependencies, sandbox/VM/container setup, Python or Node tooling, and OS-specific permissions.
- Sandbox story: must be sandbox-first. No host desktop control until a local sandbox proof is reviewed.
- Windows compatibility risk: medium to high until exact project docs are inspected.
- Account/API key risk: depends on integration path; must not use provider sessions or accounts without explicit approval.
- Legal/TOS risk: high if used against real services without approval and allowlists.
- Safety risk: high because full computer use has broad blast radius.
- Best first test: read-only source/docs/license evaluation, then sandbox-only launch with no credentials and no external websites.
- What not to do: do not connect to user accounts, do not drive host desktop, do not bypass CAPTCHAs or platform protections, do not use for external actions.
- Recommendation: research only now; likely strongest long-term direction after sandbox proof.

## 2. AutoBrowser

- Purpose: browser-control and browser automation layer.
- Fit for Ghoti: strong near-term fit because browser control is narrower and more observable than full desktop control.
- Current truth: read-only candidate audit exists; isolated clone/eval status is referenced in intake docs; not runtime-wired.
- Likely install/runtime requirements: Docker and browser runtime are likely required.
- Sandbox story: better than host desktop if run in a contained browser profile/container.
- Windows compatibility risk: medium due Docker/browser requirements.
- Account/API key risk: high if it touches logged-in user profiles; must use blank isolated profiles first.
- Legal/TOS risk: medium to high depending target site and automation use.
- Safety risk: medium to high; browser actions can submit forms, spend money, post content, or change accounts.
- Best first test: isolated blank-profile browser session that only opens a local test page and reports DOM state.
- What not to do: no real credentials, no social posting, no purchases, no scraping behind login, no external form submission.
- Recommendation: use soon after ActionIntent adapter design and isolated validation.

## 3. Claude Computer Use

- Purpose: provider-native computer-use capability for UI interaction.
- Fit for Ghoti: powerful future adapter if wrapped by Ghoti approval gates and visible operator state.
- Current truth: strategy note exists; not wired into Ghoti runtime.
- Likely install/runtime requirements: provider access, compatible client/API, screenshots, tool-call loop, and account permissions.
- Sandbox story: should start with local test app or sandbox browser only.
- Windows compatibility risk: medium; depends on provider and tool runner.
- Account/API key risk: high; provider credentials and screenshot data require care.
- Legal/TOS risk: medium to high for external accounts and websites.
- Safety risk: high without allowlists and approval binding.
- Best first test: local-only static UI task with ActionIntent approval before each click/type.
- What not to do: no autonomous clicking/typing, no sensitive apps, no credentials, no external account actions, no action from observation alone.
- Recommendation: research/use later behind ActionIntent + CapabilityAdapter gates.

## 4. Browser Use

- Purpose: browser-agent framework/reference for navigating pages and interacting with browser state.
- Fit for Ghoti: useful as reference or fallback for browser-agent patterns.
- Current truth: available as a Codex plugin/skill in this environment, but not automatically wired into Ghoti runtime.
- Likely install/runtime requirements: Python/Playwright or browser runtime depending exact setup.
- Sandbox story: can be constrained to localhost or approved test domains.
- Windows compatibility risk: medium.
- Account/API key risk: depends on target sites and model provider used.
- Legal/TOS risk: medium; browser automation can violate platform rules if misused.
- Safety risk: medium to high if allowed to act on arbitrary pages.
- Best first test: localhost-only overlay/dashboard smoke test, not external browsing.
- What not to do: do not treat Codex plugin availability as Ghoti runtime capability; do not use it for external account actions.
- Recommendation: research/reference fallback.

## 5. Obscura

- Purpose: browser/CDP/headless browsing candidate with potential Rust/headless tooling angle.
- Fit for Ghoti: possible low-level browser-control reference, but risky for first adapter.
- Current truth: read-only/source verification exists in repo history; not runtime-wired.
- Likely install/runtime requirements: Rust or native build chain and browser/CDP dependencies.
- Sandbox story: must be isolated and localhost-only first.
- Windows compatibility risk: medium to high until build path is stable.
- Account/API key risk: low for local-only tests, high if used with real browser profiles.
- Legal/TOS risk: high if stealth or scraping features are used against third-party services.
- Safety risk: high if anti-detect or scraping behavior is enabled.
- Best first test: build/source verification and local static page CDP read-only smoke, no external sites.
- What not to do: no stealth browsing, no evasion, no scraping against TOS, no logged-in sessions.
- Recommendation: research only.

## 6. RUFLO

- Purpose: multi-agent orchestration and MCP/tool coordination candidate.
- Fit for Ghoti: useful orchestration architecture reference, not a first computer-use adapter.
- Current truth: high-priority research reference; no runtime wiring.
- Likely install/runtime requirements: Node/npm, provider keys, MCP configuration, broad tool surface.
- Sandbox story: weak until every tool and permission is constrained.
- Windows compatibility risk: medium.
- Account/API key risk: high because orchestration frameworks often require provider credentials and many tools.
- Legal/TOS risk: depends on tool configuration; can become high quickly.
- Safety risk: high due large MCP/tool surface and previous trust concerns documented in repo intake.
- Best first test: continue source/security review; extract architecture ideas only.
- What not to do: do not wire to Ghoti runtime, do not provide broad filesystem or account access, do not use for cap bypass.
- Recommendation: research only for orchestration.

## Practical Path

1. Keep N+3.2 focused on wait/resume and readiness state.
2. Use N+3.3 or N+3.4 to build one sandbox-only CapabilityAdapter demo.
3. Test the demo against local files or localhost pages only.
4. Evaluate AutoBrowser first for browser control.
5. Evaluate TryCUA/CUA Driver as the long-term sandbox/full-computer direction once exact source and sandbox model are verified.
