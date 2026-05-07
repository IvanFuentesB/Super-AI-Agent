# N+3.72C Remote Main Truth Check

**Generated:** 2026-05-07
**Agent:** Claude Sonnet 4.6
**Mission:** Diagnose apparent discrepancy between Claude N+3.72B push report and
Codex N+3.73B/N+3.73C seeing stale origin/main.

---

## Verdict

**REMOTE_MAIN_ALREADY_CORRECT**

Remote main was already at the correct post-N+3.72B commit when this diagnostic ran.
No push was needed. Codex had stale (uncached) refs.

---

## Remote State at Diagnostic Time

| Check | Result |
|---|---|
| `git ls-remote origin refs/heads/main` | `cdedf6087ed9bb69b33981436840dbd1c2598b03` |
| `git rev-parse origin/main` (after fetch) | `cdedf6087ed9bb69b33981436840dbd1c2598b03` |
| Expected from N+3.72B report | `cdedf60` |
| Match | **YES** |

---

## N+3.72B Commit Chain — All Present

| Commit | Type | Description |
|---|---|---|
| `cdedf6087ed9bb69b33981436840dbd1c2598b03` | commit | `docs(ghoti): add N+3.72B final main merge gate report` |
| `3a6e7bb790f72b816325c4a4c7e8371b6638b5ba` | commit | `fix(ghoti): remove trailing blank lines at EOF in integration delta` |
| `784aad8` | commit | `fix(ghoti): normalize CRLF to LF in integration delta files` |
| `a09a3de2484b85a57f97255f38f45aacfc114fba` | commit | `merge(ghoti): land supervised content MVP 100 slice` |
| `677d9f03cd7d52157d4babfb6d3a96d64946b867` | commit | `feat(ghoti): implement N+3.65 supervised content MVP 100 slice` |

All verified via `git cat-file -t <hash>` — all return `commit`.

---

## N+3.65 on Main

`git merge-base --is-ancestor 677d9f0 origin/main` → exit 0 → **YES**

---

## origin/main Log (top 8)

```
cdedf60 docs(ghoti): add N+3.72B final main merge gate report
3a6e7bb fix(ghoti): remove trailing blank lines at EOF in integration delta
784aad8 fix(ghoti): normalize CRLF to LF in integration delta files
a09a3de merge(ghoti): land supervised content MVP 100 slice
99c26b5 docs(ghoti): add N+3.70 merge report for N+3.65 supervised content MVP 100 land
00809e8 merge(ghoti): land N+3.65 supervised content MVP 100 slice
677d9f0 feat(ghoti): implement N+3.65 supervised content MVP 100 slice
30009cd chore(ghoti): refresh N+3.63A dashboard card and catalog timestamps
```

---

## Diagnosis of Codex Discrepancy

Codex N+3.73B/N+3.73C reported `origin/main` as `63ba393` — the pre-merge value.

Likely causes (in order of probability):

1. **Stale git refs in Codex sandbox.** Codex ran `git rev-parse origin/main` without
   first running `git fetch origin`. In sandboxed/ephemeral environments, remote refs
   are cached at session start and do not auto-update. This is the most common cause.

2. **Codex used a different local clone.** If Codex has its own clone or working
   directory, that clone's `origin/main` ref would not have been updated by Claude's
   push to the GitHub remote. The GitHub remote received the push, but Codex's local
   `origin/main` tracking ref was never refreshed.

3. **Network/fetch lag.** Rare, but GitHub can briefly show stale pack refs to a
   different API region. Resolved within seconds.

**Resolution:** Codex must run `git fetch origin --prune` before reading
`origin/main`. The remote is correct.

---

## No Push Performed

This diagnostic did not push to main. Main was already correct.
This report is committed to `diag/ghoti-agent-n3-72c-remote-main-truth-check` only.

---

## Next Action

**Rerun Codex N+3.73C final main audit** after running `git fetch origin --prune`
inside the Codex environment. Remote main is at `cdedf60` with N+3.65 landed,
whitespace clean, and supervised MVP slice score 100.
