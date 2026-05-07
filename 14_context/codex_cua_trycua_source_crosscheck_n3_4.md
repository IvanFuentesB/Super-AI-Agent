# Codex CUA / TryCUA Source Crosscheck - N+3.4

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: ad022a0
Status label: parallel_audit_only / source_crosscheck / no_install / not_runtime_wired

## Sources Checked

- GitHub: `trycua/cua` - https://github.com/trycua/cua
- Cua Driver docs - https://cua.ai/docs/cua-driver/guide/getting-started/introduction
- Cua Computer SDK docs - https://cua.ai/docs/cua/guide/get-started/using-computer-sdk

No clone, install, package download, driver launch, sandbox launch, or runtime wiring occurred.

## Exact Source Candidates

| Candidate | URL | What it appears to be | Current verdict |
|---|---|---|---|
| `trycua/cua` | `https://github.com/trycua/cua` | Main open-source Cua repo containing Cua Driver, sandbox SDKs, benchmarks, docs, packages, and examples | Likely canonical source |
| Cua Driver docs | `https://cua.ai/docs/cua-driver/...` | Documentation for the Cua Driver package, described as a macOS background computer-use driver that speaks MCP over stdio | Canonical docs for Cua Driver |
| Cua SDK docs | `https://cua.ai/docs/cua/...` | Documentation for Cua sandbox/computer SDKs and agent-ready environments | Canonical docs for broader Cua sandbox path |
| Older/adjacent `trycua/computer` references | Mentioned in older public material | Older or adjacent computer-use interface references | Do not treat as canonical until mapped to current `trycua/cua` package layout |
| Generic "CUA" MCP servers | Various | Different projects using "computer-use agent" terminology | Not canonical for Ghoti until separately verified |

## Likely Canonical Source

Likely canonical source: `trycua/cua`.

Reasons:

- The GitHub repo describes itself as open-source infrastructure for computer-use agents.
- It includes documented packages for Cua Driver, Cua sandbox, computer server, agent, benchmarks, and related tooling.
- It links to `cua.ai` as the official docs site.
- The repo lists MIT license in GitHub metadata and README/license area.

## License Truth

Known from public source view:

- `trycua/cua`: MIT license.
- Third-party components may have their own licenses.
- Optional components may introduce stricter licenses; license must be checked per package before use.

Do not assume every subpackage/dependency is MIT-compatible without source review.

## Install Requirements / OS Support

From public docs and repo description:

- Cua Driver is presented as a macOS background computer-use driver.
- Broader Cua sandbox/SDK material presents macOS, Linux, Windows, Android, and browser/device-related paths.
- Python 3.11+ is shown for the `cua` package path.
- The repo includes Swift, Python, TypeScript, shell, Docker/package files, and sandbox/VM-oriented components.

Important Windows caveat:

- Cua Driver itself appears macOS-oriented.
- The broader Cua sandbox path claims Windows support, but Ghoti should verify which package supports Windows before planning a Windows-local smoke test.
- A Windows Ghoti machine should prefer sandbox/VM/container proof over host-desktop driver assumptions.

## Security Risks

- Full computer-use control has a broad blast radius.
- Screenshot capture may expose private data.
- Background control can confuse the operator if not visibly surfaced.
- MCP stdio tools can expand capability quickly if over-allowed.
- Install scripts and package lifecycle hooks must be inspected before use.
- Cloud/sandbox products may involve external services or account terms.
- CUA Driver background/no-foreground behavior is powerful and must not be treated as safer merely because it avoids foreground disruption.

## Should It Be Cloned Next?

Yes, but only as an explicitly approved, isolated, read-only source evaluation milestone.

Recommended clone path:

`21_repos/third_party/evals/cua`

Required before clone:

1. Operator approval.
2. Confirm exact repo: `https://github.com/trycua/cua`.
3. Confirm no install/build/run during clone milestone.
4. Keep nested repo untracked.
5. Audit install scripts, package files, license, platform support, and Windows/sandbox path.

## What Not To Do Yet

- Do not run the install shell command shown in public docs.
- Do not `pip install cua`.
- Do not run `npx cuabot`.
- Do not launch any Cua Driver daemon or MCP server.
- Do not connect Claude/Codex/Gemini/GPT providers.
- Do not use live accounts.
- Do not capture host desktop screenshots.
- Do not click/type.
- Do not wire Cua into Ghoti runtime.

## Verdict

Verdict: `trycua/cua` is likely canonical and should be the next CUA source-evaluation target, but only as a no-install, no-runtime-wiring, sandbox-first read-only review.
