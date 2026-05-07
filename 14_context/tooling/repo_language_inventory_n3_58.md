# Repo Language Inventory — N+3.58A

Generated: 20260506T211627Z
Branch: `feat/ghoti-agent-claude-n3-58-language-truth-rust-readiness-merge-assistant` | HEAD: `874aefd`

## Tracked Language Summary

| Language | Tracked Files |
|----------|--------------|
| Markdown | 596 |
| (no ext) | 83 |
| JSON | 64 |
| Python | 51 |
| PowerShell | 13 |
| .txt | 7 |
| .jsonl | 6 |
| JavaScript | 4 |
| HTML | 3 |
| CSS | 2 |
| YAML | 2 |
| TOML | 1 |

## Java Truth

Tracked Java: **NONE**
Tracked Java build files (pom.xml/build.gradle): NONE

## Rust Truth

Tracked Rust: **NONE**
Tracked Rust manifest files (Cargo.toml/Cargo.lock): NONE

## Why GitHub May Show Java or Rust

GitHub detects repository language from ALL files in the repository tree, including untracked files, third-party content in subdirectories, generated output, and workspace files outside .gitignore. It also caches language stats and may display stale data after files are removed. The 'git ls-files' command shows only tracked files; GitHub counts more. If GitHub shows Java but 'git ls-files' shows none, the Java files are likely: untracked, in 21_repos/third_party/, in .gitignore'd output folders, or a stale GitHub language cache.

Likely causes in this repo:
- `21_repos/third_party/` may contain reference intake repos with Java/Rust content (read-only, not owned).
- Untracked output folders, generated files, or workspace-only content.
- Stale GitHub language cache after files were removed from tracking.

## Runtime Stack (Current — Truthful)

- **Python** — primary runtime scripts, CLI, orchestration
- **Node.js / JavaScript** — dashboard MVP server, frontend
- **PowerShell** — Windows operator scripts
- **Rust** — NOT present. Planned for future stable-core use only.
- **Java** — NOT present. No Java tracked or planned.

## Conclusion

The Ghoti repo does not use Java or Rust in its tracked codebase.
Any GitHub UI showing Java reflects external/untracked content or a stale language cache.
