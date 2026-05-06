# Codex N+3.51 - Ruflo, Obsidian, And Gemma Readiness

Milestone: N+3.51

Date: 2026-05-06

## Ruflo / Claude-Flow Truth

Path inspected:

```text
21_repos/third_party/evals/ruflo
```

Local package metadata:

```text
name: claude-flow
version: 3.5.80
package-lock.json: present
node_modules: absent
```

Scripts found:

```text
dev
build
build:ts
test
test:ui
test:security
lint
security:audit
security:fix
security:test
v3:domains
v3:swarm
v3:security
```

Lifecycle install scripts found in top-level `package.json`:

```text
none found among preinstall, install, postinstall, prepare
```

Readiness verdict:

```text
RUFLO_STATUS = cloned/intake-only, not installed, not wired
```

Important limitation:

`git -C 21_repos/third_party/evals/ruflo rev-parse HEAD` failed because Git detected dubious ownership for the nested repository. This Codex run did not change global Git config and did not add `safe.directory`.

That means the nested Ruflo git HEAD is not verified in this run. Package metadata and files were readable, but nested Git state is blocked until explicitly approved.

## Ruflo Install Recommendation

The practical safe next step is an isolated dependency install gate, not runtime wiring.

Allowed install command for the future Claude milestone if the gate passes:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only\21_repos\third_party\evals\ruflo
npm ci --ignore-scripts
```

Stricter variant Claude may offer as an optional safer default:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only\21_repos\third_party\evals\ruflo
npm ci --ignore-scripts --audit=false --fund=false
```

Why this is only conditionally safe:

- `--ignore-scripts` prevents lifecycle scripts from running.
- Dependency resolution still touches the npm registry.
- Installed dependency tree may be large.
- `node_modules` must never be staged.
- Help/version commands must be read-only.
- No global install is allowed.
- No swarm/MCP/runtime wiring is allowed yet.

## Ruflo Guardrails Before Use

Required before any deeper Ruflo use:

- install only inside `21_repos/third_party/evals/ruflo`,
- no global install,
- no credentials,
- no Claude Code hook/MCP activation,
- no swarm launch,
- no live browser/desktop/account control,
- no account actions,
- no posting/email/payment/scraping/jobs/giveaways,
- no hidden background processes,
- no repo writes outside declared lane,
- log all commands and outputs,
- Codex audits help/version results before any next step.

V1 meaning of "use Ruflo":

1. isolated install,
2. read-only help/version command,
3. local-only plan generation if help/version is safe,
4. no swarm execution until explicit future approval.

## Obsidian Truth

Vault path exists:

```text
14_context/obsidian_vault/
```

Required vault files checked and present:

- `00_Index.md`
- `01_Current_State.md`
- `02_Next_Actions.md`
- `09_Migration_Handoff.md`

Compact memory files checked and present:

- `project_state.md`
- `repo_and_tool_index.md`
- `money_os_memory.md`
- `safety_rules.md`

Obsidian app visibility checks:

- `winget list --id Obsidian.Obsidian --accept-source-agreements` did not find a matching package in this sandbox.
- `where.exe obsidian` did not find Obsidian on PATH.
- `Get-Command obsidian` did not find a command.
- Search under common local and Program Files paths did not find `Obsidian.exe`.

Readiness verdict:

```text
OBSIDIAN_VAULT_STATUS = present
OBSIDIAN_APP_STATUS = not verified as installed/visible in this sandbox
```

This differs from earlier user context saying winget had Obsidian installed. The likely explanation is environment/user-profile mismatch or stale prior truth. Installed according to one environment does not mean the current sandbox user can see or launch the app.

## Obsidian Helper Truth

Current helper:

```text
03_scripts/open_obsidian_vault.ps1
```

Behavior:

- `-Check` verifies required vault files.
- `-Open` builds an `obsidian://open?path=...` URI and calls `Start-Process`.
- It does not modify vault contents.
- It does not verify the Obsidian executable path.
- It does not prove the app opened.

Recommended next improvement:

- add `-CheckInstall`,
- search PATH and common install paths,
- optionally check winget without installing,
- print a clear manual fallback if app is not visible,
- support URI open only with explicit `-Open`,
- never auto-open from dashboard refresh,
- document that vault exists even if app is not installed.

## Gemma / Ollama Truth

Commands run:

```powershell
python 03_scripts/ghoti_local_orchestrator.py --gemma-check
ollama list
```

Observed:

```text
Ollama: found, version 0.22.0
ollama list: no models listed
Gemma: not found
```

Readiness verdict:

```text
OLLAMA_STATUS = installed
GEMMA_STATUS = model not available in this sandbox
```

Current scripts only check Ollama/Gemma availability. They do not yet call Gemma to compress project context or prompt packs.

## Gemma Next Step

Recommended next Claude implementation:

- create `03_scripts/gemma_compact_memory_worker.py`,
- dry-run default,
- reads a local markdown file,
- checks Ollama and model availability,
- uses `ollama run gemma3:4b` only if model exists or after explicit operator approval to use the available configured model,
- writes draft output only,
- never overwrites canonical compact memory,
- records a source map and warning list,
- includes a no-model fallback that writes a Claude/Gemma prompt outbox artifact instead of failing silently.

Safe output targets:

- `14_context/prompt_bus/outbox/`
- `05_logs/gemma_compact_memory_drafts/<run_id>/`

Forbidden:

- automatic `ollama pull`,
- automatic canonical overwrite,
- executing model output,
- public/live/account/money actions,
- using Gemma output as source of truth without review.
