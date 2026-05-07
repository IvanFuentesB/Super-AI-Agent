# Codex N+3.13 Next Claude Implementation Review

Status: codex_parallel_audit / implementation_review_only / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## 1. Current State

- CUA path is near execution but remains approval-gated.
- Docker/WSL appears ready from user/Claude evidence, although Codex's own shell previously could not access the Docker daemon.
- CUA digest approval exists for `sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a`.
- ActionIntent payload hash exists and matches: `69149d31f052bfce0d15e383797b3fbbeee80dc351f3a2e100f1746fb51418e4`.
- Gemma/Ollama is installed as Ollama only; `ollama list` is empty in Codex's shell.
- User approved the Gemma pull phrase: `APPROVE OLLAMA PULL GEMMA3:4B FOR LOCAL BRAIN SMOKE`.
- Persistent dashboard is still planning-only; first safe step is a PowerShell launcher.

## 2. What Claude Code Should Do Next

A. Finish/push pending commits if needed.

B. Pull Gemma3:4B only because user approved:

```text
APPROVE OLLAMA PULL GEMMA3:4B FOR LOCAL BRAIN SMOKE
```

C. Run local brain smoke:

```powershell
ollama run gemma3:4b "Return exactly: GHOTI_LOCAL_BRAIN_OK"
```

D. Record results in:

```text
14_context/gemma_local_brain_smoke_n3_13.md
```

E. Add or update the wait/resume seed for local brain ready.

F. Do not wire Gemma as an autonomous router yet.

## 3. CUA Next Step

Digest approval exists:

```text
APPROVE CUA IMAGE DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a FOR SCREENSHOT-ONLY SMOKE
```

Payload approval has not been explicitly provided unless the user says the exact payload phrase:

```text
APPROVE CUA SCREENSHOT-ONLY SMOKE WITH DIGEST sha256:2bb539bd42f59f9e2a889faa4ebcb535a0c06397a3b98e45fd5cc8a96c22014a AND PAYLOAD 69149d31f052bfce0d15e383797b3fbbeee80dc351f3a2e100f1746fb51418e4
```

Claude should not run the screenshot smoke until that exact payload approval is present. Digest approval is enough for the image gate, not for execution of a containerized screenshot smoke.

## 4. Persistent Dashboard

Implement next only if current CUA/Gemma smoke work is stable.

Recommended first step:

- Create `03_scripts/run_dashboard.ps1`.
- Add simple desktop shortcut instructions.
- Start from repo root or dashboard directory safely.
- Print localhost URL.
- Avoid admin requirements.
- Avoid background daemon behavior unless separately approved.

Do not add a Windows service yet. Do not add Electron/Tauri yet. Do not add autostart yet.

## 5. What Claude Code Should Avoid

- No OpenClaw install.
- No n8n install.
- No autonomous router.
- No live browser actions.
- No click/type.
- No account login.
- No auto-posting.
- No provider cap bypass or quota evasion.
- No external adapter execution without ActionIntent, payload hash, approval, and audit trail.

## 6. Recommended Next Claude Milestone

N+3.13-Claude — Gemma/Ollama local brain smoke + CUA approval gate reconciliation.

This should prioritize:

1. Pull approved Gemma model.
2. Run tiny local-brain smoke.
3. Record truthful local-brain status.
4. Confirm CUA digest gate status.
5. Stop before CUA screenshot execution unless the exact payload approval phrase is present.

## 7. Recommended Later Milestone

N+3.14 — preview-only brain router policy/config + agent registry docs.

Suggested outputs:

- `23_configs/local_brain_task_policy.example.json`
- `23_configs/brain_routing_policy.example.json`
- `20_agents/agent_registry.example.json`
- `17_integrations/n8n_plan.md`
- `02_automation/workflow_intake_plan.md`

## 8. Verdict

Prioritize Gemma smoke now because it reduces API dependence fastest and carries less operational risk than CUA. Keep CUA screenshot smoke gated until exact payload approval is provided. Keep all routing and multi-agent orchestration preview-only until the local brain and approval trail are proven.
