# Codex N+4.4D Preview Path Containment Fix Real Audit 2

## Verdict

**Final verdict: CLEAN PASS**

N+4.4D fixes the N+4.4B preview path containment blocker. The target branch rejects sibling-prefix outside paths such as `C:\Users\ai_sandbox\Documents\AI_Managed_Only_evil\fake.html`, preserves valid repo-local HTML preview behavior, and keeps the stacked N+4.3A/N+4.4A/N+4.4B/N+4.4C functionality passing.

## Remote Truth

| Item | Result |
| --- | --- |
| Audit branch | `audit/ghoti-agent-codex-n4-4d-preview-path-containment-fix-real-audit-2` |
| Target branch | `origin/feat/ghoti-agent-claude-n4-4d-preview-path-containment-fix` |
| Target remote ref | `refs/heads/feat/ghoti-agent-claude-n4-4d-preview-path-containment-fix` |
| Remote hash from `ls-remote` | `e633261e3f06617f9631905d97ad1101340374cc` |
| Local fetched target hash | `e633261e3f06617f9631905d97ad1101340374cc` |
| Base main commit | `e16101992bf95447a6cb697e12c8c843c3c519a8` |
| Polling result | Branch appeared on poll attempt 13; remote and local fetched refs matched. |
| Fetch staleness | Not stale. |

## Stack Verification

| Required commit | Purpose | Verified |
| --- | --- | --- |
| `1fb7804ce7f2e71c5a34f6d810235fe770b5e2de` | N+4.3A content studio demo | Yes |
| `1521269533fcd457403ed730a884341f1e44aee6` | N+4.4A desktop operator control plane | Yes |
| `ad00a6b24e3141dc8abae1c5964690fbacf98007` | N+4.4B dashboard action center | Yes |
| `d64024bdced345ab4ea67da2c89af41acdb39aec` | N+4.4C recipe runner preview polish | Yes |
| `e633261e3f06617f9631905d97ad1101340374cc` | N+4.4D preview path containment fix | Yes |

No-commit merge rehearsal from `origin/main` into the isolated audit worktree completed with no conflicts.

## Changed Files

Target commit `e633261` directly changes:

| File | Purpose |
| --- | --- |
| `01_projects/dashboard_mvp/server.js` | Replaces vulnerable preview path containment with `path.relative()` based containment. |
| `01_projects/runtime_mvp/tests/test_n4_4d_preview_path_containment_fix.py` | Adds static and live endpoint containment tests. |
| `14_context/claude_n4_4d_preview_path_containment_fix.md` | Claude implementation report. |

The stacked branch also carries the expected N+4.3A/N+4.4A/N+4.4B/N+4.4C files and seed local-only artifacts.

## N+4.4B Blocker Resolution

| Check | Result |
| --- | --- |
| Previous bad pattern | `normalizedPath.startsWith(repoRoot)` accepted sibling-prefix paths. |
| Secure containment helper present | Yes, `isPathInsideRepo(candidate)` uses `path.resolve()` plus `path.relative()`. |
| Rejects repo root equality | Yes, `relative === ""` is rejected. |
| Rejects parent traversal | Yes, `relative.startsWith("..")` is rejected. |
| Rejects absolute relative result | Yes, `path.isAbsolute(relative)` is rejected. |
| `/api/desktop-operator/preview` uses containment helper | Yes. |
| `startsWith(repoRoot)` containment remains in runtime server | No. |
| `indexOf(repoRoot) === 0` containment remains in runtime server | No. |
| N+4.4B blocker fixed | Yes. |

## Live Endpoint Validation

Dashboard server was started in the isolated audit worktree on a local audit port. All calls were made without GUI clicking or browser auto-launch.

| Case | Expected | Result |
| --- | --- | --- |
| Valid repo-local HTML | Accepted | HTTP 200, `ok: true`, repo-relative preview path returned. |
| Sibling-prefix outside path: `C:\w\n4_4d_preview_path_containment_real_audit_2_evil\fake.html` | Rejected | HTTP 400, `ok: false`, `REJECTED: path not repo-local`. |
| Normal outside path: `C:\Users\ai_sandbox\Documents\outside_preview_n44d.html` | Rejected | HTTP 400, `ok: false`, `REJECTED: path not repo-local`. |
| Traversal path | Rejected | HTTP 400, `ok: false`, `REJECTED: path not repo-local`. |
| Repo-local secret/env-style path | Rejected | HTTP 400, `ok: false`, `REJECTED: path not repo-local`. |
| Repo-local non-HTML file | Rejected | HTTP 400, `ok: false`, `REJECTED: only .html or .htm previews allowed`. |
| Missing repo-local HTML | Not served | HTTP 404, `ok: false`, `preview not found`. |

Temporary endpoint fixtures were removed after validation and were not committed.

## Static Validation

| Check | Result |
| --- | --- |
| `git diff --check` | Pass |
| `git diff --cached --check` during merge rehearsal | Pass |
| `git show --check --stat HEAD` | Pass |
| `node --check 01_projects/dashboard_mvp/server.js` | Pass |
| `node --check 01_projects/dashboard_mvp/public/app.js` | Pass |
| Python AST parse for changed/stacked Python files | Pass (`AST_OK 5`) |
| Server `startsWith(repoRoot)` / `indexOf(repoRoot) === 0` scan | Pass, none in runtime server. |
| Server `shell:true` scan | Pass, none in relevant runtime paths. |

## Tests And Regression

| Check | Result |
| --- | --- |
| `python -m unittest 01_projects.runtime_mvp.tests.test_n4_4d_preview_path_containment_fix -v` | Pass, 18/18 |
| `python -m unittest 01_projects.runtime_mvp.tests.test_n4_4c_desktop_operator_recipe_runner_preview_polish -v` | Pass, 16/16 |
| `python -m unittest 01_projects.runtime_mvp.tests.test_n4_4b_desktop_operator_dashboard_action_center -v` | Pass, 17/17 |
| `python -m unittest 01_projects.runtime_mvp.tests.test_n4_4a_desktop_operator_control_plane -v` | Pass, 20/20 |
| `python -m unittest 01_projects.runtime_mvp.tests.test_n4_3a_supervised_content_studio_demo -v` | Pass, 15/15 |
| `python -m unittest 01_projects.runtime_mvp.tests.test_n4_2a_local_memory_intake -v` | Pass, 26/26 |
| `python -m unittest 01_projects.runtime_mvp.tests.test_n4_1_runtime_reliability -v` | Pass, 19/19 |
| `python 03_scripts/local_memory_compression_bridge.py --json` | Pass; local-only JSON, no external API used. |
| `python 03_scripts/repo_skill_plugin_intake.py --validate-config` | Pass; 22 entries, blocked runtime flags false. |
| `python 03_scripts/ghoti_readiness_check.py --status` | Pass; supervised MVP score 100, 9/9 categories. |
| `python 03_scripts/supervised_content_mvp_runner.py --validate-latest` | Pass; proof packet valid, production public release false. |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File 03_scripts/check_runtime_mvp.ps1` | Pass; summary says runtime MVP checks passed. |
| `pwsh -NoProfile -ExecutionPolicy Bypass -File 03_scripts/check_dashboard_mvp.ps1` | Pass; summary says dashboard MVP checks passed. |

Combined unit regression count for N+4.4D through N+4.1 was 131 passing tests.

## Safety Scan

| Safety item | Result |
| --- | --- |
| No secrets/API keys committed | Pass; broad scan only found deny-list words, tests, and report prose. |
| No live Gemini prompts | Pass. |
| No user goal sent to Gemini | Pass; Gemini remains status/fallback-oriented. |
| No arbitrary shell execution from model output | Pass. |
| No arbitrary click/type exposure | Pass. |
| No live account/API actions | Pass. |
| No posting/uploading | Pass. |
| No money/trading actions | Pass. |
| No external repo clone/install/run | Pass; forbidden action names appear only in deny lists/planning guardrails. |
| No UI-TARS/The Agency/Weavy/Manychat/Vouch/AEX/AirLLM/OpenFang/MoneyPrinter runtime wiring | Pass. |
| Approval gates intact | Pass. |
| Raw approval token not stored/returned | Pass by inherited N+4.4B/N+4.4C tests and scans. |
| Default mode dry-run/local-only preserved | Pass. |
| Preview endpoint arbitrary file read | Blocked by repo-local containment, HTML extension checks, secret/env checks, and existence checks. |

## Screenshot And Terminal Behavior

| Item | Result |
| --- | --- |
| Blocking GUI popup | Not observed. |
| Weird `runtime-desktop-clipboard-checkruntime-desktop-clipboard-check` terminal command | Not reproduced as a terminal command. |
| Clipboard/handoff guard negative tests | Observed expected safe checker behavior: junk payloads were blocked before paste and reported truthfully. |
| Blank `node.exe` issue | Not observed as a blocker; dashboard server checks completed and exited. |
| Lingering validation process tied to audit worktree | None found beyond the active audit shell while checking. |

## Direct Answers

| Question | Answer |
| --- | --- |
| Is the N+4.4B blocker fixed? | Yes. |
| Does sibling-prefix outside path get rejected? | Yes, HTTP 400 / `ok: false`. |
| Does valid repo-local preview still work? | Yes, HTTP 200 / `ok: true`. |
| Is there any remaining `startsWith(repoRoot)` containment in the runtime server? | No. |
| Did any external tool become runtime-wired? | No. |
| Can Gemini touch the computer yet? | No. |
| Are approval gates intact? | Yes. |
| Is this full Ghoti production 100%? | No. This is a clean audited local/security milestone, not full production autonomy. |

## Final Verdict

**CLEAN PASS**

Recommended next action: merge N+4.4D after preserving the security proof in this audit report, then run a final main audit for the merged preview containment fix.
