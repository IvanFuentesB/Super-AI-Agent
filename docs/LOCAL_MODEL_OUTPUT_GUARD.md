# Local Model Output Guard

The N+6.1A output guard exists because the first real `gemma3:4b` evaluation produced one hallucinated repo-bundle answer: it invented `StableLM-DanceDiffusion` and cited an external GitHub path. That was useful evidence, but not safe enough for routing.

The guard now requires every routed model answer to include `source_metadata` with:

- known repo bundle IDs from `14_context/repo_knowledge/generated/repo_knowledge_map.json`
- known repo file paths from the generated repo map
- `local_only=true`
- `live_api_used=false`

The guard rejects:

- invented bundle IDs
- unknown source files
- URLs or external repo claims
- missing source metadata
- claims that provider setup, Telegram, browser/Playwright, live APIs, or production routing are enabled

Run:

```powershell
python 03_scripts/local_model_output_guard.py --self-test --json
```

Safety boundaries: no live APIs, no provider setup, no token reading, no browser actions, no shell command execution, and no file edits from model output.
