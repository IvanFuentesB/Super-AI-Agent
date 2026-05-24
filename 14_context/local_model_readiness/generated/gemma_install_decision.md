# Gemma Install Decision

N+5.9A prepares the decision; it does not download a model.

## Recommended First Command

```powershell
ollama pull gemma3:4b
```

Human approval required before model download. Ghoti must not run this command automatically.

## Why `gemma3:4b`

Best first balance for useful summaries, classification, and compact context work without jumping to 12B/27B.

- Disk note: Ollama lists gemma3:4b at about 3.3GB.
- Context note: Gemma 3 4B is documented with a 128K context window on Ollama.
- Caution: Needs local disk and enough RAM/VRAM; install manually only after Ivan approves the pull.

## Lighter Alternatives

```powershell
ollama pull gemma3:1b
ollama pull gemma3:270m
```

Use gemma3:1b or gemma3:270m when Ivan wants a quick low-risk local smoke before the 4B model.

## Current Recommendation

gemma3:4b is installed. Run the local quality plan next, but keep production routing disabled until a later human-approved milestone.

Production routing remains disabled until a later human-approved quality milestone.
