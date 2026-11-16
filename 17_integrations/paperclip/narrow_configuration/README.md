# Narrow Paperclip configuration save — owner WIP draft

This is a source patch of exactly eight owner-committed files, not a vendor
installation or upstream Git history. Source `accb52eaaabcf1e749d07aa2f0b18de55aef305d`, parent/base `e04e2ae1a0d47cdedf5380b5a0d94f280a82d5d1`.
The owner explicitly permits draft publication and is preparing a separate
corrected successor; this WIP commit is not final or review-approved.

The delta changes the existing Configuration Save UI to send edited fields,
retain unrelated stored configuration/secrets, handle argument lists and use
readback for uncertain writes. It adds tests for the existing real PATCH/GET
routes; it adds no arbitrary HTTP proxy, provider or service-control interface.
This paragraph describes intent, not product acceptance.

## Dependencies and reproduction

The required base is the exact e04e2ae Paperclip tree. It can be reproduced by
the eight-patch recipe in PR #26 from public upstream d0bdbe11. That recipe's
four earlier prerequisite implementations still require independent acceptance.
Do not substitute the different v0.3.1 tag, install dependencies here or apply
this patch to the installed service. Upstream MIT notice is retained.

In a separately authorized disposable source checkout of the exact required
base, inspect SOURCE_MANIFEST.json and verify the raw patch hash, then use:

    git apply --check --index 0001-narrow-configuration-save.patch
    git apply --index 0001-narrow-configuration-save.patch
    git write-tree

The publisher's isolated apply check reproduced the exact committed result tree
`8d7d7dd6f5abd8b138c0fe0b86f6eb328c6a9566`. This is source reproduction, not an application run.

## Executed tests and remaining failures

The existing independent route runner previously executed a test-only raw
snapshot: control 2/2 PASS, twelve candidate cases 8 PASS / 4 FAIL. Per-file raw
equivalence to this commit is recorded in SOURCE_MANIFEST.json; no different
snapshot is silently called verification of an owner's final commit.
No old suite was rerun for this publication. Three cases returned HTTP 500;
the fourth read old arguments after a simulated post-write error. Direct
secret-service import versus the fixture's mocked barrel is a hypothesis about
fixture wiring, not proof of a production defect. The owner retains the fix.

The exact proven runner, versions, source hashes and failure traces were sent
through the existing private shared-brain handoff. That packet's absolute local
paths, logs and owner data are not uploaded here. A final successor requires the
existing control plus all twelve assertions in the proven isolated environment,
independent source review and dependency acceptance before merge/adoption.

## Adoption and rollback

Keep this PR draft until the corrected candidate is independently accepted.
No company/agent records, database, service, credentials, accounts or installed
configuration were changed. Hermes owns adoption. An eventual deployment must
preserve the corrected 13857ef launcher; an obsolete archive is not a rollback.
There is no host change to roll back from this publication.
