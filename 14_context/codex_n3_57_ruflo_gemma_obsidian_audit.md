# Codex N+3.57 - Ruflo, Gemma, And Obsidian Audit

## Verdict

PENDING TARGET BRANCH.

The Ruflo/Gemma/Obsidian clean-pass fixes cannot be audited because the target branch is missing remotely.

## Ruflo Requirements

Once the branch exists, Codex must run:

```powershell
python 03_scripts/ruflo_install_gate.py --source-status
python 03_scripts/ruflo_install_gate.py --status
python 03_scripts/ruflo_install_gate.py --install --dry-run
python 03_scripts/ruflo_install_gate.py --smoke
python 03_scripts/ruflo_install_gate.py --report --dry-run
python 03_scripts/ruflo_install_gate.py --catalog --dry-run
```

Expected clean-pass truth:

- Clean checkout missing source is described truthfully, not as unsafe.
- Source bootstrap path exists or is documented.
- Install command is only `npm ci --ignore-scripts`.
- No lifecycle scripts means install safe but approval-gated.
- Ruflo runtime wiring = NO.
- No `npx`, no MCP, no swarm, no global install.

## Gemma Requirements

Once the branch exists, Codex must run:

```powershell
python 03_scripts/gemma_compact_memory_worker.py --status
python 03_scripts/gemma_compact_memory_worker.py --compress --input 14_context/compact_memory/project_state.md --dry-run
```

Expected truth:

- Local Ollama only.
- Gemma model availability reported exactly.
- Outputs are `DRAFT_ONLY`, `NOT_CANONICAL`, and `HUMAN_REVIEW_REQUIRED`.
- Canonical compact memory is not modified.

## Obsidian Requirements

Once the branch exists, Codex must run:

```powershell
python 03_scripts/obsidian_probe.py --status
python 03_scripts/obsidian_probe.py --json
powershell -ExecutionPolicy Bypass -File 03_scripts/open_obsidian_vault.ps1 -Check
```

Expected truth:

- Vault existence and required vault files reported consistently.
- App executable detection is consistent between dashboard, probe, and PowerShell helper.
- Check mode does not open the app.

## Current Status

N+3.56 had conditional gaps: Ruflo source/package was missing in clean checkout, Gemma model was missing, and Obsidian detection disagreed across helpers. N+3.57 cannot verify clean-pass fixes without the pushed target branch.
