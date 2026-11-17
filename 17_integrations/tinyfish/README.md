# Disabled provider adapter — source review snapshot

Exact first-party diff from accepted private lineage6541093 to candidate6f6177d,
with original blob/tree/digest provenance. No private Git ancestry, built payload,
account data, keys or runtime receipts are imported. The source remains disabled.

This is a DRAFT review artifact, not a portable installer or host-adoption grant.
The full existing runtime and accepted original base are required to apply the
patch; public main's layout must not be treated as the private installed release.
No installation, provider call, credential setup or live approval is performed
by publication. Owner46 adapter/14 UI tests use synthetic transport and are not
independent live-provider evidence.

Independent review must verify durable run identity, uncertain submission and
retry reconciliation, remote cancellation versus local acknowledgment, budgets,
untrusted content, credential isolation and the external metered approval grant.
A prompt saying read-only is not a technical mutation restriction. Current API
features do not provide enforced browser read-only navigation.

Historical source/package/UI approvals are separate; none authorizes this adapter.
Keep all credentialed activation and installed release changes with the explicitly
authorized host owner after final acceptance. See SOURCE_MANIFEST.json for exact
scope and limitations. No patch is automatically applied by this directory.

## Independent verdict: CHANGES_REQUESTED

Exact6f6177d independently passes the existing46 adapter and14 UI synthetic tests.
One additional independently executed regression is RED,0 setup errors:100
unrelated local jobs hide an unresolved submission from the recent100 window,
allowing a second mocked metered start despite duplicate/concurrency/daily caps.
Complete provider-specific authority cannot depend on UI presentation pagination.

Static findings separately require trusted external-metered approval binding,
complete persistence redaction and narrow validated provider-result routing.
Those are source findings, not three additional dynamically executed failures.
No activation is approved, and no provider call or actual secret was used.

The portable independent regression preserves both original behavioral assertions.
Supply the exact reviewed full source snapshot with its existing runtime imports
and a fresh disjoint owned evidence directory. It denies network and subprocess
creation and uses synthetic transport with the real RunStore. Expected RED on
this rejected candidate is retained, not rewritten to fit its current behavior.

```text
python -I -B independent_tests/uncertain_submission_regression.py <reviewed-source-snapshot> <fresh-owned-evidence-dir>
```

The portable form changes only fixture path binding and empty PATH. Its body and
assertions are reviewed against the retained executed original; no second run is
claimed from collecting the file. The actual source patch remains byte-exact.
