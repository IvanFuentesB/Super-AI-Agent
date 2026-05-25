CLEAN PASS / N+6.1B FINAL MAIN AUDITED

Branch:
- Final origin/main: 39daf4d81f8a5dc123c9949ce6d7c3ea49763978
- Final main audit branch: audit/ghoti-agent-codex-n6-1b-final-main-constrained-local-model-routing-guard
- Merged feature: feat/ghoti-agent-codex-n6-1a-constrained-local-model-routing-repo-bundle-guard
- Feature commit: 7d4069189efb1d454ae3380eeff3f579db596b39
- Merged audit: audit/ghoti-agent-codex-n6-1a-constrained-local-model-routing-repo-bundle-guard
- Audit commit: c2ee56a448eff38d49da405432feb95c56470e2f
- Main merge/report commit: 39daf4d81f8a5dc123c9949ce6d7c3ea49763978

Validation:
- git diff --check: PASS
- git show --check --stat HEAD: PASS
- N+4 runtime tests: 329 OK
- N+5 runtime tests: 97 OK
- N+6 runtime tests: 14 OK
- Total runtime tests: 440 OK
- Launcher smoke: PASS
- Context pack generation: PASS
- Local worker status/demo: PASS
- Gemma status: PASS
- Local model eval: PASS
- Launcher routing status: PASS
- Launcher route-task status-paragraph: PASS
- Launcher routing demo: PASS
- Local model routing status: PASS
- Local route-task status-paragraph: PASS
- Local routing demo: PASS
- Output guard self-test: PASS
- Hermes bridge status: PASS
- Repo map status: PASS
- Public repo security audit: 150 checks, 0 blockers, 7 warnings requiring human review
- Model council scan: PASS
- UI-TARS dry-run: PASS, observation-only
- Approved adapter runner status: PASS, approval-gated/local-only
- External sandbox status: PASS, static inspection only
- Supervised content demo validate-latest: PASS
- Node syntax checks: PASS
- Runtime PowerShell check: PASS
- Dashboard PowerShell check: PASS

Status Truth:
- Gemma installed: yes, gemma3:4b
- Active model lane: ollama_gemma_guarded
- Routing readiness: 82%
- Guard enabled: true
- Source metadata required: true
- Production routing enabled: false
- Safe tasks: summarize-latest-report, status-paragraph, codex-next-prompt, safety-classification, context-bundle-summary, next-milestone-outline, report-to-bullets
- Fallback: local_demo remains available when guard rejects or Gemma is unavailable

Hermes / WSL:
- WSL Ubuntu installed.
- Hermes path: /home/ai_sandbox/.local/bin/hermes
- Hermes version: Hermes Agent v0.14.0 (2026.5.16)
- Hermes readiness: 58%
- Codex provider: pending/not proven
- Telegram: manual later/no token
- Browser/Playwright: degraded/not claimed
- No VPS

Safety:
- No live APIs used.
- No browser automation performed.
- No computer-use click/type performed.
- No account actions performed.
- No Hermes provider setup or Telegram setup performed.
- No additional model pulls performed.
- UI-TARS remains observation-only.
- Adapter runner remains approval-gated/local-only.
- External sandbox remains static inspection only.

Commands:
- Launcher: python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard
- Dashboard: http://127.0.0.1:3210
- Gemma status: python 03_scripts/ghoti_product_launcher.py --gemma-status --json
- Routing status: python 03_scripts/ghoti_product_launcher.py --local-worker-routing-status --json
- Hermes bridge: python 03_scripts/ghoti_product_launcher.py --hermes-bridge-status --json

Cleanup:
- Validation-only generated files were restored before this report.
- Duplicate routing demo directories generated during validation were removed after path containment checks.
- No broad process kills were used.
- Primary worktree remained read-only except inspection.

Final Verdict:
CLEAN PASS / N+6.1B MAIN AUDITED
