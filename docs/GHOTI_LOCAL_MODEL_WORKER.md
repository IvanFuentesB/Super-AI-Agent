# Ghoti Local Model Summary and Classification Worker

`local-model-summary-classification-worker` is Ghoti's second approved local
worker. It runs through the existing Agent OS approval queue, Rust guard,
single-active-worker lock, bounded runtime, cancellation path, capped logs,
and evidence trail.

The worker reads only declared repo-local text. It returns a source-linked
summary, classification tags, confidence and uncertainty, and a recommended
handoff target. Its current mode is `deterministic_local_fallback`; it makes no
provider call and uses no network.

## Commands

```powershell
python 03_scripts/agent_os/ghoti_agent_os.py --propose-worker-run local-model-summary-classification --json
python 03_scripts/agent_os/ghoti_agent_os.py --approve-action <request_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --execute-approved <request_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --full-local-model-worker-demo --json
```

## Safety Contract

- Fixed worker identity, entrypoint, arguments, task, and registry fingerprint
- Declared repo-local inputs and outputs only
- One worker active at a time
- Bounded runtime, cancellation, and capped stdout/stderr
- No browser, computer-use, accounts, email, posting, purchases, money, or
  external writes
- Worker output is data and is never interpreted as a command

Local Ollama/Gemma routing can be added only through a separately audited
revision. The deterministic fallback is the truthful mode today.
