# Codex N+3.58 - Next Sequence Lock

## Recommendation

Run one more tiny Claude fix before merge.

N+3.56-FIX is close and safety-safe, but not a clean PASS because Obsidian/dashboard commands crash and target whitespace fails cached diff check.

## Exact Next Claude Recommendation

```text
N+3.58-FIX - Obsidian Permission Handling, Dashboard Probe Safety, Whitespace Cleanup
```

Branch:

```text
feat/ghoti-agent-claude-n3-58-fix-obsidian-dashboard-whitespace
```

Scope:

- Fix `obsidian_probe.py` permission-denied handling.
- Fix `ghoti_dashboard.py` Obsidian probe crash.
- Ensure `open_obsidian_vault.ps1 -Check` does not show Python tracebacks.
- Clean `14_context/ghoti_dashboard_card.md` trailing whitespace.
- Re-run the N+3.58 validation subset.

## Exact Next Codex Recommendation

After Claude pushes the fix branch, Codex should run a narrow re-audit focused on:

- `obsidian_probe.py --status`
- `obsidian_probe.py --json`
- `ghoti_dashboard.py --status/json/card --dry-run`
- `git diff --cached --check`
- branch merge test

## Merge Now?

Not recommended if the goal is clean 90-94%.

If the operator accepts a conditional merge, use `codex_n3_58_merge_plan.md`, but Codex recommends fix-first because the failing dashboard/Obsidian commands are user-visible.

## Direct Answers

- CC/Codex automatic yet? No, manual by design.
- Ruflo source/install usable yet? Source absent, install not usable yet; gate is truthful.
- Ruflo runtime wired? No.
- Gemma usable? Ollama found, Gemma model not found, so not usable for real compression yet.
- Obsidian accessible? Vault yes; app/probe status fails due permission handling.
- Course helper supports `--goal` safely? Yes.
- Java tracked? No.
- Rust tracked? No.
- Should Rust replace current MVP now? No.
