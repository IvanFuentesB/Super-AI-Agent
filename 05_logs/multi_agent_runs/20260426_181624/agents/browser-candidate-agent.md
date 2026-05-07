# Browser Candidate Agent (browser-candidate-agent)

- Status: done
- Task: Compare Auto Browser and Obscura as safe future browser candidates.
- Safe next step: build Ghoti ActionIntent first, then evaluate Auto Browser in isolation if approved.
- Key compact evidence:
  - ## Current Verdict
  - 1. Build Ghoti's own small operator contract first: action schema, approval gate, audit log, capability allowlist, adapter interface, and local-only state.
  - 3. Evaluate Auto Browser first if a browser-control candidate is needed.
  - 5. Treat Obscura as research-only or blocked for Ghoti runtime until the project can prove legal/TOS-safe, non-stealth use.
  - | Candidate | Category | Current verdict | Why |
  - | Browser Use (`browser-use/browser-use`) | Browser agent framework | Research later | Mature ecosystem and MIT, but cloud/stealth/CAPTCHA/proxy positioning conflicts with Ghoti's no-bypass policy unless limited to local open-source use |
  - ### Auto Browser
  - - Observed purpose: MCP-native browser control plane with Playwright sessions, human takeover, reusable auth profiles, approvals, audit trails, and local-first deployment.
  - - Approval gates.
