# Repo Intake Queue

Inspect-first repos awaiting static intake. None are cloned or executed by being
listed. Run each through the safe intake before adapting anything. Full workflow:
`docs/GHOTI_REPO_INTAKE_SAFETY.md`.

## Queue

| Repo / lane | Why | Decision needed |
|-------------|-----|-----------------|
| repomix | Pack a repo into one AI-friendly file | Confirm official package, then intake. |
| gitingest | Turn a git repo/URL into a prompt digest | Confirm canonical source, then intake. |
| code-graph (CodeGraph / Git Nexus cluster) | Structural code graph for large-repo navigation/audit | Identify a maintained OSS option; intake; no execution. |
| superclaude | Agent framework; evaluate patterns | Intake-first; extract patterns, do not import wholesale. |
| bmad | Agent framework; evaluate patterns | Intake-first; extract patterns, do not import wholesale. |
| archon | Agent framework; evaluate patterns | Intake-first; extract patterns, do not import wholesale. |
| mem0 | Long-term memory; must not duplicate memory | Intake-first; only adopt if it extends the one memory path. |
| claude-mem | Long-term memory bridge | Intake-first; do not add a second memory system. |
| cad-text-to-cad (e.g. CadQuery / build123d) | Parametric / text-to-CAD workflows | Intake-first; identify OSS; no license abuse. |

## Intake steps (per repo)

1. Confirm the canonical source/URL. Many names collide; do not assume.
2. Dry-run: `python 03_scripts/tool_stack/repo_intake.py <repo-url>`
   (validates the target, clones nothing).
3. Apply (static only): add `--apply` to shallow-clone into the gitignored
   sandbox `14_context/tool_intake/repo_sandbox/<slug>/` and write a report.
   No install scripts or code are ever run.
4. Read the report at `14_context/tool_intake/reports/<slug>_<timestamp>.md` and
   its decision (`inspect_more` / `safe_to_adapt` / `risky` / `reject`).
5. Adapt only after a human review. Reports are committed; cloned source is not.
