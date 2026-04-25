# Ghoti Rust Setup Plan

Date: 2026-04-25
Branch: feat/ghoti-visible-operator-stack
Status label: plan_only / do_not_install_yet / not_runtime_wired

## Purpose

Prepare a safe Rust toolchain setup path for future Ghoti work without installing anything in this milestone.

Rust may become useful for small, fast, local utilities around token processing, filesystem-safe indexing, desktop helpers, model-adjacent tooling, or future native components. This document is a checklist only. It does not install Rust, does not compile Rust code, and does not wire Rust into Ghoti runtime.

## Why Rust May Matter For Ghoti

- Fast local tooling for scanning, indexing, and context compaction.
- Safer native helper binaries where memory safety matters.
- Potential future desktop/overlay experiments if Ghoti moves beyond browser-based overlay prototypes.
- Possible high-performance token, prompt, or repo-analysis utilities.
- Useful ecosystem for CLI tools that may support local-first operator workflows.

## Where Rust May Fit Later

| Area | Possible use | Current truth |
|---|---|---|
| Context/token utilities | Local prompt/context compaction helpers | Concept only; not implemented |
| Repo analysis | Fast source graph or code-review graph tools | Concept only; not implemented |
| Desktop helpers | Native window/overlay experiments | Future research; current overlay is browser-based |
| MCP/tooling helpers | Local binaries called by supervised workflows | Future only; not runtime-wired |
| Performance-sensitive capture/indexing | Metadata or frame-index processing | Future only; existing capture remains JavaScript/runtime-side |

## Do Not Install Yet

Rust must not be installed during this milestone. Install only after explicit operator approval in a later task.

Before installation, confirm:

- The branch and working tree are understood.
- No runtime/private/local junk is staged.
- The user explicitly approves machine-level toolchain changes.
- The intended Rust use case is narrow and documented.
- Rollback expectations are understood.

## Windows Install Options

### Option A: Official Rustup Installer

Use only after explicit approval:

```powershell
winget install Rustlang.Rustup
```

Then open a new terminal and verify:

```powershell
rustc --version
cargo --version
rustup --version
```

### Option B: Manual Installer

Use only after explicit approval:

1. Download from `https://rustup.rs/`.
2. Run the Windows installer.
3. Accept the default stable toolchain unless a later milestone requires otherwise.
4. Open a new terminal and run the verification commands below.

### Option C: Existing Toolchain Verification Only

Safe read-only checks:

```powershell
rustc --version
cargo --version
rustup --version
```

These commands verify presence only. They do not install Rust.

## Verification Commands

After an approved install, run:

```powershell
rustc --version
cargo --version
rustup --version
cargo --help
```

Optional local smoke test after approval:

```powershell
cargo new --bin ghoti-rust-smoke
cd ghoti-rust-smoke
cargo run
```

Do not commit generated smoke-test projects unless a later milestone explicitly asks for a Rust workspace.

## Rollback Notes

If Rust was installed with rustup and must be removed later:

```powershell
rustup self uninstall
```

If installed through winget:

```powershell
winget uninstall Rustlang.Rustup
```

Rollback should be operator-approved because it changes machine-level tooling.

## Safety Boundaries

- Do not install Rust without explicit user approval.
- Do not create native binaries that bypass Ghoti approval gates.
- Do not add autonomous execution paths.
- Do not wire Rust tools into runtime until a separate supervised implementation milestone proves safety, logging, and rollback.
- Do not use Rust tooling to bypass platform limits, model safety, legal boundaries, or TOS.
- Do not commit generated build artifacts such as `target/`.

## Current Status

- Setup status: `plan_only / do_not_install_yet / not_runtime_wired`
- Rust installed by this milestone: NO
- Rust code added by this milestone: NO
- Runtime wired: NO
- Third-party repos cloned: NO
