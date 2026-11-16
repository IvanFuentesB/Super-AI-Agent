# Codex Skills

Skills for the auditor / second-pass agent. Codex reviews after Claude Code
builds. Status of record: `14_context/tool_stack/skills_registry.json`.

| Skill | Purpose | manual_required |
|-------|---------|-----------------|
| karpathy-guidelines | Anti-pitfall coding discipline applied to review | false |
| context-engineering | Keep audit context tight and relevant | false |
| verification-loop | Re-verify the builder's claims before sign-off | false |
| parallel-execution-optimizer | Run independent audit checks in parallel | true |
| security-review | Review diffs for security issues | false |
| rust-guard-audit | Audit Rust runtime/policy guard code | false |
| merge-gate | Gate merges on review + checks passing | false |
| repo-intake-audit | Audit repo-intake reports and decisions | false |
| token-saving-audit | Flag wasteful prompting/context usage | true |

Notes:

- The audit discipline skills (security-review, rust-guard-audit, merge-gate,
  repo-intake-audit, karpathy, context-engineering, verification-loop) are
  already part of this repo's workflow; use them directly.
- `parallel-execution-optimizer` and `token-saving-audit` are manual-install
  candidates pending canonical source confirmation.
- Codex is review-oriented; it does not bypass approval gates or run outbound
  actions.
