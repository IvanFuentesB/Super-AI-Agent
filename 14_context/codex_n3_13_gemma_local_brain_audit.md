# N+3.13 Codex Gemma Local Brain Audit

Status: codex_parallel_audit / local_brain_audit / no_model_pull / not_runtime_wired

Date: 2026-04-28
Branch: feat/ghoti-visible-operator-stack

## Commands Run

```powershell
ollama --version
ollama list
where.exe ollama
Get-Command ollama
```

Codex did not run `ollama pull`.

## Ollama Truth From Codex Shell

| Field | Truth |
| --- | --- |
| Ollama installed | YES |
| Ollama path | `C:\Users\ai_sandbox\AppData\Local\Programs\Ollama\ollama.exe` |
| Ollama version | `0.21.2` |
| Installed models | none; `ollama list` is empty |
| Gemma available locally | NO |
| Local brain usable now | NO |

Note: Prior Claude docs recorded Ollama `0.9.2` from a different user/path context. Codex's current shell resolves to the `ai_sandbox` Ollama install at version `0.21.2`.

## Approval Truth

User provided:

```text
APPROVE OLLAMA PULL GEMMA3:4B FOR LOCAL BRAIN SMOKE
```

This approval is sufficient for Claude Code to pull `gemma3:4b` in the main execution lane. Codex still did not pull because this task is audit/documentation only.

## Risk Notes

- Disk usage: model download likely multiple GB.
- Network usage: pulls from Ollama model registry.
- Time: download and first load may take several minutes.
- Performance: local inference may be slow depending CPU/GPU availability.
- Capability: local Gemma can help with compact summaries and simple local reasoning, but it must not drive CUA or operator actions without explicit approval gates.

## Recommended First Smoke

After Claude pulls the approved model:

```powershell
ollama run gemma3:4b "Return exactly: GHOTI_LOCAL_BRAIN_OK"
```

Pass condition:

```text
GHOTI_LOCAL_BRAIN_OK
```

If the model responds with extra text, record it honestly and decide whether to retry once or lower expectations for deterministic local-brain use.

## Readiness Verdict

| State | Verdict |
| --- | --- |
| Before pull | Not ready: Ollama installed, no models |
| After successful `gemma3:4b` pull | Ready for tiny local-brain smoke only |
| After tiny smoke succeeds | Candidate for low-risk summaries and diagnostics |
| Operator/autonomy use | Still not ready without routing, approval gates, and quality validation |

## What Remains Forbidden

- No provider cap bypass.
- No autonomous computer-use actions.
- No click/type driven by Gemma.
- No external posting, outreach, trades, legal/tax filings, or live-account actions.
- No claim that Gemma drives Ghoti until runtime routing is actually built and validated.
