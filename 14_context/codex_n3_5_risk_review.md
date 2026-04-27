# Codex N+3.5 Risk Review

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: ca403cd
Status label: risk_review / no_runtime_changes / not_runtime_wired

## What Can Go Wrong

CUA/computer-use can fail dangerously because it crosses from "planning" into "doing":

- It can click the wrong UI element.
- It can type into the wrong app.
- It can submit a form.
- It can expose or capture credentials.
- It can interact with logged-in accounts.
- It can create misleading confidence if dashboard labels overclaim readiness.
- It can retain screenshots longer than intended.
- It can become a hidden background worker if not surfaced visibly.
- It can bypass approval gates if "approval to use CUA" is treated as blanket approval.

## What Must Stay Blocked

Hard blocks:

- live accounts
- passwords
- 2FA
- password managers
- banking
- payments
- trading
- email
- social posting
- legal/tax filing
- private documents
- click/type in first smoke
- shell execution
- file uploads
- stealth/evasion
- cap/quota bypass
- autonomous loops

## Why CUA Is Higher Risk Than Browser-Only Adapters

Browser-only adapters have a narrower blast radius:

- target is usually one browser context
- domains can be allowlisted
- page state can be inspected
- no OS-wide permissions are usually needed

CUA can be broader:

- may see the whole screen or host app windows
- may need accessibility/screen-recording permissions
- may act on native apps
- may operate in background where the user does not see focus changes
- may combine screenshot, click, type, and app launch capabilities

Therefore CUA must start sandbox-only and observe-only.

## Why Screenpipe Retention Matters

Screenpipe-style memory can be useful, but capture data is sensitive. Retention limits are not a nice-to-have; they are part of the safety model.

Required retention rules:

- default 3 days
- local-only
- dry-run cleanup first
- explicit allowed roots
- never delete outside capture roots
- never stage captures
- no hidden recording
- visible capture status

Without retention, local memory becomes surveillance clutter and a privacy liability.

## Why Obsidian Vault Reduces Token Use Safely

An Obsidian/plain markdown vault reduces token use by making the current project state compact and linkable:

- short notes instead of huge pasted logs
- one concept per file
- links to source docs and commits
- easy handoff for ChatGPT, Claude, and Codex
- no provider quota bypass
- no fake accounts
- no hidden usage evasion

The safest version is plain markdown under `14_context/obsidian_vault/`, with no plugins and no RAG ingestion at first.

## Recommended Next Milestone

Primary recommendation: N+3.6 CUA screenshot-only sandbox smoke.

Precondition:

- source path is accepted
- sandbox profile remains disabled by default
- click/type/shell/live accounts remain false
- operator explicitly approves any CUA clone/install/run

Safer alternate recommendation: N+3.6 Screenpipe retention route.

Choose Screenpipe route first if the user wants:

- no external driver install
- no CUA execution
- local-only visibility
- retention policy validation

## Final Verdict

CUA is the right strategic direction, but the next real implementation should be boring and reversible. Descriptor-only or screenshot/observe-only is safe enough. Click/type is not.
