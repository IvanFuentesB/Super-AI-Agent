# Narrow Paperclip configuration save — accepted source, dependency blocked

Source `d2d7647eca88575870e079e359948520ce50290b`, parent WIP `accb52eaaabcf1e749d07aa2f0b18de55aef305d`, required base `e04e2ae1a0d47cdedf5380b5a0d94f280a82d5d1`.
This updates the SAME operation PR #31. Eight committed source/test files are
represented by one full-index patch; hashes, Git blobs and result tree are in
SOURCE_MANIFEST.json. No upstream repository history or installation is copied.
MIT notice is retained. No owner live files were staged.

## Independent acceptance

On raw frozen committed files, the existing route control passed 2/2, the same
twelve final cases passed 12/12 and relevant UI tests passed 13/13. Each suite
ran once, with zero setup/import errors, hook timeouts or assertion failures.
The existing Vitest3.2.4/Node22.16 runner used source-root relocation only and
drizzle-orm inlining; linked dependencies stayed read-only. These are independent
synthetic tests, not owner totals or production service/secret-provider evidence.

The successor adds a direct secret-service fixture mock at the module actually
imported by the unchanged real route and adds three persistence assertions. It
retains all twelve original cases and all 47 earlier expectations. PATCH/GET,
authorization, origin guard and error handler stay real. Seven other source
blobs are unchanged from WIP. Earlier 8-pass/4-fail results remain historical.

The narrow extraArgs edit preserves untouched configuration, identity/budget,
stored secret bindings and the false permission-bypass flag in the tested
sequential stale-read flow. Redacted placeholders are refused before a request.
Argument parsing round-trips quoted comma-containing values. Uncertain writes
trigger readback and an explicit unconfirmed message, not an automatic retry.

Same-field concurrency remains last-writer-wins; no CAS or atomic multi-writer
guarantee is introduced. Removing a key/changing adapter type retains the
existing whole-replacement path and its stale-copy limits. Editing env replaces
that field. This repair does not claim universal configuration synchronization.

## Dependency and source reproduction

PR #26 reproduces the exact required e04 tree from pinned public upstream
d0bdbe11. Its prerequisite 3 has a demonstrated asynchronous-browser-callback
cancellation defect (C-P3-1); prerequisites 1, 2 and 4 are scoped source-approved.
Keep THIS PR draft until the dependency is corrected and independently accepted.
Do not substitute the distinct public v0.3.1 tag or weaken a guard to apply it.

In an authorized disposable checkout of the exact base, inspect the manifest
and raw patch hash, then `git apply --check --index` and `git apply --index` the
patch. The original WIP application plus exact eleven-line fixture successor
reproduced final tree `239405e35499f698020db4e575ef6b74ebcf2457`. The publisher also checks the full final patch
against that exact base before publication. No product build/service was run.

## Host adoption and rollback

Hermes owns any reviewed bundle build, installed service and board session.
Record built UI byte hashes separately from source identity. Preserve the
corrected original 13857ef launcher; an obsolete archive is not a rollback.
An authorized future UI rollback uses the previous e04 UI build, with no DB
migration or server change. There is no host change from this publication.

No live configuration save, credentials, account action, company/agent record,
database, provider, installation, restart or global setting changed. Exact
private test-runner paths/logs remain in the existing owner handoff, not here.
