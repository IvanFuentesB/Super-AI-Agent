# Codex N+3.62 LLM Council Safety Audit

## Verdict

LLM Council verdict: NOT AUDITED

Reason: the requested N+3.61A remote target branch is missing.

Codex cannot claim that the LLM Council scaffold is implemented, local-first, safe, or merge-ready until the target branch exists and the required commands pass on the merged test state.

## Required LLM Council Behavior

The future branch must implement `03_scripts/llm_council_runner.py` with a local-first, Karpathy-style three-stage flow:

1. Stage 1: first opinions from named or configured council members.
2. Stage 2: anonymized peer review over first opinions.
3. Stage 3: chairman synthesis with explicit human-review markers.

Required safety properties:

- `local_demo` mode works without API keys.
- External providers are disabled by default.
- No OpenRouter/OpenAI/Anthropic/Gemini/Grok API calls happen by default.
- No `.env` or secret/token/credential files are read.
- No API keys are printed, stored, logged, or required for local demo.
- `label_to_member` mapping is stored only in metadata, not injected into peer-review labels.
- Runtime logs remain unstaged.
- Outputs include markers such as `HUMAN_REVIEW_REQUIRED`, `NO_AUTONOMOUS_ACTION`, or equivalent.

## Required Commands For Future Audit

Run these only after the target branch exists and has been no-commit merged into a clean audit worktree:

```powershell
python 03_scripts/llm_council_runner.py --status
python 03_scripts/llm_council_runner.py --demo --dry-run
python 03_scripts/llm_council_runner.py --ask "How should Ghoti use an LLM council safely?" --dry-run
python 03_scripts/llm_council_runner.py --ask "How should Ghoti use an LLM council safely?" --apply
python 03_scripts/llm_council_runner.py --list-sessions
```

Audit must confirm:

- Stage 1 exists.
- Stage 2 exists.
- Stage 3 exists.
- Metadata exists.
- Generated session files are local-only.
- Generated session files are not staged unless explicitly intended for audit docs, which they should not be.

## External Provider Gate

External providers may be documented for later, but they must not be active by default.

Unsafe by default:

- OpenRouter API call
- OpenAI API call
- Anthropic API call
- Gemini API call
- Grok/xAI API call
- `.env` key loading
- token or credential discovery
- clipboard automation
- browser automation
- live posting, email, payment, trading, account, or scraping action

## Current Direct Answers

- LLM Council implemented? Unknown, target missing.
- Karpathy-style three-stage flow present? Unknown, target missing.
- External API calls enabled? Unknown on target; must be NO by default.
- OpenRouter key stored? Unknown on target; must be NO.
- Ollama required? Unknown on target; local demo should not require external keys and should degrade truthfully if Ollama/model unavailable.
