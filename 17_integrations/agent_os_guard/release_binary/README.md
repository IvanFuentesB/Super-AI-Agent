# Packaged Agent OS guard source

This review snapshot targets the release revision in SOURCE_MANIFEST.json. The patch carries the guard, Python resolver, release packaging change, tests and build provenance. Apply it only to that base. Public main lacks the complete release and swarm implementation. The executable and installation payload stay outside this source port.

The resolver checks the packaged executable against the release manifest and provenance digest. Test the actual installed workflow in a disposable release without Cargo and verify its manifest again after queue writes. Host adoption and merge require separate clearance.
