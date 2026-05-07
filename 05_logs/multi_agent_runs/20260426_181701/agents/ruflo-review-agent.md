# RUFLO Review Agent (ruflo-review-agent)

- Status: done
- Task: Summarize the current safe next step from RUFLO audit docs.
- Safe next step: keep RUFLO research-only; mine architecture patterns, not runtime behavior.
- Key compact evidence:
  - Status label: read_only_evaluation / not_installed / not_runtime_wired
  - - Status label: `read_only_evaluation / not_installed / not_runtime_wired`
  - - What it does not do: It is not a runtime-standalone AI model. It does not replace Claude. It does not work without an Anthropic API key. It does not run fully offline.
  - ### SECURITY — CRITICAL FLAGS (must be read before any install decision)
  - A deliberately obfuscated one-liner in the npm `preinstall` script silently deleted directories and cache files on user machines. The code was removed only after external security disclosure and with no explanation from the maintainer.
  - SQL injection vulnerabilities were present prior to v3.5.40, converted to parameterized queries as part of the security remediation release.
  - - Security risk: **CRITICAL** — supply-chain attack history; obfuscated malicious preinstall; covert repo manipulation via prompt injection; SQL injection history. Even with v3.5.40 remediation, trust is not automatically restored.
