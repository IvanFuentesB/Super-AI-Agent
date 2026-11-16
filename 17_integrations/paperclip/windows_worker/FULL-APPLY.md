# Eight-patch public draft recipe

Status: DRAFT ONLY. The four prerequisites are NOT independently approved.
Their static content-safety clearance permits draft source-patch publication.
It grants no functional approval, merge, installation or service authorization.
The original four repair patches and their prior approval scope remain unchanged.

## Public prerequisite and exact identity

Public upstream origin: https://github.com/paperclipai/paperclip.git
Pinned starting commit: d0bdbe11a9624435b6dca3968389bd59c6a559a2
Starting tree: 4f8f24f139dfb1d8aee62020a25e9935c3a0b8a0
Main must independently verify this exact commit is available from GitHub before
claiming the draft is publicly reproducible. Packaging used retained local objects
at a shallow boundary; no upstream clone/fetch or installation was performed.

Remote v0.3.1 advertises 63c62e3ada077bac45292f3d2779bd48a8831cda.
It is a different identity; neither the tag nor package version identifies this
recipe's base. No assertion about tag ancestry is made.

Apply four prerequisites in prerequisites/series, then four original repairs in
series. full-series lists all eight relative paths. full-manifest.json pins every
patch SHA256, parent/commit, intermediate tree and status.

Prerequisite commits, in order:
1. 5c8b9e4114c657e9c7268e4cc82e63e2b5238a99 — company query cache arrays.
2. f8e301c1b8e94c0c80fba47c47c664a04148bf36 — HTTP/bootstrap log privacy.
3. fc03825cd15629b6c0c8dcab9937997e3923f4f7 — bounded CLI pairing/redaction.
4. 5e55510dbeb869bacfcd843f975632dc739519af — bounded first-engineer UI.
All four: NOT independently approved by this preparation.

Original repair interval, unchanged:
5e55510dbeb869bacfcd843f975632dc739519af..e04e2ae1a0d47cdedf5380b5a0d94f280a82d5d1.
It includes Windows process containment, cancellation, resolution/orphan recovery,
tests and e04's declaration fix. Main still performs independent safety review.

## Apply instructions — not executed here

Use a clean disposable checkout already at the exact upstream pin. Set $patchDir
to this prepared folder. No recipe command below downloads or installs anything.

    $m = Get-Content (Join-Path $patchDir 'full-manifest.json') -Raw | ConvertFrom-Json
    $current = git --no-optional-locks rev-parse HEAD
    if ($LASTEXITCODE -or $current -ne $m.base) { throw 'Wrong base commit' }
    $tree = git --no-optional-locks rev-parse 'HEAD^{tree}'
    if ($LASTEXITCODE -or $tree -ne $m.base_tree) { throw 'Wrong base tree' }
    $dirty = git --no-optional-locks status --porcelain
    if ($LASTEXITCODE -or $dirty) { throw 'Checkout must be clean' }
    foreach ($p in $m.patches) {
        $f = Join-Path $patchDir $p.file
        if ((Get-FileHash $f -Algorithm SHA256).Hash.ToLower() -ne $p.sha256) { throw 'Patch hash mismatch' }
        $currentTree = git --no-optional-locks write-tree
        if ($LASTEXITCODE -or $currentTree -ne $p.parent_tree) { throw 'Wrong preimage tree' }
        git --no-optional-locks apply --check --index $f
        if ($LASTEXITCODE) { throw 'Patch does not apply' }
        git --no-optional-locks apply --index $f
        if ($LASTEXITCODE) { throw 'Patch application failed' }
        $currentTree = git --no-optional-locks write-tree
        if ($LASTEXITCODE -or $currentTree -ne $p.tree) { throw 'Wrong intermediate tree' }
    }
    $finalTree = git --no-optional-locks write-tree
    if ($LASTEXITCODE -or $finalTree -ne $m.head_tree) { throw 'Wrong result tree' }

Expected final tree: 89e3964b370d6cd1474be03c04a3c3328521947f.
It matches source head e04e2ae1a0d47cdedf5380b5a0d94f280a82d5d1.
Raw diffs reproduce tracked trees, not commit authors, timestamps or commit IDs.
Main alone owns draft PR creation, integration decisions and eventual commits.

Build/test instructions and pinned tooling are in README.md. They remain
instructions only: no apply, product tests, builds, service or installation was
performed here. Safety review of prerequisite implementation remains a separate
gap even if the eight-patch tree reproduction succeeds.

## Content safety and scope

Full individual predecessor diffs were scanned before artifacts were written:
private absolute user paths, key-shaped credentials and authenticated URLs had
zero matches. Two account-field occurrences belong to documented synthetic test
markers; one unchanged authorization context uses a runtime challenge token.
No private values were emitted. Those classifications are recorded in
prerequisites/manifest.json. Pattern scanning is not comprehensive secret detection.
No private repository paths, account logs/receipts, bundles or vendor history are
part of these patch payloads. Source tests and privacy-handling code are included.
