# Paperclip Windows repair patch preparation

Four raw Git diffs in series order include the actual Windows Job Python helper,
TypeScript control boundary, heartbeat cancellation/orphan handling, source tests,
and e04's service declaration fix. Main must independently safety-check before porting.

Origin: https://github.com/paperclipai/paperclip.git
License: MIT; upstream license text copied from the clean source checkout into LICENSE.upstream. Its exact payload hash is pinned; checkout EOL may differ from Git blob bytes.

## Exact identity and prerequisite gap

Required local fork base: 5e55510dbeb869bacfcd843f975632dc739519af
Base tree: 97d0270efa7fc15b153022753fbbe67acc010ea6
Result commit: e04e2ae1a0d47cdedf5380b5a0d94f280a82d5d1
Result tree: 89e3964b370d6cd1474be03c04a3c3328521947f
Result parent: f2b01139d79c71e4596c0e0aaab105e194b18c19

The retained repo is shallow at upstream pin d0bdbe11a9624435b6dca3968389bd59c6a559a2.
Four earlier fork commits after that pin contain query-cache, onboarding privacy,
CLI-pairing and first-engineer UI changes. Manifest lists their exact identities;
their complete approval is not established here. Their separate prerequisites/ series is now contentsafety-cleared for draft packaging only, NOT independently approved.
The original four-repair series still requires this fork base. FULL-APPLY.md documents all eight patches from exact retained public upstream pin d0bdbe11, subject to main verifying GitHub availability.
No complete approved series from public upstream is claimed; prerequisite implementation review remains open.

Remote v0.3.1 advertises 63c62e3ada077bac45292f3d2779bd48a8831cda.
Neither that tag nor package.json version 0.3.1 describes the required fork base.
The original included lifecycle plan's version shorthand must not override these
commit identities. Do not apply directly to v0.3.1 or d0bdbe11. Public reachability
of exact d0bdbe11 was not rechecked; no clone/fetch/install was performed.

## Apply after independent safety review

Instructions only, not run here. Set $patchDir to this prepared folder. Work from
an already provisioned clean disposable checkout at the exact required fork base:

    if ((git --no-optional-locks rev-parse HEAD) -ne '5e55510dbeb869bacfcd843f975632dc739519af') { throw 'Wrong base' }
    if ((git --no-optional-locks rev-parse 'HEAD^{tree}') -ne '97d0270efa7fc15b153022753fbbe67acc010ea6') { throw 'Wrong base tree' }
    if (git --no-optional-locks status --porcelain) { throw 'Dirty checkout' }
    $m = Get-Content (Join-Path $patchDir 'manifest.json') -Raw | ConvertFrom-Json
    foreach ($p in $m.patches) {
        $f = Join-Path $patchDir $p.file
        if ((Get-FileHash $f).Hash.ToLower() -ne $p.sha256) { throw 'Hash mismatch' }
        git --no-optional-locks apply --check --index $f
        if ($LASTEXITCODE) { throw 'Patch does not apply' }
        git --no-optional-locks apply --index $f
        if ($LASTEXITCODE) { throw 'Apply failed' }
        if ((git --no-optional-locks write-tree) -ne $p.tree) { throw 'Wrong intermediate tree' }
    }

This recreates exact tracked trees, not original commit metadata/IDs. Main alone
owns integration commits. No source checkout or index was changed during packaging.

## Build and source tests

Instructions only. Use already provisioned disposable Windows, Node >=20, pinned
pnpm 9.15.4 and existing frozen-lockfile dependencies. No installation is included.
Set PAPERCLIP_WINDOWS_PYTHON to an approved absolute Python interpreter path.
Windows-specific worker tests require that variable and real Windows Job support;
inspect skips rather than interpreting skipped Windows cases as successful proof.

    pnpm run build
    pnpm run typecheck
    pnpm exec vitest run packages/adapter-utils/src/windows-worker.test.ts packages/adapter-utils/src/windows-worker-protocol.test.ts packages/adapter-utils/src/windows-worker-startup.test.ts packages/adapter-utils/src/windows-worker-heartbeat.test.ts packages/adapter-utils/src/service-declarations.test.ts packages/adapters/codex-local/src/server/codex-args.test.ts

Commands derive from source package scripts and included test paths; not executed.
Inspect existing workspace preflight scripts before running. Tests create synthetic
workers and temporary evidence; no live account or production service is required.

## Static inspection and byte reproduction

All complete patch texts scanned for private absolute user paths, credential-shaped
keys, authenticated URLs and account value assignments: zero matches. Process
boundary, heartbeat, declaration and test source was statically read. This is not
an independent security approval. Complete selected interval git diff --check passed.
No generated logs/receipts, bundles, dependencies or author email metadata included.

Each manifest patch pins parent, commit, trees, SHA256, byte size and changed paths.
Regenerate raw LF bytes with git --no-optional-locks diff and these options:
--no-ext-diff --no-textconv --no-color --no-renames --no-indent-heuristic
--diff-algorithm=myers --full-index --binary --src-prefix=a/ --dst-prefix=b/
--unified=3 --output=<patch-file> <parent> <commit>
Do not reserialize through text pipelines.

## Published raw bytes

Final remote readback identified Git CRLF-to-LF conversion in documentation,
series and JSON serialization, and in LICENSE.upstream. No raw .patch bytes
changed; all eight patch hashes and reproduced trees remain exact. The public
license pin in manifest.json now names the published LF Git blob, which matches
the upstream LICENSE blob. Its original packager checkout hash is retained
separately for provenance. Verify raw objects with `git show`, since a Windows
working checkout may translate line endings. Metadata publication is not proof
of a byte-identical local checkout. No global Git setting was changed.
