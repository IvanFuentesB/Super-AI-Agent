# Codex CUA / TryCUA Exact Source Review - N+3.5

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: ca403cd
Status label: parallel_audit_only / source_review / no_install / not_runtime_wired

## Sources Reviewed

Primary public sources checked:

- GitHub: `trycua/cua` - https://github.com/trycua/cua
- Cua Driver docs: https://cua.ai/docs/cua-driver/guide/getting-started/introduction
- Cua Driver installation docs: https://cua.ai/docs/cua-driver/guide/getting-started/installation
- Cua docs home / broader SDK positioning: https://cua.ai/docs

No clone, install, model/provider connection, CUA execution, screen capture, or runtime wiring occurred.

## Likely Canonical Source

Likely canonical source: `https://github.com/trycua/cua`

Source confidence: high for the broad Cua project, high for Cua Driver docs, medium for the exact future Ghoti package path because the repo contains several products/packages and the Windows-compatible path must be confirmed by source review before implementation.

Reasons:

- The public GitHub repo is under `trycua/cua`.
- The repo links to `cua.ai` as the official docs site.
- GitHub metadata and repo page describe it as open-source infrastructure for computer-use agents.
- The repo contains `libs`, docs, examples, package files, and Cua Driver references.
- The Cua Driver docs describe Cua Driver as a macOS computer-use driver that speaks MCP over stdio.

## License

Known from public source/docs:

- `trycua/cua` is presented as MIT licensed.
- Cua Driver docs also state MIT license.

Remaining check before use:

- Verify license files in the exact package path chosen for Ghoti.
- Check third-party dependencies and generated binaries separately.
- Do not assume every subcomponent, model, benchmark, or dependency has identical terms.

## Install Requirements

Observed from public docs:

- Cua Driver install path uses a shell installer from `raw.githubusercontent.com/trycua/cua/main/libs/cua-driver/scripts/install.sh`.
- Cua Driver installation targets macOS, installs `CuaDriver.app`, symlinks a CLI, and requires macOS TCC permissions.
- Cua Driver requires Accessibility and Screen Recording permissions.
- Broader `cua` SDK examples use `pip install cua` and Python 3.11+.
- Repo examples also show `npx cuabot` for sandbox/co-op flows.

Ghoti rule:

- Do not run install scripts.
- Do not `pip install cua`.
- Do not run `npx cuabot`.
- Do not grant Accessibility or Screen Recording permissions.
- Do not launch any MCP server or driver.

## OS Support

Current truth:

- Cua Driver appears macOS-only from current Cua Driver docs.
- Cua Driver docs require macOS 14 Sonoma or later and Apple Silicon or Intel Mac.
- Cua Driver is not a VM; it operates the real host Mac.
- Broader Cua SDK/docs describe sandbox support for macOS, Linux, Windows, Android, and local/cloud paths.
- For this Windows Ghoti repo, the relevant path is likely the broader Cua sandbox/SDK path, not the macOS Cua Driver host driver.

Important distinction:

- "Cua Driver" does not equal "Windows host driver" based on current docs.
- "Cua sandbox/SDK" may support Windows environments, but that must be verified in source before any Windows smoke test is planned.

## VM / Sandbox Requirement

Sandbox is required for Ghoti.

Rationale:

- Full computer use can click/type and see private data.
- Cua Driver host control is explicitly not a VM.
- Ghoti's first CUA path must avoid host desktop control and live accounts.
- A sandbox/VM gives the operator a controlled target surface and a clean kill boundary.

Minimum sandbox requirements:

- no live accounts
- no credentials
- no 2FA
- no sensitive apps
- no private documents
- no host desktop control
- one ActionIntent at a time
- payload-hash-bound execution
- local audit trace
- 3-day screenshot retention

## API Keys / Cloud Requirements

Current truth:

- Cua Driver itself is documented as an MCP/CLI driver and may not require provider keys by itself.
- Agent loops using Claude, GPT, Gemini, etc. would require provider credentials.
- Broader Cua cloud/sandbox offerings may involve accounts, cloud services, or provider keys.

Ghoti rule:

- No provider API keys or cloud accounts in the first source review.
- No Cua cloud use without explicit approval.
- No provider/session sharing, cap bypass, or account abuse.

## Security / Privacy Risks

- Accessibility and Screen Recording permissions are powerful.
- Cua Driver can click/type in background without changing the frontmost app, which is useful but harder for a human to notice.
- Screenshots may expose private data.
- MCP stdio servers can expand capability surface quickly if added to agent clients.
- Shell installer and package lifecycle scripts must be audited before use.
- A sandbox/computer-use loop can accidentally submit forms, send messages, purchase, trade, or post content if not gated.

## Should Claude Clone / Read-Only Audit Next?

Yes, if the user explicitly approves.

Recommended next source audit:

- Clone `https://github.com/trycua/cua` into `21_repos/third_party/evals/cua`.
- Do not install.
- Do not run scripts.
- Do not launch driver/daemon/MCP.
- Inspect license, package manifests, install scripts, platform support, Windows sandbox path, and permissions.
- Keep the nested repo untracked.

## Verdict

Verdict: `trycua/cua` is the likely canonical source. Cua Driver itself appears macOS host-focused; the broader Cua sandbox/SDK path may be the relevant Windows/sandbox path. No runtime wiring yet. Next safe step is explicit-approval read-only source clone/audit, not install or execution.
