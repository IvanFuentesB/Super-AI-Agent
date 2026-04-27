# Codex CUA Sandbox Profile Review - N+3.5

Date: 2026-04-27
Branch: feat/ghoti-visible-operator-stack
Starting HEAD: ca403cd
Status label: parallel_audit_only / sandbox_profile_review / not_runtime_wired

## Profile Reviewed

File read: `23_configs/cua_sandbox_profile.example.json`

Codex did not edit this profile and did not stage it.

## Profile Truth

The example profile currently has the right safety posture for the next milestone:

| Field | Value observed | Review |
|---|---|---|
| `enabled` | `false` | Good. Nothing should run by default. |
| `mode` | `sandbox_only` | Good. Host desktop should remain blocked. |
| `require_action_intent` | `true` | Good. CUA must be action-intent gated. |
| `require_human_approval_per_action` | `true` | Good. No blanket approval. |
| `require_payload_hash_match` | `true` | Good. Prevents mutation/replay drift. |
| `allow_screenshots` | `true` | Acceptable only for sandbox/approved test target. |
| `allow_click` | `false` | Correct for next milestone. |
| `allow_type` | `false` | Correct for next milestone. |
| `allow_shell` | `false` | Correct. CUA smoke should not become shell automation. |
| `allow_file_upload` | `false` | Correct. |
| `allow_live_accounts` | `false` | Correct and non-negotiable. |
| `retention_days` | `3` | Correct baseline for screenshots/traces. |
| `allowed_windows` | `example.com test page`, `local dashboard` | Acceptable for observe/screenshot-only. |
| `forbidden_targets` | banking, password manager, 2FA, email inbox, social posting, trading, payments | Correct; should be expanded later if needed. |
| `audit_log` | `05_logs/cua_action_audit.jsonl` | Good as a local audit target if ignored/managed correctly. |

## Safety Assessment

This profile is safe enough for the next milestone if the next milestone is descriptor-only or screenshot/observe-only.

It is not enough for click/type execution yet because click/type needs additional fields:

- max actions per run
- expected foreground/sandbox target
- coordinate bounds or selector rules
- no-autosubmit enforcement
- replay-blocking evidence
- screenshot redaction/sensitive-window checks
- explicit stop/kill-switch path

## Required Next-Milestone Boundaries

For N+3.6 screenshot-only sandbox smoke:

- `enabled` remains false unless the operator explicitly starts the test.
- `allow_click` remains false.
- `allow_type` remains false.
- `allow_shell` remains false.
- `allow_live_accounts` remains false.
- screenshot target is local dashboard or `example.com`.
- one ActionIntent is proposed.
- human approval is required.
- payload hash is checked.
- audit event is written.
- screenshots are local-only and retention-limited.

## Allowed Targets Review

Acceptable for first smoke:

- local dashboard read-only page
- local static test page
- `example.com` reference page

Not acceptable for first smoke:

- logged-in browser profiles
- email
- social sites
- banking/payment/trading sites
- cloud admin consoles
- password managers
- private documents

## Retention Review

Three-day retention is appropriate. Future cleanup must:

- default to dry-run
- show files and byte count before deletion
- delete only under explicit capture roots
- never delete outside allowed roots
- never stage screenshots or traces

## Verdict

Verdict: profile is conservative and safe enough for a next descriptor-only or screenshot/observe-only milestone.

Do not use it for click/type yet. Click/type should remain a separate milestone after source audit, sandbox proof, retention proof, and audit-read-model proof.
