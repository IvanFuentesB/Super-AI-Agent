# Guarded Local Routing Quality Review

- Tasks routed: 3
- Guard enabled: true
- Fallback used: false
- Live APIs used: false
- Commands executed from model output: false
- Files edited from model output: false

N+6.0A hallucination fix: Gemma previously invented a `StableLM-DanceDiffusion`
bundle and cited an external GitHub URL. N+6.1A now rejects invented bundle IDs,
unknown source files, URLs, and missing source metadata before a routed answer can
be accepted.
