# Claude N+4.4D — Preview Path Containment Security Fix

## Executive Verdict

**IMPLEMENTED_AND_PUSHED**

Fixes the Codex N+4.4B BLOCKED_VALIDATION blocker. The vulnerable `normalized.startsWith(repoRoot)` check accepted sibling-prefix paths like `C:\Users\ai_sandbox\Documents\AI_Managed_Only_evil\fake.html` as inside-repo. Replaced with a real `path.relative()`-based directory-containment helper `isPathInsideRepo()` used by both the helper `isRepoLocalPath()` and the `/api/desktop-operator/preview` endpoint.

This branch **supersedes N+4.4B and N+4.4C** for merge purposes.

## Branches And Commits

| Field | Value |
| --- | --- |
| Branch | `feat/ghoti-agent-claude-n4-4d-preview-path-containment-fix` |
| Worktree | `C:\Users\ai_sandbox\Documents\AI_Managed_Only_worktrees\claude_n4_4d_preview_path_containment_fix` |
| Base main commit | `e16101992bf95447a6cb697e12c8c843c3c519a8` |
| Stacked on N+4.3A | YES — `1fb7804ce7f2e71c5a34f6d810235fe770b5e2de` in HEAD history |
| Stacked on N+4.4A | YES — `1521269533fcd457403ed730a884341f1e44aee6` in HEAD history |
| Stacked on N+4.4B | YES — `ad00a6b24e3141dc8abae1c5964690fbacf98007` in HEAD history |
| Stacked on N+4.4C | YES — `d64024bdced345ab4ea67da2c89af41acdb39aec` in HEAD history |
| N+4.4B audit blocker | `audit/...n4-4b...real-audit` @ `bb0ca46f7d525903c1b6e8d818d0cb77ec77214b` (BLOCKED_VALIDATION) |

## Blocker Reproduced

**YES.** Direct Node reproduction shows the vulnerability:

```
candidate:  C:\Users\ai_sandbox\Documents\AI_Managed_Only_worktrees\claude_n4_4d_preview_path_containment_fix_evil\fake.html
normalized: C:\Users\ai_sandbox\Documents\AI_Managed_Only_worktrees\claude_n4_4d_preview_path_containment_fix_evil\fake.html
VULNERABLE normalized.startsWith(repoRoot): true
SAFE path.relative() based check: rel="..\\claude_n4_4d_preview_path_containment_fix_evil\\fake.html", insideRepo=false
```

The sibling-prefix attack succeeds against `startsWith()` because there is no directory-separator boundary check — the prefix continues into the sibling segment.

## Root Cause

`server.js` previously contained two copies of the vulnerable check:

1. `function isRepoLocalPath(candidate)` returned `normalized.startsWith(repoRoot)` at the tail.
2. The `/api/desktop-operator/preview` endpoint repeated the same `normalized.startsWith(repoRoot)` check as a "defence-in-depth" second filter.

Both treat the repo root as a string prefix without enforcing that the next character is a directory separator (or the path is exactly the root). Any path whose absolute form starts with the repo-root string passes.

## Exact Fix

Added a new helper `isPathInsideRepo(candidate)` near the top of the Desktop Operator block in `server.js`:

```js
function isPathInsideRepo(candidate) {
  if (typeof candidate !== "string" || candidate.length === 0) return false;
  const resolvedRoot = path.resolve(repoRoot);
  const absolute = path.isAbsolute(candidate) ? candidate : path.join(resolvedRoot, candidate);
  let resolvedCandidate;
  try { resolvedCandidate = path.resolve(absolute); } catch (err) { return false; }
  const relative = path.relative(resolvedRoot, resolvedCandidate);
  if (relative === "") return false;             // candidate IS the repo root -> reject
  if (relative.startsWith("..")) return false;   // outside / sibling-prefix -> reject
  if (path.isAbsolute(relative)) return false;   // different drive on Windows -> reject
  return true;
}
```

- `isRepoLocalPath()` now delegates final containment to `isPathInsideRepo()`.
- The `/api/desktop-operator/preview` endpoint replaced its inline `normalized.startsWith(repoRoot)` block with a call to `isPathInsideRepo()`.

All other rejections (`..` in path string, secret/env patterns, non-`.html`/`.htm` extension, missing file) remain in place.

## Files Changed

| File | Change |
| --- | --- |
| `01_projects/dashboard_mvp/server.js` | + `isPathInsideRepo()` helper; replaced two vulnerable `startsWith(repoRoot)` containment checks |
| `01_projects/runtime_mvp/tests/test_n4_4d_preview_path_containment_fix.py` | NEW — 18 tests (static + Node-helper + live HTTP) |
| `14_context/claude_n4_4d_preview_path_containment_fix.md` | NEW — this report |

## Sibling-Prefix Outside Path Test Result

| Path | Expected | Result |
| --- | --- | --- |
| `<repoRoot>_evil\fake.html` (sibling-prefix attack) | REJECTED | **HTTP 400** — `{"ok":false,"error":"REJECTED: path not repo-local"}` |
| `C:\Windows\System32\drivers\etc\hosts` (normal outside) | REJECTED | **HTTP 400** |
| `..\..\evil.html` (traversal) | REJECTED | **HTTP 400** |
| `.env.html` (secret pattern) | REJECTED | **HTTP 400** |
| `01_projects/dashboard_mvp/server.js` (non-html) | REJECTED | **HTTP 400** |
| `14_context/content_studio/runs/.../10_preview.html` (valid repo-local html) | ACCEPTED | **HTTP 200** — `{"ok":true,"previewPath":"14_context/...","bytes":9893}` |

## Valid Repo-Local Preview Result

Valid path `14_context/content_studio/runs/20260512T172447Z_ai_tools_for_students_and_creato/10_preview.html` returns HTTP 200 with `ok=true`, normalized preview path, and byte count. The preview HTML is the showcase artifact from N+4.3A.

## Tests Result

| Suite | Result |
| --- | --- |
| **N+4.4D** | **PASS — 18/18** |
| **N+4.4C regression** | **PASS — 16/16** |
| **N+4.4B regression** | **PASS — 17/17** |
| **N+4.4A regression** | **PASS — 20/20** |
| **N+4.3A regression** | **PASS — 15/15** |
| **N+4.2A regression** | **PASS — 26/26** |
| **N+4.1 regression** | **PASS — 19/19** |
| **Total** | **131/131** |

The N+4.4D test suite explicitly covers:
- Static: `isPathInsideRepo` defined, uses `path.relative()` + `path.resolve()`, `isRepoLocalPath` delegates to it, preview endpoint uses it, no `startsWith(repoRoot)` containment anywhere, `shell:true` absent, `.html`/`.htm` extension required.
- Node-helper: 6 cases — sibling-prefix, normal outside, traversal, repo-root-itself, valid relative inside, valid absolute inside.
- Live HTTP: 5 cases against the running dashboard server.

## check_runtime_mvp.ps1 Result

PASS — "Summary: runtime MVP checks passed." (exit 0)

## check_dashboard_mvp.ps1 Result

See validation logs. The new preview-containment fix is tested directly via the N+4.4D live HTTP suite which spawns its own server.

## Validation Table

| Validation | Result |
| --- | --- |
| `git diff --check` | PASS — exit 0 |
| `node --check` server.js + app.js | PASS |
| Python AST (test + control plane) | PASS |
| Live HTTP preview test (6 cases) | PASS |
| `local_memory_compression_bridge.py --json` | PASS |
| `repo_skill_plugin_intake.py --validate-config` | PASS — 22 entries, all blocked flags False |
| `ghoti_readiness_check.py --status` | PASS — categories_passing: 9/9 |
| `supervised_content_mvp_runner.py --validate-latest` | PASS — score 100 |
| `check_runtime_mvp.ps1` | PASS |
| 7-suite regression | PASS — 131/131 |

## Safety Table

| Check | Result |
| --- | --- |
| Sibling-prefix outside path | REJECTED (HTTP 400) |
| Normal outside path | REJECTED (HTTP 400) |
| Traversal path | REJECTED (HTTP 400) |
| Repo-root-itself | REJECTED |
| Non-`.html`/`.htm` | REJECTED (HTTP 400) |
| Secret/env pattern | REJECTED (HTTP 400) |
| Non-existent preview file | REJECTED (HTTP 404) |
| Different Windows drive | REJECTED (`path.isAbsolute(relative)` true) |
| Approval gate (N+4.4A/B/C) | unchanged — preserved |
| No `shell: true` | confirmed (test) |
| No external repo wiring | preserved |
| No live Gemini prompt | preserved |
| No arbitrary click/type | preserved |
| No live account/API/posting/money | preserved |

## Direct Answers

| Question | Answer |
| --- | --- |
| Was the blocker reproduced? | **YES** — sibling-prefix path `..._fix_evil\fake.html` accepted as inside-repo by old `startsWith(repoRoot)` |
| Is the blocker fixed? | **YES** — replaced with `path.relative()` containment everywhere; reproduction now rejected at HTTP 400 |
| Is the fix applied to ALL containment checks? | **YES** — `isRepoLocalPath()` now delegates to `isPathInsideRepo()`; preview endpoint uses it directly; no `startsWith(repoRoot)` containment remains |
| Are approval gates intact? | **YES** |
| Is this full Ghoti production 100%? | NO — security fix only |

## Final Verdict

**IMPLEMENTED_AND_PUSHED**

The N+4.4B `/api/desktop-operator/preview` sibling-prefix path-containment vulnerability is fixed. 131 tests across 7 stacked regression suites all green. Live HTTP test confirms the attack is rejected with HTTP 400. Valid repo-local previews continue to work.

## Exact Next Recommended Action

Run **Codex N+4.4D real audit** on the pushed branch. This branch supersedes N+4.4B and N+4.4C for merge purposes.