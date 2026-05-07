# Codex N+3.7 CUA / Docker Gate Audit

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Status label: codex_audit / docker_cua_gate / no_install / not_runtime_wired

## Commands Run

- `docker --version`
- `docker compose version`
- `wsl --status`
- `wsl --list --verbose`
- `powershell.exe -NoProfile -Command "Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsHardwareAbstractionLayer"`
- `powershell.exe -NoProfile -Command "rustc --version; cargo --version"`
- `python --version`
- `node --version`
- `npm --version`

No install, Docker run, WSL install, CUA execution, screen capture, or browser/desktop automation occurred.

## Toolchain Truth

| Check | Result |
|---|---|
| Docker installed | NO: `docker` command not recognized |
| Docker Compose installed | NO: `docker` command not recognized |
| WSL executable | present as Windows command |
| WSL installed/configured | NO: `wsl --status` and `wsl --list --verbose` report WSL is not installed |
| Windows edition | `Windows 10 Home Single Language` |
| OS HAL | `10.0.26100.1` |
| Rust | YES: `rustc 1.95.0`, `cargo 1.95.0` |
| Python | YES: `Python 3.13.12` |
| Node | YES: `v22.16.0` |
| npm | YES: `10.9.2` |

## CUA Clone Truth

| Field | Value |
|---|---|
| CUA clone path | `21_repos/third_party/evals/cua` |
| Path exists | YES |
| Git metadata exists | YES |
| HEAD | `46dbcb47802e2c712c87e9a34d4d5b06829a2932` |
| Remote | `https://github.com/trycua/cua.git` |
| Runtime wired | NO |
| Third-party contents staged | NO |

## CUA Source / Path Truth

Existing audits say:

- CUA exact source is `https://github.com/trycua/cua`.
- Cua Driver is macOS host-focused.
- Lume path is macOS/Apple Silicon-focused.
- Windows Sandbox path is blocked on this Windows Home environment.
- Docker/Ubuntu/Kasm path is the practical local route if Docker Desktop/WSL2 is installed.
- Cloud CUA path exists but was not evaluated and would require external service approval.

## Likely Next Unlocker

Likely next unlocker:

1. Docker Desktop install.
2. WSL2 enable/configure as Docker backend.
3. CUA Docker/Ubuntu/Kasm lightweight container path.
4. Screenshot-only observe smoke in a local sandbox.

This is blocked until explicit operator approval.

Required approval phrase:

`APPROVE DOCKER DESKTOP INSTALL FOR CUA SANDBOX`

## What Must Stay Forbidden

- no click/type in first smoke
- no live accounts
- no stealth/evasion
- no background autonomy
- no host desktop control
- no credentials or 2FA
- no social/email/banking/payment/trading/legal targets
- no provider cap bypass
- no image pull/build/run without explicit approval
- screenshot-only first

## Final Verdict

Docker install gate is needed before a real CUA sandbox smoke on this machine, unless an alternative local adapter is chosen.

If the user wants speed toward computer use, the next approval decision is Docker Desktop install. If the user wants safer no-install progress, choose Screenpipe dashboard status route and Obsidian vault sync first.
