# Codex N+3.50C - Ruflo Install Gate Audit

Milestone: N+3.50C - Dashboard/Ruflo/Gemma parallel audit lane

Date: 2026-05-06

## Scope

This is a Codex audit/source-check doc only. No Ruflo install was run. No npm command was executed. No Claude Code, MCP, browser, social, email, payment, scraping, job, or account tooling was connected.

## Repo And Branch Truth

- Base branch: `feat/ghoti-visible-operator-stack`
- Base HEAD at audit start: `e7e946a26bea677d37d00370590d827f3ec82b3a`
- Codex audit branch: `audit/ghoti-agent-codex-n3-50-dashboard-ruflo-gemma-audit`
- Expected Claude branch: `feat/ghoti-agent-claude-n3-50-dashboard-ruflo-gemma`
- Claude branch status at audit start: not found on origin.

This doc prepares the audit gate for Claude's expected N+3.50 dashboard/Ruflo/Gemma implementation.

## Source-Check Summary

Primary sources checked:

- Ruflo GitHub repository: `https://github.com/ruvnet/ruflo`
- npm `npm ci` docs: `https://docs.npmjs.com/cli/v8/commands/npm-ci/`
- npm scripts lifecycle docs: `https://docs.npmjs.com/cli/v7/using-npm/scripts/`
- Python subprocess docs: `https://docs.python.org/3/library/subprocess.html`

Findings:

- Ruflo presents itself as a multi-agent orchestration platform for Claude/Codex/MCP-style workflows. That makes it powerful and high-risk by design.
- Local package metadata from the existing eval repo previously identified package name `claude-flow` and version `3.5.80`.
- npm lifecycle docs show `npm ci` can run lifecycle scripts such as `preinstall`, `install`, `postinstall`, and `prepare`.
- npm `ignore-scripts=true` means npm does not run scripts specified in `package.json` files, but commands explicitly intended to run scripts can still run their intended script. This is why no `npm run ...`, `npm start`, `npm test`, or swarm command is allowed in the install gate.
- npm audit behavior defaults to submitting audit reports unless disabled. This means `npm ci --ignore-scripts` is safer than normal install for script execution, but it is not "offline" or "no network".
- Python subprocess docs emphasize reading security considerations before `shell=True`; local gate scripts should use list-argument subprocess calls and avoid shell command strings.

## Allowed Ruflo Install Command

Allowed only after explicit operator approval:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only\21_repos\third_party\evals\ruflo
npm ci --ignore-scripts
```

This is allowed only because:

- It is isolated inside the Ruflo eval directory.
- It is not global.
- It is not Ghoti runtime wiring.
- It skips package lifecycle scripts.
- It creates local dependency files only.
- It should not be staged into the main repo.

Stricter optional variant if the operator wants to reduce npm audit/funding network chatter:

```powershell
npm ci --ignore-scripts --audit=false --fund=false
```

Do not treat the stricter variant as already approved unless the operator chooses it.

## Prohibited Commands

Do not run:

```powershell
npm install -g claude-flow
npm install -g ruflo
npx claude-flow init
npx claude-flow start
npx claude-flow hive-mind spawn ...
npm run dev
npm run build
npm start
npm test
npm run v3:swarm
npm run v3:domains
```

Also prohibited:

- no global install
- no swarm launch
- no MCP launch
- no Claude API key
- no GitHub connector wiring
- no browser/desktop control
- no live account actions
- no email/social/payment/job/giveaway actions
- no scraping
- no `.env`, credential, token, or OS environment reads
- no background processes
- no repo writes outside a declared lane

## Expected Claude-Owned Ruflo Files To Audit

Claude N+3.50 may add:

- `03_scripts/ruflo_install_gate.py`
- `14_context/tooling/ruflo_install_gate_n3_50a.md`
- `23_configs/ruflo_install_gate.example.json`

Audit checklist:

- Python stdlib only.
- Dry-run default.
- `--apply` required before install.
- Path must resolve inside `21_repos/third_party/evals/ruflo`.
- Reject global install.
- Refuse if `package.json` has lifecycle scripts: `preinstall`, `install`, `postinstall`, `prepare`.
- Prefer `npm ci --ignore-scripts` when `package-lock.json` exists.
- Never run `npm run ...`.
- Never launch MCP or swarms.
- Never read `.env`.
- Never stage `node_modules`.
- Write report only under `05_logs/ruflo_install_gate/<run_id>/`.
- Log command, cwd, return code, stdout/stderr excerpt.
- Include human approval phrase in docs before `--apply`.

## Safety Verdict

Verdict: CONDITIONAL SAFE FOR ISOLATED INSTALL GATE ONLY.

Ruflo is not safe to wire into Ghoti runtime yet. It is practical to move from source-check to isolated dependency install if and only if the gate script enforces the boundaries above.
