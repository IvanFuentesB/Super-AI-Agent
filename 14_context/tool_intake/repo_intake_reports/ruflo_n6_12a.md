# Ruflo - Static Intake Report (N+6.12A)

**Priority:** critical (explicit top priority for N+6.12A)
**Source:** `https://github.com/ruvnet/ruflo.git` (confidence: high)
**Local clone:** `21_repos/third_party_static/ruflo` (git-ignored)
**Commit:** `f57b69876ba1c4e6bf4e317d0d1529a5481692c4` (shallow `--depth 1`)
**License:** MIT (reuse permitted) - **but see security history**
**Static-inspected:** yes | **safe_to_run:** false | **runtime_wired:** false

## What it is

A multi-agent orchestration framework (aka claude-flow): role-labeled agents,
coordinator/worker separation, shared memory, and plugin/skill registration, driven
by a model provider.

## Static inspection findings

- `files_scanned`: 4336; license family detected: **MIT**; license files include
  `LICENSE` and `ruflo/src/ruvocal/LICENSE`; 12 package files.
- **Install scripts present:** `.claude-plugin/scripts/install.sh`, `scripts/install.sh`.
- **Package lifecycle hooks present:** `postinstall` in `v3/@claude-flow/browser/package.json`
  and `v3/@claude-flow/cli/package.json` (plus `prepublishOnly` across many
  `v3/plugins/*`). Lifecycle hooks are exactly the vector of the documented
  supply-chain incident, so they are called out here as risk evidence.
- Browser/computer-control, credential/auth, and network references are present in
  the tree (expected for an orchestration framework with MCP/plugins).

## Useful patterns (the architecture ideas)

1. Role-labeled single-purpose agents - each agent has one narrow job.
2. Explicit coordinator/worker separation with task hand-offs.
3. Shared **local** memory as the coordination substrate.
4. Plugin/skill registration - capabilities declared up front, not implicit.

## Risks

- **Documented obfuscated malicious npm pre-install script** (reported across
  v3.1.0-alpha.55 .. v3.5.2) that deleted directories. This is why install scripts
  and `postinstall` hooks above matter.
- **MCP prompt-injection (Issue #1375):** tool descriptions covertly added the
  maintainer as a repository contributor.
- **SQL-injection history** (remediated v3.5.40).
- Requires `ANTHROPIC_API_KEY`; not local-only; multiplies API spend across swarms.
- Autonomous multi-agent swarms; broad MCP/action surface; documented Windows issues.

## Decision: re-express, do not vendor

MIT would permit copying, but the supply-chain history makes vendoring unwise.
Ghoti extracts **one** safe, non-runtime pattern and **re-expresses it from scratch
with no code copied**: the coordinator/worker + local-memory hand-off + declared-skill
shape, captured in `03_scripts/external_adapters/ruflo_adapter_contract.py`. That
contract is inert and default-disabled (`RUFLO_SWARM_ENABLED = False`, global kill
switch engaged); it launches no agents, calls no provider, opens no network, reads
no credentials, and never installs, imports, or runs Ruflo.

## First safe next test

Read-only source/dependency audit of `package.json` lifecycle scripts and MCP
tool-description strings. **No** `npm` install, **no** MCP server start, **no** API
key use.
