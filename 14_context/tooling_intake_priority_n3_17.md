# Tooling Intake Priority — N+3.17

Date: 2026-04-28
Milestone: N+3.17
Branch: feat/ghoti-visible-operator-stack
Status: planning_only / no_installs

---

## Urgent — Now

These are implemented or actively in use:

| Tool | Status | Notes |
|---|---|---|
| Gemma context compression | ACTIVE — `local_brain_router.py --task compress_context` | Free local compute; repo-root-only; artifact outputs only |
| Money workflow tracker/templates | ACTIVE — `14_context/money_workflows/` | Templates only; no live actions |
| Experiment generation script | ACTIVE — `03_scripts/money_workflow_new_experiment.py` | JSONL append only; no external API |
| Distribution tracking | ACTIVE — `distribution_and_exposure_checklist.md` | Checklist only; no accounts wired |
| Dashboard launcher | ACTIVE — `03_scripts/run_dashboard.ps1` | Operator-triggered; no auto-start |
| Local brain router preview | ACTIVE — `local_brain_router.py --preview` | preview_only mode |

---

## Soon — Next 1–3 Milestones

Tools to plan, evaluate, and optionally approve in upcoming milestones:

| Tool | Candidate purpose | Approval required before | Notes |
|---|---|---|---|
| PaperclipAI | Zero-human-company style control plane — orchestrate agents and tasks | APPROVE PAPERCLIP INSTALL | Planning_only. Do not install/wire. Review isolated install plan first. |
| n8n | Deterministic workflow rails for multi-step automation | APPROVE N8N INSTALL | Planning_only. Local Docker install path. Review before any containers. |
| OpenClaw | Worker/channel/multi-agent candidate for remote-assistant and browser-assist | APPROVE OPENCLAW RUNTIME WIRING | Reference material. Do not wire until control boundary is clear. |
| Skills system | `.claude/skills/` — wrap common Ghoti workflows for one-command invocation | No approval needed for skill files | Low risk. Skills are markdown configs, not code installs. |

---

## Future Game Lane

| Tool | Candidate purpose | Status | Approval required |
|---|---|---|---|
| `ivanmurzak/Unity-MCP` | AI-assisted Unity workflow for Google Play / App Store game pipeline | tracked_only / not_installed | APPROVE UNITY-MCP INSTALL before any install, clone, or run |
| Unity Hub | Game engine install | not_installed | Yes — separate approval for Unity Hub install |
| Google Play Console | App distribution | no_account | Yes — account creation and payment setup |
| App Store Connect | iOS distribution | no_account | Yes — Apple Developer Program ($99/year) |

Do NOT install Unity, Unity-MCP, or touch app-store accounts without explicit approval.
See `14_context/money_workflows/simple_phone_game_pipeline.md` for the full plan.

---

## Mythos / Leaked Repo Ecosystem

**Status: audit-only / risk-only / NO leaked code**

Mythos refers to any leaked, proprietary, or unreleased Anthropic code or related ecosystem repos.

Safe lessons from documented public research:
- Strict verification loops before execution
- Correction loop architecture (retry with audit trail)
- File hash truth (verify files before trusting)
- Task budget tracking (stop after N failures)
- Audit log patterns (persist events for review)
- Defensive default behavior (safe-by-default, not attack-by-default)

Unsafe / prohibited:
- Cloning leaked or proprietary Anthropic repos
- Installing leaked code into the runtime
- Running offensive cyber tools
- Unrestricted autonomous security agents
- Any code derived from non-public Anthropic sources

**Do not clone, install, run, copy, or depend on leaked/proprietary Anthropic code. Ever.**

---

## Dolphin / Uncensored Models

**Status: evaluation-only / no_runtime_wiring**

Dolphin and similar uncensored local models may be useful for:
- Legitimate local analysis where safety filters are too restrictive for the task
- Evaluating model quality for specific domains
- Research and comparison

Prohibited uses:
- Bypassing legal restrictions or platform safety rules
- Generating harmful, deceptive, or illegal content
- Replacing safety gates or approval flows in the runtime
- Any live account, financial, or legal action

Do not install uncensored models without a clear, legitimate use case and explicit operator approval.

---

## CUDA / GPU Acceleration

**Status: documentation_only / no_installs_now**

CUDA is the primary path for accelerating local inference on NVIDIA GPUs.

Benefits (future):
- 3–10x faster Gemma inference on compatible GPU
- Enables larger local models (7B, 13B, 70B)
- Reduces per-task time for compression and drafting

Current status:
- No CUDA installed in this environment
- Gemma3:4b runs via CPU-only Ollama currently
- Install CUDA only when GPU inference is a clear bottleneck and the GPU is confirmed compatible

Approval required before: CUDA Toolkit install, Ollama GPU build, any driver changes.

---

## What Is NOT Being Installed in N+3.17

- PaperclipAI — planning_only
- OpenClaw — reference_only
- n8n — planning_only
- Unity / Unity Hub — not_installed
- Unity-MCP — not_installed
- Dolphin / uncensored models — not_installed
- CUDA — not_installed
- Manus — not_evaluated
- Any leaked / proprietary Anthropic code — PROHIBITED
