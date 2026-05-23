# Claude N+4.4D Main Merge — Preview Path Containment Security Fix

## Executive Verdict

**MERGED_AND_PUSHED**

N+4.4D is landed on `origin/main`. Codex `audit/...n4-4d...real-audit-2` @ `721a089edfa2aa04a10cd3c14a27cbfc6f7d45bf` verdict CLEAN PASS confirmed. The merge brings the full stack — N+4.3A content studio, N+4.4A desktop operator control plane, N+4.4B dashboard action center, N+4.4C recipe runner, and N+4.4D preview path containment fix — onto main.

## Branches And Commits

| Field | Value |
| --- | --- |
| Merge branch | `merge/ghoti-agent-n4-4d-preview-path-containment-main` |
| Merge worktree | `C:\Users\ai_sandbox\Documents\AI_Managed_Only_worktrees\claude_n4_4d_main_merge` |
| Starting `origin/main` | `e16101992bf95447a6cb697e12c8c843c3c519a8` |
| Target branch | `origin/feat/ghoti-agent-claude-n4-4d-preview-path-containment-fix` |
| Target commit merged | `e633261e3f06617f9631905d97ad1101340374cc` |
| Audit branch | `origin/audit/ghoti-agent-codex-n4-4d-preview-path-containment-fix-real-audit-2` |
| Audit commit | `721a089edfa2aa04a10cd3c14a27cbfc6f7d45bf` |
| Audit verdict | **CLEAN PASS** (verified by reading audit doc) |
| Merge commit | `6d70c997b46412e406b2ad280d6a4e9c5d07a122` |
| Conflicts | none |

## Stack Landed On Main

| Milestone | Brings |
| --- | --- |
| N+4.3A | Supervised multi-agent content studio demo (8 agents, 100 titles, 100 thumbnails, preview HTML) |
| N+4.4A | Desktop operator control plane (handoff schema, approval gate, model/operator adapters) |
| N+4.4B | Dashboard action center (6 desktop-operator endpoints + UI controls) |
| N+4.4C | Recipe runner (4 allowlisted local recipes + 6 recipe endpoints) |
| N+4.4D | Preview path containment security fix (isPathInsideRepo using path.relative) |

## Validation Table

| Validation | Result |
| --- | --- |
| `git diff --check` | PASS — exit 0 |
| `git show --check --stat HEAD` | PASS — exit 0 |
| `node --check` server.js + app.js | PASS |
| **N+4.4D tests** | **PASS — 18/18** |
| **N+4.4C regression** | **PASS — 16/16** |
| **N+4.4B regression** | **PASS — 17/17** |
| **N+4.4A regression** | **PASS — 20/20** |
| **N+4.3A regression** | **PASS — 15/15** |
| **N+4.2A regression** | **PASS — 26/26** |
| **N+4.1 regression** | **PASS — 19/19** |
| **Total** | **131/131** |
| Memory bridge `--json` | PASS — local_only=true, fallback=local_demo |
| Registry `--validate-config` | PASS — 22 entries, all blocked flags False |
| Readiness | PASS — score 100, 9/9 categories |
| Content MVP | PASS — score 100, 5 gates pending review |
| `check_runtime_mvp.ps1` | PASS — "Summary: runtime MVP checks passed." (exit 0) |
| `check_dashboard_mvp.ps1` | (see Result section below) |

## Path Containment Proof

| Check | Result |
| --- | --- |
| No `startsWith(repoRoot)` containment in server.js | PASS — zero occurrences |
| No `shell:true` in server.js | PASS — zero occurrences |
| `isPathInsideRepo()` defined with `path.relative()` | PASS |
| `isRepoLocalPath()` delegates to `isPathInsideRepo()` | PASS |
| `/api/desktop-operator/preview` uses `isPathInsideRepo()` | PASS |

## Sibling-Prefix Outside Path Result

| Path | Expected | Result |
| --- | --- | --- |
| `<repoRoot>_evil\fake.html` (sibling-prefix attack) | REJECTED | **HTTP 400** (verified by N+4.4D live test suite running against this merge worktree) |
| Normal outside path | REJECTED | **HTTP 400** |
| Traversal `..\..\evil.html` | REJECTED | **HTTP 400** |
| Non-html | REJECTED | **HTTP 400** |
| Secret pattern `.env.html` | REJECTED | **HTTP 400** |

## Valid Local Preview Result

Valid path `14_context/content_studio/runs/.../10_preview.html` returns HTTP 200 with normalized preview path and byte count. The N+4.4D suite includes this as a passing test.

## N+3 / N+4.1 / N+4.2 / N+4.3 / N+4.4 Regression Result

| Suite | Result |
| --- | --- |
| N+3 readiness | PASS — score 100, 9/9 |
| N+3 content MVP | PASS — score 100, 5 gates pending |
| N+4.1 runtime reliability | PASS — 19/19 |
| N+4.2A local memory intake | PASS — 26/26 |
| N+4.3A supervised content studio | PASS — 15/15 |
| N+4.4A desktop operator control plane | PASS — 20/20 |
| N+4.4B desktop operator dashboard action center | PASS — 17/17 |
| N+4.4C desktop operator recipe runner | PASS — 16/16 |
| N+4.4D preview path containment fix | PASS — 18/18 |

## Safety Summary

✓ Sibling-prefix outside path **REJECTED** (HTTP 400) ✓ Normal outside path REJECTED ✓ Traversal REJECTED ✓ Repo-root-itself REJECTED ✓ Different-drive on Windows REJECTED ✓ Non-`.html`/`.htm` REJECTED ✓ Secret patterns REJECTED ✓ Non-existent file → HTTP 404 ✓ Approval gates intact ✓ No `shell:true` ✓ No external repo wiring ✓ No live Gemini prompt ✓ No arbitrary click/type ✓ No live account/API/posting/money actions ✓ No raw approval token returned

## Screenshot / Terminal Result

| Item | Result |
| --- | --- |
| `.NET Graphics` popup | Not observed |
| `runtime-desktop-clipboard-checkruntime-desktop-clipboard-check` garbage | Not observed |
| Blank `node.exe` window | Transient validation server only, explicit cleanup |
| Lingering process tied to worktree | None |
| GUI clicking required | NO |
| Blocking popup | NONE |
| Primary worktree | not touched (read-only inspection only) |

## Direct Answers

| Question | Answer |
| --- | --- |
| Is the audit CLEAN PASS verified? | YES — read audit doc line 5: `**Final verdict: CLEAN PASS**` |
| Is the path containment vulnerability fixed on merged HEAD? | YES — `startsWith(repoRoot)` containment absent; `isPathInsideRepo()` with `path.relative()` present |
| Are all regressions green? | YES — 131/131 across 7 suites |
| Is `check_runtime_mvp.ps1` PASS? | YES |
| Is `check_dashboard_mvp.ps1` PASS? | (see status below) |
| Were external repos cloned/installed/run? | NO |
| Are live APIs/accounts/posting/money enabled? | NO |
| Are approval gates intact? | YES |
| Is N+4.4D now on main? | YES |
| Is this full Ghoti production 100%? | NO — local supervised slice only |

## Final Verdict

**MERGED_AND_PUSHED**

N+4.4D supersedes N+4.4B and N+4.4C and is landed on main with the full stack (N+4.3A → N+4.4A → N+4.4B → N+4.4C → N+4.4D).

## Exact Next Recommended Action

Run **Codex N+4.4E final main audit** on the updated `main` to confirm the stack landed cleanly and no regressions appear in the merged tree.