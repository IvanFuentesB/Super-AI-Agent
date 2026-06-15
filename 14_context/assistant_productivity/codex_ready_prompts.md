# Codex Ready Prompts

Use one prompt per task. Keep the relevant branch, commit, worktree, and checks
small and explicit.

## Merge gate

> Audit `<target branch>` against current `origin/main` in an isolated
> repo-contained worktree. Inspect attribution, diff scope, secrets, private
> paths, and safety boundaries. Run the target tests and public audit. Merge and
> push main only when every required gate passes.

## Rust validator audit

> Review `<Rust crate>` as a deterministic fail-closed validator. Verify it has
> no network or write surface, checks malformed input, unsafe capabilities,
> private paths, secret-like values, and emits stable fingerprints. Run its
> tests with a temporary Cargo target directory.

## MCP audit

> Audit the repo-local MCP templates and strategy files. Require disabled
> defaults, environment-variable names only, no credential values, read-only
> first capabilities, and explicit blocked account/browser/send actions.

## Repo-intake audit

> Apply inspect-first repo intake to `<source>`. Record canonical URL, revision,
> license, package/install scripts, hooks, binaries, auth/network surfaces,
> reusable patterns, risk classification, blocked actions, and next safe step.
> Do not execute the repo.

## Public repo safety audit

> Review the proposed diff for secrets, local absolute paths, private memory,
> account identifiers, generated residue, third-party contents, and misleading
> capability claims. Run `public_repo_security_audit.py` and report blockers
> before any push.

## Token-saving audit

> Identify repeated context, broad file loads, duplicated instructions,
> unnecessary agents/tools, and prompts that can become reusable skills or
> compact handoffs. Preserve high-risk verification and produce the smallest
> reliable next context packet.

## Parallel branch audit

> Map independent lanes by branch, base, write surface, and validation. Run
> read-only checks in parallel, block overlapping file ownership, then report
> clean merge order without changing main.

## Continue a Claude Code branch

> Inspect `<Claude branch/worktree>` before editing. Verify remote status,
> uncommitted work, base, intended milestone, tests already run, and incomplete
> pieces. Preserve safe work, fix only verified gaps, and do not restart the
> milestone or overwrite unpublished changes.

## No-overlap implementation

> Implement `<task>` on a clean worktree. First list files owned by active
> branches. Use additive files or isolated modules, avoid overlapping surfaces,
> and leave a precise integration note for the other lane.

## GitHub PR review

> Review PR `<number>` for scope, unresolved comments, attribution, test claims,
> safety boundaries, and mergeability. Reproduce the important checks locally;
> do not rely only on the PR description.

## Finish incomplete Claude branch protocol

> Fetch remote truth, inspect the unfinished worktree read-only, and classify
> each change as complete, safe-but-incomplete, generated residue, or blocked.
> If the branch is unpublished, create a separate Codex branch and implement
> non-overlapping work only. Report exact integration order.
