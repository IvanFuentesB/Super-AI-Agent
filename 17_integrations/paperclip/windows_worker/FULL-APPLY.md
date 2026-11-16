# Nine-patch pinned source recipe

Original public base: d0bdbe11a9624435b6dca3968389bd59c6a559a2, tree4f8f24f139dfb1d8aee62020a25e9935c3a0b8a0.
Do not substitute the distinct v0.3.1 tag. Existing eight patches reproduce e04; appended patch corrects C-P3-1.
Original worker/declaration and historical failed evidence remain unchanged.

Inspect all patch hashes and use an already provisioned disposable checkout. No command below installs, starts a service or authorizes a live login.

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

Expected final source tree: df78771e6c9631a8d7edf6e9d0992570a6f3b432 (original owner b32d26e53cb77b7d28f7f95bd95bfe35117eaa5f).
The accepted narrow-save patch then produces combined tree 47f0df456dace03cb9918435f5f4424969b0e3a9.
Original e04 tree89e3964b370d6cd1474be03c04a3c3328521947f and narrow-only tree239405e35499f698020db4e575ef6b74ebcf2457 remain distinct historical identities.

Raw patches reproduce tracked trees, not original authors, dates or commit IDs. Independent correction tests and combined checks/build are described in README; host installation is separate.
