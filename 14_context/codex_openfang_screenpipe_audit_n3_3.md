# Codex OpenFang + Screenpipe Audit - N+3.3

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Observed HEAD: bd6a76f
Status label: parallel_audit_only / no_runtime_changes / not_runtime_wired

## OpenFang Section

Status label: exact_repo_unknown_or_unverified / rust_candidate / not_runtime_wired

### Current Truth

OpenFang is treated here as an unverified Rust candidate. This Codex lane did not search the web, clone a repo, install Rust dependencies, or run any OpenFang code. The exact repository identity, license, purpose, and runtime behavior must be verified before it enters the main intake registry as anything stronger than a watchlist item.

### Why A Rust Codebase Matters

Rust candidates matter for Ghoti because Rust can be a strong fit for:

- local desktop/screen tooling
- low-level browser/CDP helpers
- long-running local services
- performance-sensitive capture/indexing
- safer native components when source and dependencies are trustworthy

Rust also raises setup and trust questions:

- build scripts can run arbitrary code
- native dependencies can be hard to audit
- Windows build behavior can differ from Linux/macOS docs
- binaries may need signing, permissions, or local firewall review

### Required Checks Before Clone

Before any OpenFang clone or install:

1. Exact repo identity.
2. Official source URL.
3. License and commercial constraints.
4. Primary purpose and whether it actually helps Ghoti.
5. Build scripts, especially `build.rs`, shell scripts, PowerShell scripts, install scripts, and postinstall hooks.
6. Dependency tree and supply-chain risk.
7. Network behavior at runtime.
8. Filesystem behavior at runtime.
9. Whether it requires credentials, browser profiles, or external accounts.
10. Windows compatibility and rollback path.
11. Whether it can run in an isolated folder or sandbox.

### OpenFang Verdict

OpenFang remains `exact_repo_unknown_or_unverified / rust_candidate / not_runtime_wired`.

Do not clone, build, or install until a future milestone identifies the exact repo and the user explicitly approves a read-only source evaluation.

## Screenpipe Section

Status label: local_capture_candidate / retention_required / not_runtime_wired

### Purpose

Screenpipe-style tooling may help Ghoti with:

- local screen/audio memory
- operator replay
- future observation layer
- local context reconstruction
- "what happened during this session" review

This is not automatic AI screen sharing. It must remain local-only, operator-controlled, and retention-limited.

### 3-Day Retention Requirement

Default policy:

- `retention_days = 3`
- cleanup starts as dry-run only
- cleanup must report files and bytes before deletion
- deletion must never cross outside allowed capture roots
- deletion must be manually approved or run by a clearly named local-only task

Suggested allowed roots must be explicit, for example:

- `01_projects/dashboard_mvp/.tmp-screenshots/capture_frames`
- a future explicit Screenpipe local storage directory if approved

Never delete:

- source files
- docs
- runtime code
- third-party repos
- user documents
- browser profiles
- credentials
- anything outside the configured capture roots

### Sensitive Capture Boundaries

Screen/audio capture must not run while any of these are visible or active:

- passwords
- 2FA codes
- banking
- email
- password managers
- private docs
- private chats
- legal/tax/medical records
- live external accounts unless explicitly approved
- confidential client/work material

Capture must be visible in the dashboard or overlay when active.

### Future Integration Requirements

If Screenpipe is evaluated later, Ghoti should require:

- dashboard capture status
- local-only storage path
- explicit ActionIntent proposal before starting capture
- operator approval before capture starts
- retention policy shown before capture starts
- manual dry-run cleanup first
- audit entry for start/stop/cleanup
- no cloud sync by default
- no automatic background recording

### First Safe Screenpipe Test

First test should be:

- install-free documentation/source review
- no capture started
- identify data directories
- identify retention controls
- identify audio defaults
- identify cloud/network behavior
- write a local dry-run retention plan

Only after that should a later milestone start capture, and only with explicit operator approval.

### Screenpipe Verdict

Screenpipe is promising as a local observation/memory layer, but it is sensitive. The right next step is retention-policy design and dry-run cleanup validation, not capture.

Verdict: research next / local-only / retention-required / not runtime-wired.
