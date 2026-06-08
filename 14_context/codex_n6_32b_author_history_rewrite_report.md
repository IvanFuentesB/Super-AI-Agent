# N+6.32B Targeted Author History Rewrite Report

## Verdict

**PASS**

The explicitly approved targeted author/committer cleanup completed successfully. The public default branch and affected feature refs no longer expose the forbidden author/committer identity. No broad attribution-message cleanup was performed, no unrelated history was rewritten, and no feature branch was merged.

## Scope And Backup

- Repository visibility: `PUBLIC`
- Default branch: `main`
- Old main: `ca90fbdbffff87a6375c0d7dfb8e64fcee9f7432`
- New main: `1c568a84dc2e3a87b51a5e28a5cb79662508f47c`
- Local backup bundle: created and verified
- Backup refs pushed: none
- Push mode: explicit `--force-with-lease`
- Plain force used: no
- Broad attribution-message rewrite: no

## Targeted Main Rewrite

Only the forbidden identity commit and descendants whose parent IDs necessarily changed were recreated:

| Purpose | Old commit | Clean commit |
| --- | --- | --- |
| Rust policy integration-test fix | `3a10177cc3595c9ae435fb807c2c0bbd0d214f89` | `d448a63b0ce008b6c9b3f946ea182fc91ceb363a` |
| Rust policy merge commit | `af43fbc1c3374b44b3ef96380528f505e1969570` | `04606f21d100108d135f973a7207da7ec878882f` |
| N+6.28B merge-gate report | `ca90fbdbffff87a6375c0d7dfb8e64fcee9f7432` | `1c568a84dc2e3a87b51a5e28a5cb79662508f47c` |

The old and clean main trees are identical. Commit messages were preserved. The clean commits use:

`IvanFuentesB <IvanFuentesB@users.noreply.github.com>`

as both author and committer.

## Sanitized Feature Refs

Each affected feature patch was verified byte-for-byte identical before its remote ref moved.

| Branch | Old head | Clean head | Result |
| --- | --- | --- | --- |
| `feat/ghoti-agent-claude-n6-28a-rust-policy-checker` | `3a10177cc3595c9ae435fb807c2c0bbd0d214f89` | `d448a63b0ce008b6c9b3f946ea182fc91ceb363a` | Direct bad ref replaced |
| `feat/ghoti-agent-claude-n6-29a-computer-use-repo-backed-adapter` | `27a0a1076e958141f6f4fc2a179d11ad1e96ea43` | `d65c0abff6445d10f9d6586fd209ed1eb82c37b8` | Rebased on clean main; three identities corrected |
| `feat/ghoti-agent-claude-n6-30a-plug-and-play-swarm-memory-intake` | `ea90bbc778b7ff847c3dcff34ce47aca35fa3e93` | `260483477729f3f8ec30d4c20966ab0cf40cb41b` | Rebased on clean main; three identities corrected |
| `feat/ghoti-agent-claude-n6-31a-rust-runtime-base` | `f6b27218d4a0064be5e5d65460132f09b79ce979` | `e305a25687b6f8e3e27cb32157ae2b450e5092b5` | Rebased on clean main; two identities corrected |
| `feat/ghoti-agent-claude-n6-32a-no-ai-attribution-guard` | `3ee2d92cf7178d6bd85c60538eed4e8e0300d6e8` | `595887e04fffc0823d319f36b550c1af2c3899a2` | Rebased on clean main |

The five feature-ref moves were performed as one atomic, lease-protected push.

## Verification

- No remote branch contains old commit `3a10177...`.
- No tag contains old commit `3a10177...`.
- `origin/main` contains no forbidden author or committer identity.
- The four pending feature branches contain no forbidden author or committer identity.
- The four pending feature branches descend from cleaned `origin/main`.
- The four pending feature branches do not contain the old bad commit.
- Exclusive pending-branch commit messages contain no prohibited attribution trailers.
- Latest five main commits contain no prohibited attribution trailers.
- GitHub contributors API reports only `IvanFuentesB`.
- `git fsck --no-reflogs --unreachable` reports the replaced commits as locally unreachable, as expected after the rewrite.
- Public repository security audit: 150 checks, 0 blockers, 8 warnings requiring human review.
- Product launcher status: passed; local-only safety truth unchanged.

Historical message-only attribution text remains where inherited because the human explicitly prohibited the broader 106-commit message cleanup.

## Safety Result

- No secrets, tokens, cookies, or private files were introduced.
- No backup branch or backup ref was pushed.
- No pending feature was merged.
- No unrelated commit tree or feature patch changed.
- No plain force push was used.
- No current remote ref risks reintroducing the old bad commit.

## Next Merge Queue

1. Audit and merge N+6.32A no-AI-attribution guard first, so future merge gates enforce the corrected policy.
2. Audit and merge N+6.29B computer-use adapter.
3. Audit and merge N+6.30B plug-and-play swarm/memory intake.
4. Audit and merge N+6.31B Rust runtime base.

Each merge gate must start from cleaned `origin/main` and re-check author, committer, and latest commit messages before pushing.
