        # Local Task Quality Evaluation Plan

        Current quality status: `ready_for_human_approved_eval`.

        ## Tasks

        - Summarize latest Ghoti report: Compress the latest milestone report into compact memory.
- Produce one-paragraph human status: Give Ivan a concise truthful local MVP status.
- Classify next task: Classify work as coding, docs, audit, content, research, or safety.
- Generate concise Codex prompt from context pack: Create a small handoff prompt without leaking secrets.
- Identify relevant repo bundle: Pick the right repo knowledge bundle for a task.
- Detect unsafe automation request: Refuse unsafe autonomous action and suggest a safe alternative.
- Compress long report to 10 bullets: Summarize a long audit report while preserving status truth.

        ## Current Evaluation Result

        - Mode: `gemma_available_not_invoked`
        - Model: `gemma3:4b`
        - Tasks total: `7`
        - Tasks passed: `7`
        - Score percent: `55`
        - Safety gate passed: `True`
        - JSON validity passed: `True`
        - Production routing recommended: `False`

        This is a deterministic local_demo quality-plumbing result unless a real Gemma model is installed and a later human-approved milestone runs model prompts. Production routing remains disabled.

        To load or run the N+6.0A local evaluation summary, use `python 03_scripts/ghoti_product_launcher.py --local-model-eval --json`.
