# Publishability Scope

## Core Vs Vendor Scope

- core scan should focus on tracked core files and first-party folders
- third-party intake folders should be optionally excluded by default

## Why Exclusions Matter

Vendor repos often contain example `.env` files, fixtures, and test keys that are noisy for public-core review even when the core repo itself is clean.

## Practical Rule

Scoped scanning helps public release review stay focused on first-party code, configs, docs, and tracked artifacts instead of vendor intake noise.
