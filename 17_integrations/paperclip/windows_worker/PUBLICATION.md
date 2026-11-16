# Publication and review boundary

This directory contains actual upstream source/test diffs, upstream MIT license,
hashes and reproducible build/apply instructions, not a vendor installation or
foreign Git history. The exact upstream base is publicly resolvable at
https://github.com/paperclipai/paperclip/commit/d0bdbe11a9624435b6dca3968389bd59c6a559a2.
The public v0.3.1 tag is a different pin; do not substitute it.

The publisher applied all eight patches in order in a fresh disposable clone.
Every intermediate tree matched and the final tree was
89e3964b370d6cd1474be03c04a3c3328521947f, exactly the approved worker/declaration
head e04e2ae1a0d47cdedf5380b5a0d94f280a82d5d1. PUBLICATION_CHECK.json records
this packaging proof. It is not a rerun of Windows lifecycle tests or a live run.

The last four repair patches carry the retained approved worker/declaration
scope through f2b01139/e04e2ae. The four earlier fork prerequisites have NOT
received independent implementation approval in this publication run. Keep this
PR draft; successful tree reproduction does not approve them or authorize adoption.
The packager's manifests/documents accurately record that it did not itself
apply/build/test/install; the later publisher's apply-only proof is separate.

No company data, user credentials, live memory, node_modules, virtualenvs, binary
bundles, logs, installed service or runtime cache is included. Hermes alone owns
reviewed installation/adoption and the running service. No new lifecycle repair,
configuration operation or service restart is performed by this publication.
