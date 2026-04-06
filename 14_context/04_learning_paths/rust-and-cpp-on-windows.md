# Rust and C++ on Windows

Last updated: 2026-04-05

## Why this exists

You said two things clearly:

- later you want to learn Rust
- later you also want C++ available on this machine

This file is the low-risk planning path only.

## Rust later

### When Rust makes sense for you

- performance-sensitive tools
- reliable CLI utilities
- local automation tools that need speed and good packaging
- learning modern systems programming without jumping straight into unsafe-heavy C++

### Recommended install path later

Official Rust guidance for Windows is `rustup`, and the Rust docs note that Windows may require the Microsoft Visual C++ Build Tools.

Sources:

- [Rust install page](https://www.rust-lang.org/tools/install)
- [Cargo installation docs](https://doc.rust-lang.org/stable/cargo/getting-started/installation.html)
- [VS Code Rust docs](https://code.visualstudio.com/docs/languages/rust)

### Recommended Rust editor extensions later

- `rust-lang.rust-analyzer`
  - official VS Code Rust path and best-supported editor integration
- `tamasfe.even-better-toml`
  - useful because Cargo and many project configs use TOML
- `ms-vscode.cpptools`
  - official Windows debugging path mentioned by the VS Code Rust docs for Rust debugging on Windows

### What to install later, not now

- rustup / Rust toolchain
- C++ build tools needed by Rust on Windows if prompted

## C++ later

### When C++ makes sense for you

- native Windows tooling
- system-level integration
- game, graphics, embedded, or existing C++ ecosystem work
- situations where library availability matters more than language ergonomics

### Recommended install path later

Start with the Microsoft-supported Windows path first:

- Visual Studio Build Tools
- Desktop development with C++ workload
- VS Code + Microsoft C/C++ extension

Sources:

- [Microsoft C++ docs](https://learn.microsoft.com/en-us/cpp/?view=msvc-170)
- [Configure VS Code for Microsoft C++ on Windows](https://code.visualstudio.com/docs/cpp/config-msvc)

### Recommended C++ editor extensions later

- `ms-vscode.cpptools`
  - official Microsoft C/C++ extension
- optional later: clangd-based workflow
  - `clangd` provides strong code intelligence, but it is better as a second step after the basic MSVC path is working
  - source: [clangd overview](https://clangd.llvm.org/)

## Which one first later

Recommendation:

- learn Rust first for modern CLI/tooling work
- add C++ after you have a reason to build or debug native Windows/C++ code

Why:

- Rust gives you a cleaner path into systems programming
- C++ is worth having, but it brings more toolchain complexity on Windows

## What is explicitly not happening in this phase

- no Rust install
- no C++ build tools install
- no extension installs yet
