# Definite refusal before a configuration request

This is a scoped successor to the narrow-save source published in PR31. The
original patch, historical results and combined-tree approval remain unchanged.

The new full-index patch contains only the dedicated redacted-value error and
its regression test. A local refusal happens before a request is sent, so it is
a definite failure, rather than an uncertain server result. Network failures and
server errors remain uncertain and retain readback without an automatic retry.
The change does not authorize a live save or alter the permission-bypass flag.

## Source reproduction

Apply `redacted-refusal-followup.patch` after the accepted combined source tree
`47f0df456dace03cb9918435f5f4424969b0e3a9`. The result is exactly
`bdab2ce706f3e682781ad0e93da935155b937867`, carried by owner candidate
`e8ad1fd98142e6a4f53172f143381a4fa4100dd7`. The equivalent narrow-save lineage
commit is `596d24629cf7e9be0cda61fd1352343b3d643871`.

`REDACTED_REFUSAL_FOLLOWUP.json` binds the patch, original preimages and source
postimages. This publication ports reviewed first-party changes with provenance;
it does not copy private repository history, dependency installations, generated
bundles, source maps, configuration, memory or runtime state.

## Adoption boundary

Source acceptance, package verification and installed acceptance are separate.
The emitted UI/CLI package is private and needs its own artifact review. The
existing launcher still pins the prior revision; its proposed pin update must
receive a separate review against the actual installed preimage. No package or
source publication authorizes changing that launcher, starting the service,
performing a save, or exercising a worker. PR27 remains a source-only snapshot.


## Independent source acceptance

The exact new source delta passed 18 independent-execution tests: the existing
7-case helper suite and 11 additional bounded checks, with zero failures or
skips. Actual mutation/query/client helpers were exercised with synthetic fetch:
the local refusal made no request or readback; HTTP500/network failures made one
PATCH followed by three active readbacks without a retry; representative 4xx
failures remained definite. The narrow payload and unchanged secret/permission
fields were verified. Source and indexes remained unchanged.

Node22.23.4, Vitest3.2.4 and TypeScript5.9.3 were reused without installation.
These results are separate from owner tests, the earlier accepted combined build
and the emitted-bundle/distributable review. This source approval is not an
installed-service, launcher-pin or authenticated live-save approval. No private
build payload, source map, configuration or runtime database is published here.
