# Narrow Paperclip configuration save â€” accepted source and combined compatibility

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

PR26 now includes the independently accepted C-P3-1 correction b32d26e53cb77b7d28f7f95bd95bfe35117eaa5f after the original e04 sequence. Its corrected tree is df78771e6c9631a8d7edf6e9d0992570a6f3b432. Applying this unchanged narrow-save patch produces combined tree 47f0df456dace03cb9918435f5f4424969b0e3a9.

Original patch base e04 and original narrow-only result239405e35499f698020db4e575ef6b74ebcf2457 remain provenance, not the new combined build identity. All eight original source postimages and raw patch SHA remain unchanged. Verify original e04 context, corrected recipe preimage and combined result separately.

The combined source passed the full service/declaration build and independent affected cancellation/control/routes/form checks, whose candidate-bound receipt hash is in SOURCE_MANIFEST.json. Initial offline pnpm manager provisioning failure is retained; only task-owned build config was corrected, with no dependency install or global setting change. Synthetic tests/build are not a live DB/save or host-install approval.

## Host adoption and rollback

Hermes owns any reviewed bundle build, installed service and board session.
Record built UI byte hashes separately from source identity. Preserve the
corrected original 13857ef launcher; an obsolete archive is not a rollback.
An authorized future UI rollback uses the previous e04 UI build, with no DB
migration or server change. There is no host change from this publication.

No live configuration save, credentials, account action, company/agent record,
database, provider, installation, restart or global setting changed. Exact
private test-runner paths/logs remain in the existing owner handoff, not here.

## Reviewed source follow-up

See REDACTED_REFUSAL_FOLLOWUP.md and its manifest for the separately reviewed
e8ad1fd definite pre-send refusal correction. The original patch and historical
approvals above remain unchanged. Distribution and launcher adoption are separate.
