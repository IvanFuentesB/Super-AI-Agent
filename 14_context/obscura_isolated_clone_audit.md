# Obscura Isolated Clone Audit

Status label: `isolated_clone_audit / no_build / no_runtime_wiring`
Date: 2026-04-26
Branch: `feat/ghoti-visible-operator-stack`
Milestone: N+2.9
Auditor: Claude Code (Sonnet 4.6)

---

## Clone Truth

- Clone path: `21_repos/third_party/evals/obscura`
- Source URL: https://github.com/h4ckf0r0day/obscura
- Clone command: `git clone --depth 1 https://github.com/h4ckf0r0day/obscura.git`
- Commit hash cloned: `99e75f1` — "fix: load balancer panics, stealth flag, shadow DOM polyfill"
- cargo build run: NO
- cargo test run: NO
- binary executed: NO
- Staged in git: NO (third-party eval area; intentionally excluded)

---

## Why It Matters for Ghoti

Obscura is a Rust-based headless browser engine offering a single binary, CDP (Chrome DevTools Protocol) server, and Puppeteer/Playwright compatibility. For Ghoti, it is relevant as a potential lightweight replacement for full headless Chrome in browser automation workflows:
- 30 MB memory vs 200+ MB for headless Chrome
- Instant startup vs ~2s for Chrome
- CDP compatibility means existing Playwright scripts could target it
- Single binary with no runtime dependencies after build

Risk: "stealth mode" (anti-detection + tracker blocking) is a feature flag that must be evaluated carefully for TOS/legal-aware use only.

---

## License

- License: Apache 2.0
- Copyright: not explicitly listed (repo owner h4ckf0r0day)
- Commercial-use: permitted under Apache 2.0
- Patent grant: included (Apache 2.0 patent clause)
- AGPL implications: none
- Attribution required: yes (NOTICE file if present; LICENSE file copy)

Note: The README badges show MIT but the LICENSE file content is Apache 2.0. Apache 2.0 governs.

---

## Rust Requirement

- Rust version required: 1.75+
- Local Rust version: `rustc 1.95.0` — satisfies requirement
- Build time: ~5 minutes (V8 compiles from source on first build; cached after)
- `cargo build --release` produces a single static binary
- Stealth mode: `cargo build --release --features stealth` adds anti-detection + tracker blocking

cargo build was NOT run in this milestone. Explicit operator approval required before any build.

---

## Workspace Structure

Cargo.toml defines a workspace with 6 crates:
- `crates/obscura-dom` — DOM processing
- `crates/obscura-net` — Network layer
- `crates/obscura-browser` — Browser engine core
- `crates/obscura-cdp` — CDP (Chrome DevTools Protocol) implementation
- `crates/obscura-js` — JavaScript (V8) integration
- `crates/obscura-cli` — CLI interface

Key dependencies (from workspace Cargo.toml):
- `tokio` (async runtime), `reqwest` (HTTP with cookies/gzip/TLS), `serde/serde_json` (data)
- `tokio-tungstenite` (WebSocket for CDP), `html5ever` / `servo_arc` / `cssparser` (HTML/CSS parsing)
- `clap` (CLI args), `tracing` / `tracing-subscriber` (logging)
- No external cloud/account deps in Cargo.toml

---

## CDP / Puppeteer / Playwright Compatibility Claims

From README:
- Claims drop-in replacement for headless Chrome with Puppeteer and Playwright
- Starts CDP server at port 9222: `obscura serve --port 9222`
- Puppeteer compatibility: claimed YES
- Playwright compatibility: claimed YES

These claims have NOT been verified by running the binary. At this trust level: treat as "stated capability, not verified."

---

## Scraping / Stealth Risk Boundaries

The repo README uses "Lightweight, stealthy" prominently and lists "Anti-detect: Built-in" as a differentiator. The `--stealth` flag enables anti-detection fingerprint spoofing and tracker blocking.

**Legal/TOS-aware use only:**
- Stealth features are marketed for "automation at scale" and scraping
- Anti-detection can be used for both legitimate (avoiding bot misdetection on your own sites) and illegitimate (bypassing anti-bot protections on third-party sites) purposes
- Ghoti must never use stealth mode to circumvent platform anti-bot protections, paywalls, rate limits, or access controls
- TOS-aware use: only scrape sites where: (a) the operator has permission, (b) robots.txt allows, (c) the platform terms allow automated access, (d) no personal data is harvested without consent

The author's GitHub handle (`h4ckf0r0day`) and the "stealth" marketing are flags that suggest the target audience includes adversarial users. The repo itself does not appear to ship malicious code — the Cargo.toml shows standard Rust crates with no obfuscation — but the stealth feature must remain gated and TOS-aware only.

---

## Windows Feasibility

- Windows releases: available as `.zip` from the GitHub releases page (manual download + extract)
- No Windows tarball in the automated download script examples in README (Linux/macOS only shown)
- Building from source on Windows: possible with Rust 1.75+ installed; V8 compilation adds complexity on Windows (requires LLVM/clang toolchain in addition to Rust)
- Assessment: feasible for binary distribution; source build on Windows is more complex than on Linux/Mac

---

## Verdict

**research only → isolated build candidate** after explicit operator approval for `cargo build`.

The source appears clean (no obfuscation, standard Rust crates). CDP/Playwright compatibility is a genuine value proposition for lightweight browser use in Ghoti. However:
- Build has not been run; V8 compilation is resource-intensive
- Stealth features must remain disabled or TOS-gated
- Windows binary from releases page is simpler than a source build but requires manual download
- Author/repo identity (h4ckf0r0day) warrants continued caution

---

## Exact Next Safe Step

Option A — Download pre-built binary (Windows, no Rust build):
```
# Download the .zip from:
https://github.com/h4ckf0r0day/obscura/releases/latest
# Extract manually, test with:
./obscura --version
./obscura fetch https://example.com --eval "document.title"
```

Option B — Build from source (requires operator approval + ~5 min):
```
cd 21_repos/third_party/evals/obscura
cargo build --release
# Do NOT add --features stealth unless explicitly approved and TOS-reviewed
./target/release/obscura --version
```

Do NOT use `--stealth` feature or run against third-party sites without explicit TOS review and operator approval.
