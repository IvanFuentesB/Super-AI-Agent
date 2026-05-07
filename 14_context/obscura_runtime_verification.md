# Obscura Runtime Verification

Status label: `runtime_verified / binary_built / cdp_confirmed / no_stealth / no_live_accounts`
Date: 2026-04-26
Branch: `feat/ghoti-visible-operator-stack`
Milestone: N+3.2
Auditor: Claude Code (Sonnet 4.6)

---

## Build Facts

- Source: `21_repos/third_party/evals/obscura` (commit `99e75f1`, read-only)
- Build command: `cargo build --release` (no `--features stealth`)
- `CARGO_TARGET_DIR`: `C:\tmp\obscura_build` (short path — Windows MAX_PATH workaround)
- Build duration: ~1m 30s (dependencies cached after first download)
- Rust toolchain: `stable-x86_64-pc-windows-msvc` / `rustc 1.95.0`
- Binary location: `C:\tmp\obscura_build\release\obscura.exe`
- Warnings: minor unused imports/variables in `obscura-net`, `obscura-js`, `obscura-cdp`, `obscura-cli` — no errors

### Rustup note
Rustup was present but had no installed toolchains at start of N+3.2. `rustup default stable` was run with operator approval before the build. Toolchain re-downloaded (~400 MB).

---

## Test Results

| Test | Command | Result |
|------|---------|--------|
| Binary runs | `obscura --help` | PASS — CLI responds, lists `serve`, `fetch`, `scrape` subcommands |
| `--version` flag | `obscura --version` | NOT IMPLEMENTED — binary returns error (no version flag in CLI) |
| Version from banner | `obscura serve` startup | `Headless Browser v0.1.0` |
| Fetch + JS eval | `obscura fetch https://example.com --eval "document.title"` | PASS — returns `Example Domain` |
| CDP server start | `obscura serve --port 9222` | PASS — starts at `ws://127.0.0.1:9222/devtools/browser` |
| CDP version probe | `curl http://127.0.0.1:9222/json/version` | PASS — valid JSON response |

### CDP /json/version response
```json
{
  "Browser": "Obscura/0.1.0",
  "Protocol-Version": "1.3",
  "User-Agent": "Obscura/0.1.0 (Headless Browser)",
  "V8-Version": "N/A",
  "WebKit-Version": "N/A",
  "webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/browser"
}
```

Note: `V8-Version` and `WebKit-Version` report `N/A` — these are cosmetic fields; the JS engine (Deno/V8) compiled and ran correctly as shown by the fetch eval.

---

## What Was NOT Tested

| Item | Status | Reason |
|------|--------|--------|
| `--stealth` flag | NOT TESTED | Requires TOS review and explicit operator approval |
| Playwright connection to CDP | NOT TESTED | Deferred — next safe step if operator approves |
| Third-party sites | NOT USED | Only `example.com` (IANA reference domain) |
| Auth profiles | NOT CONFIGURED | Out of scope for N+3.2 |
| Live accounts | NOT CONNECTED | Safety boundary |

---

## Binary Trust Assessment

- Built from source — we compiled it ourselves, dependency chain is standard Rust crates
- No obfuscation in source (confirmed in N+2.9 audit)
- `--stealth` not compiled in (no `--features stealth`)
- Binary is at `C:\tmp\obscura_build\release\obscura.exe` — not in repo, not in PATH
- Source in `21_repos/third_party/evals/obscura` remains unmodified (read-only per policy)

---

## Windows Path Issue (Root Cause)

First `cargo build` attempt failed with `os error 2` (file not found) when trying to create a temp file in the target directory. Root cause: Windows MAX_PATH limit (260 chars) exceeded by the combination of the deep repo path and cargo's temp file naming. Fixed by setting `CARGO_TARGET_DIR=C:/tmp/obscura_build`.

---

## Verdict

**`runtime_verified`** — Obscura builds cleanly on Windows with Rust 1.95.0, fetches pages, evaluates JS, and starts a CDP server. CDP Protocol-Version 1.3 response confirms Playwright/Puppeteer compatibility is structurally present (not yet verified by actual Playwright connection).

---

## Next Safe Steps

**N+3.2a (optional, operator approval required):** Playwright CDP connection test
```python
# Test only — no live accounts, no third-party scraping
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    print(page.title())
    browser.close()
```

**N+3.3:** Gemma model pull — `ollama pull gemma3:4b` (operator approval required, ~2.5 GB)

**Stealth gate (not yet open):** `--stealth` mode requires explicit TOS review and operator approval before any use.
