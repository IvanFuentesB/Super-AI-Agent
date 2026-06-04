# MarkItDown N+6.19A Sandbox Report

Source: `https://github.com/microsoft/markitdown`

Clone path: `21_repos/third_party_runtime_sandbox/markitdown`

Observed HEAD: `e144e0a2be95b34df17433bac904e635f2c5e551`

Latest commit summary: `e144e0a Bump version to 0.1.6 (#1914)`

License detected: MIT

## Result

MarkItDown cloned successfully into the ignored runtime sandbox. Only read-only git metadata and static scans were performed.

## Static Scan

Static scan verdict: blocked for runtime execution in N+6.19A.

The scanner found install and container references plus high-review encoded-content patterns. That does not mean MarkItDown is malicious; it means Ghoti should not install/run it automatically in this milestone.

## Future Use

MarkItDown remains the preferred future document-ingestion candidate for PDF/doc-to-Markdown conversion into Obsidian/Ghoti memory. A later milestone should create an isolated venv, inspect package metadata, install only into the sandbox venv, and run `markitdown --help` before any real conversion.
