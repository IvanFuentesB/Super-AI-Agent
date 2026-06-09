# GHOTI N+6.40A -- Working MVP: Runtime Recipes

**Milestone:** N+6.40A
**Branch:** `feat/ghoti-agent-claude-fable-n6-40a-working-mvp-runtime-recipes`
**Status:** Implemented (feature branch; not merged)

---

## What Ghoti can do today

Ghoti now has **Working Recipes**: safe local supervised workflows that do real
work right now. Each recipe inspects, summarizes, validates, and writes a
Markdown report into `14_context/operator_reports/generated/`. Every run is
checked against a deny-by-default capability policy first - when the Rust
policy checker binary is built it is invoked for real; otherwise a Python
mirror enforces the identical policy.

| Recipe | What it does |
|--------|--------------|
| `project-health` | Full local snapshot: git truth, launcher status, public security audit, Rust status, PR queue, dashboard reachability |
| `handoff-pack` | Copy-paste packets for the implementation lane, the audit lane, and the local Hermes/Ollama lane |
| `cleanup-preview` | Read-only inspection: untracked/modified files, large files, worktrees, caches, old logs - never deletes or moves |
| `local-model-check` | Checks the ollama command, the localhost endpoint, and llama3.1:8b / gemma3:4b - never pulls |
| `fixture-replay-demo` | Replays the claude-swarm fixture plan: 5 tasks / 3 parallel groups / 0 overlaps, simulation only |
| `all-safe` | Runs all five in sequence plus an aggregate summary report |

## How to run recipes from the CLI

```bash
# list everything
python 03_scripts/operator_recipes/ghoti_operator_recipes.py --list

# run one recipe
python 03_scripts/operator_recipes/ghoti_operator_recipes.py --run project-health --json

# run everything safe
python 03_scripts/operator_recipes/ghoti_operator_recipes.py --run all-safe --json

# custom repo-local output dir
python 03_scripts/operator_recipes/ghoti_operator_recipes.py --run cleanup-preview --json --output-dir 14_context/operator_reports/generated
```

An `--output-dir` outside the repo is **preview-only**: the report content is
returned in the JSON (`report_preview`) but nothing is written. No allowlisted
external paths exist yet, so this holds even with `--apply`.

## How to run recipes from the dashboard

1. `python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard`
2. The Home / Capabilities page opens with **Working Recipes** at the top:
   "Start here: run a useful local recipe."
3. Click any recipe button. The card shows the last result and the report path.
4. The Artifacts page lists generated operator reports.

Endpoints (localhost only):
- `GET /api/product-control/operator-recipes` - list recipes via the CLI
- `POST /api/product-control/run-operator-recipe` - run one allowlisted recipe id
- `GET /api/product-control/latest-operator-recipe-runs` - cached run summaries

## What reports are generated

Every report is Markdown with the same honest structure: **What happened**,
**What Ghoti did**, **What Ghoti refused to do**, **What files/reports were
created**, **What the user can do next** (starting with "Next action:"), and
**What remains disabled**. Reports land in
`14_context/operator_reports/generated/` (gitignored; never committed).

## What supervised means

You click or run a command; Ghoti does bounded read-only work plus a repo-local
report write; you read the result. Nothing executes in the background, nothing
acts on your accounts, and the policy check runs before the recipe body.

## What is blocked (and why that is good)

Live agents, account actions, provider/API calls, Telegram, Obsidian, MCP,
browser automation, computer-use, auto-submit, file deletion, file moves, and
all writes outside the repo. The policy is deny-by-default: a capability that
is not explicitly allowed is denied, including unknown future capabilities.

## Policy enforcement detail

- Manifest: `23_configs/operator_recipe_policy.example.json` (deny-by-default).
- Rust checker: `rust/ghoti_policy_checker` now allows the two recipe
  capabilities `report_write_repo_local` and `local_model_status_read`
  alongside the existing read-only set, and has unit tests proving the recipe
  capability set is allowed while `external_write` stays denied.
- When `rust/target/{release,debug}/ghoti_policy_checker` exists, every recipe
  run invokes it (`--input plan.json`) and records
  `rust_checker_available: true, rust_checker_used: true`.
- Without the binary, the Python mirror enforces the same lists and the run
  records the mirror as the checker. Either way the JSON declares requested,
  allowed, and denied capabilities explicitly.

## What not to claim

- Do not claim live autonomy: recipes are supervised report generators.
- Do not claim Telegram/Obsidian/MCP exist: they are roadmap only.
- Do not claim model readiness without running `local-model-check`.

## How to demo to an investor

1. Open the dashboard; point at "Working Recipes - Start here".
2. Click **Run All Safe Recipes** (about 20 seconds).
3. Open the project health report: real git truth, real audit result.
4. Open the fixture replay report: real parallel planning, nothing launched.
5. Point at "What remains disabled": blocking unsafe behavior is the feature.

## What comes next

1. **Obsidian curated memory** - repo-local curated notes bridge.
2. **Telegram status notifications** - notification-only, no inbound commands.
3. **Supervised action recipes** - recipes that propose a bounded mutating
   action and execute it only after an explicit approval token.

## Codex audit target

`audit/ghoti-agent-codex-n6-40a-working-mvp-runtime-recipes`
