# Paperclip - Tier 1 intake (N+6.22A)

Static, planning-only. **`source_needed`**: the exact "Paperclip" project is ambiguous
(several unrelated projects use the name), so no URL is recorded and nothing is cloned.

## Status

- Tier: 1 (operator flagged it as a flagship priority).
- Source: **source_needed** - the operator must confirm the exact repo/URL.
- Gate: `tier1_static_inspect` once the URL is confirmed; no install/clone/execute yet.

## What we will check first (read-only, after the URL is confirmed)

- License + README + packaging metadata (is reuse allowed, what does it actually do).
- Dependency and install hooks (any preinstall/postinstall scripts, any network on
  install) before it is ever added to the N+6.19A allowlist.
- Whether it needs accounts, API keys, or live network - if so it is deferred to a
  secret-management milestone.

## Why it might matter

The operator ranked Paperclip as Tier 1, so it is worth a fast, careful static pass as
soon as the exact source is known. Until then it stays a source-needed placeholder; it
is never guessed.
