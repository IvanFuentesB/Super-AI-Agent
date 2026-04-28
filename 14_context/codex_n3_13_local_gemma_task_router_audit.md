# Codex N+3.13 Local Gemma Task Router Audit

Status: codex_parallel_audit / router_policy_only / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## 1. Current Truth

| Field | Truth |
| --- | --- |
| Ollama installed | YES |
| Ollama path in Codex shell | `C:\Users\ai_sandbox\AppData\Local\Programs\Ollama\ollama.exe` |
| Ollama version in Codex shell | `0.21.2` |
| Installed models | NONE (`ollama list` returned no models) |
| Gemma model installed | NO |
| Local brain inference ready | NO |
| Current blocker | `gemma3:4b` has not been pulled in this shell |
| User approval phrase present | YES: `APPROVE OLLAMA PULL GEMMA3:4B FOR LOCAL BRAIN SMOKE` |

Earlier Claude lane docs saw Ollama through a different user/path context (`C:\Users\Navif\AppData\Local\Programs\Ollama\ollama.exe`, version `0.9.2`). Codex currently resolves the `ai_sandbox` path. Both truth records should stay documented because Ghoti shell behavior can differ by execution lane.

Codex did not run `ollama pull`, `ollama run`, or any model inference in this audit.

## 2. Desired Router Behavior

The next safe local-brain step is a preview-only router that recommends which brain should handle a task. It must not dispatch work automatically.

- Easy local text tasks should be suggested for Gemma/Ollama after the model is installed and smoke-tested.
- Hard coding, multi-file architecture, test repair, and repo-wide implementation should remain Claude Code or Codex work.
- Uncertain, risky, external, destructive, or account-connected tasks should escalate to human approval and a stronger model.
- The router should emit a reason, confidence, risk label, and required approval labels before any action is considered.

## 3. Task Classes Gemma Should Handle

Gemma/Ollama is best suited for cheap, local, reversible, text-only work after a successful local smoke test:

- Summarize local docs.
- Compress memory notes.
- Draft queue summaries.
- Classify tasks by difficulty and risk.
- Create first-pass markdown plans.
- Extract TODOs from local logs.
- Rewrite internal notes.
- Generate low-risk checklist drafts.
- Compare small local text snippets.
- Produce short status blurbs for dashboard read models.

## 4. Task Classes Gemma Should Not Handle Alone

Gemma must not be treated as an autonomous operator or trusted executor.

- Multi-file code edits.
- Security-sensitive changes.
- CUA/browser execution.
- Live-account actions.
- Money, business posting, outreach, purchases, trades, or filings.
- Installs, package pulls, Docker pulls, model pulls, or image pulls.
- Deletes, cleanup, or destructive filesystem operations.
- Git commits or pushes.
- External API actions.
- Legal, financial, medical, tax, or regulated decisions.
- Any task whose failure could affect credentials, accounts, money, reputation, or private data.

## 5. Proposed Router Policy

| Task shape | Suggested brain | Approval |
| --- | --- | --- |
| Simple / local / reversible / text-only | Gemma after smoke | No, if read-only |
| Local summary from one or a few small files | Gemma after smoke | No, if read-only |
| One-file code change | Gemma may draft, Claude/Codex reviews and applies | Usually yes before commit |
| Multi-file code change | Claude Code or Codex | Yes for risky changes |
| Architecture / security / external action | Claude/Codex plus user approval | Yes |
| CUA, browser, Docker, Screenpipe, installs, model pulls | Claude/Codex execution lane only | Yes |
| Destructive or irreversible action | Human approval and audit trail | Yes, always |

Router output should be advisory:

```json
{
  "recommended_brain": "gemma_local | codex | claude_code | human",
  "difficulty": "easy | medium | hard",
  "risk_level": "low | medium | high | blocked",
  "approval_required": false,
  "reason": "short explanation",
  "runtime_wiring_truth": "preview_only"
}
```

## 6. Proposed Implementation Later

Recommended first implementation should stay preview-only:

- Add `23_configs/local_brain_task_policy.example.json`.
- Add a CLI dry-run classifier such as `brain_route_preview.py`.
- Add a dashboard read-only `suggested_brain` field later, if safe.
- Use compact task specs and file references instead of pasting large docs.
- Require a local Gemma smoke result doc before any `recommended_brain: gemma_local` output is allowed.
- Do not automatically dispatch work to Gemma, Claude, Codex, CUA, n8n, or any external adapter.

## 7. Verdict

Next implementation should be policy/config plus dry-run classification only. Ghoti should not wire autonomous routing yet. Gemma can become the cheap local worker for easy text tasks only after `gemma3:4b` is pulled, smoke-tested, and documented.
