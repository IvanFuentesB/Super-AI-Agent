# Corrected Paperclip launcher: source publication only

This is first-party launcher source and two tests derived from approved source commit
`13857ef7dbcf7be9d5a93b2da5bf90bf9d3edd25`, base
`dcfa5dd97e0f03bc6dfa0fe0c695aef9c1f12330`. SOURCE_MANIFEST.json pins all three
raw source blobs and published hashes. The two tests are exact source blobs;
the launcher has ONE privacy/portability change: PAPERCLIP_WINDOWS_PYTHON derives
the same relative tool location from Path.home() instead of a private absolute
user literal. No other launcher logic changes. Original source approval does not
automatically cover this port. No historical Git objects, installed application or user state is
included. Repository first-party licensing applies; no vendor source is copied.

The retained original launcher approval and owner-confirmed installed preflight PASS
are unchanged. This publication does not rerun that review or prove live worker
execution. No service was started, renewed, stopped, installed or reconfigured.
The superseded launcher, rollback script and old archive release instructions
are deliberately excluded. Do not replace the corrected installed launcher with
an earlier packaged version.

## Host boundary and missing dependencies

This is a DRAFT source snapshot, not a portable standalone service distribution.
Apart from that one expression, the source retains its host-relative paths, exact helper hashes and
Paperclip source/declaration pin `e04e2ae1a0d47cdedf5380b5a0d94f280a82d5d1`.
Those host dependencies and settings are NOT supplied here. Missing or different
helpers, artifacts or guards must fail closed; never remove their validation to
make this snapshot execute. The two tests include installed-artifact checks;
do not mistake their presence or earlier owner counts for new independent runs.

Read the source and SOURCE_MANIFEST.json for review. There is intentionally no
automatic start/install command or web route. Hermes owns reviewed installation,
native permissions, finite lease, running-host control and company/database
preservation. Moving this source alone does not authorize host adoption.

The separate Windows worker patch recipe is in ../windows_worker/ on its own
draft branch/PR. Its four earlier prerequisite implementations remain unapproved
in this publication run. Do not substitute the public v0.3.1 tag for its pinned
upstream commit. Review and compose dependencies through their own gates.

## Excluded overlay

The delivered three-file Paperclip status overlay is not copied here: it carries
host/company-specific binding and depends on runtime modules absent from this
clean main slice. Its synthetic tests and owner freeze are separate evidence,
not approval of live running/stopped observations. Request a privacy-safe,
parameterized owner candidate before publishing that overlay.

## Rollback and adoption

No installed state changes, so no host rollback is needed. Removing this source
snapshot from a future branch must not delete or modify the installed service,
state, company records or launcher. A main merge or deployment is not authorized
by this draft publication.
