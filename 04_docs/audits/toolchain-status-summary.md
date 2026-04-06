# Toolchain Status Summary

Last updated: 2026-04-05

## Installed and usable

- Git 2.49
- Git LFS
- Node.js 22.16
- `npm.cmd` 10.9.2
- `winget`
- PowerShell 5.1
- `schtasks`
- Codex desktop app runtime

## Installed but broken or incomplete

- Python 3.13 appears installed from the machine uninstall registry, but `python`, `py`, and `pip` are not callable in this sandbox account.
- VS Code is installed, but `code` is not callable from the current shell.
- Cursor command resolves to the other account via machine PATH residue and is not usable from this sandbox account.
- `wsl.exe` exists, but WSL itself is not installed yet.

## Missing but important

- PowerShell 7 (`pwsh`)
- `uv`
- `gh`
- `pnpm`
- Ollama

## Optional later

- Rust toolchain
- Docker Desktop
- WSL2
- Bun
- Playwright
- llama.cpp
- Aider

## Practical install order later

1. Repair Python
2. Install PowerShell 7
3. Install `uv`
4. Install `gh`
5. Install `pnpm`
6. Install Ollama

## Things not to do yet

- Do not clean machine PATH yet without approval.
- Do not install Docker and WSL just because they are common.
- Do not install Rust until a Rust-first repo becomes active work, not just an evaluated repo.
