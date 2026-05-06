# Codex N+3.52 - Ruflo, Gemma, And Write Gate Review

## Ruflo Truth

Inspected local Ruflo candidate path: `21_repos/third_party/evals/ruflo`.

Observed from N+3.50A validation:

- Package name/version: `claude-flow` / `3.5.80`
- `package-lock.json`: present
- `node_modules`: absent
- Top-level lifecycle scripts: none detected
- NPM in PATH: not found during this audit
- Codex install performed: no
- Ruflo swarm/runtime/MCP executed: no
- Ghoti runtime wiring: no

## Safe Install Command, Not Yet Run

The intended isolated command remains:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only\21_repos\third_party\evals\ruflo
npm ci --ignore-scripts
```

This audit does not approve running it until npm path truth is resolved and the gate requires an extra explicit confirmation flag.

## Ruflo Gate Hardening Required

`--install --dry-run` is safe. `--install --apply` should not be enough by itself. Next Claude should require something like:

```powershell
python 03_scripts/ruflo_install_gate.py --install --apply --confirm-local-ruflo-install
```

Required hard gates:

- No global install.
- No `npx`.
- No swarm launch.
- No MCP launch.
- No credentials or `.env` reads.
- No live accounts.
- No desktop/browser/account control.
- No repo writes outside declared lane files.
- No hidden background processes.
- Log every install/smoke action locally.

## Gemma Truth

Observed from N+3.50A validation:

- Ollama responds.
- No Gemma model was listed in this audit.
- No model pull was performed.
- `gemma_compact_memory_worker.py --compress --dry-run` did not write and did not call Ollama.
- Apply mode is intended to write draft-only artifacts under local logs and optional prompt bus outbox.
- Canonical compact memory overwrite is not allowed.

Claude N+3.50A docs claimed Gemma was found earlier, but current validation contradicted that claim. Treat current validation as the merge gate truth.

## Gemma Verdict

`NOT YET USABLE FOR TOKEN SAVING`

The script shape is promising, but token savings are not real until a local model is present and a draft summary is successfully written.

## Required Gemma Hardening

1. Add `--model` override.
2. Add no-model fallback artifact or clear prompt bus outbox instruction.
3. Keep model pulls manual and approval-gated.
4. Write only draft artifacts.
5. Never overwrite `14_context/compact_memory/*.md` directly.
6. Require human, Claude, or Codex review before promoting a Gemma draft to canonical memory.

## Overall Verdict

`CONDITIONAL`

Ruflo and Gemma are safely separated from live actions, but neither is actually operational enough yet to justify a strong merge claim.
