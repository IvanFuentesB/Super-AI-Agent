# Language and Rust Strategy — N+3.58A

## Current Truthful Stack

| Language | Present | Role |
|----------|---------|------|
| Python | YES — tracked | Primary runtime scripts, orchestration, CLI |
| JavaScript / Node.js | YES — tracked | Dashboard MVP server and frontend |
| PowerShell | YES — tracked | Windows operator automation scripts |
| Markdown | YES — tracked | Documentation, context files |
| JSON | YES — tracked | Configuration, data |
| YAML | YES — tracked | Configuration |
| Shell | YES — tracked | Utility scripts |
| Java | NO — not tracked | Not present, not planned |
| Rust | NO — not tracked | Not present; planned for future stable-core only |

## Java Status

Java is NOT tracked in this repository.
If GitHub shows Java, the cause is one of:
1. Untracked third-party content in `21_repos/third_party/` (read-only reference repos)
2. Generated output or workspace files outside .gitignore
3. Stale GitHub language cache after files were removed

**Authoritative check:** `git ls-files | Select-String "\.java$|pom.xml|build.gradle"` returns nothing.

## Rust Status

Rust is NOT tracked in this repository.
**Authoritative check:** `git ls-files | Select-String "\.rs$|Cargo.toml|Cargo.lock"` returns nothing.

## Rust Introduction Strategy

### Do Not Rewrite Now

- Python MVP is not yet stable enough to justify a rewrite.
- Rewriting active scripts mid-development would introduce regressions.
- Ghoti needs end-to-end supervised workflows first, then stable core extraction.
- Do not add unused Rust crates to affect GitHub language stats — that is dishonest.

### Introduce Later For

When the Python core is stable and we need:
- **Approval gate engine** — compile-time correctness for policy decisions
- **Durable job runner** — crash-safe task execution with state recovery
- **Plugin/tool sandbox boundary** — memory-safe process isolation
- **File watcher/event loop** — low-overhead OS event monitoring
- **Desktop/operator daemon** — lightweight Windows background service

### Principles

- Introduce Rust for a specific bounded component, not a full rewrite.
- Keep Python orchestration layer. Rust handles the stable hot path.
- Each Rust component must have a clear boundary and a Python fallback during transition.

## Completion Band Estimates

| Milestone State | Estimated Band |
|-----------------|---------------|
| main before N+3.51/N+3.58 merge | ~74–76% |
| N+3.51/N+3.56-FIX branch after clean Codex audit | ~90–94% |
| After N+3.58 language truth + merge assistant | ~92–95% |
| 100% | Actual end-to-end supervised workflows (not just scaffolding) |

## Next Steps

1. Codex audit this branch — expect PASS.
2. After PASS: use merge assistant to land N+3.56-FIX into main.
3. Separately land N+3.58 into main.
4. Run real supervised workflow end-to-end to reach 100%.
5. When Python MVP is stable: scope one Rust component (approval gate engine).
