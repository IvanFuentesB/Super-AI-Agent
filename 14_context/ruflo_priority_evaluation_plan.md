# RUFLO Priority Evaluation Plan

Date: 2026-04-26
Branch: feat/ghoti-visible-operator-stack
Status label: priority_research_plan / not_installed / not_runtime_wired

## Why RUFLO Is Priority

RUFLO is the top-priority external repo/tool candidate for multi-agent orchestration because Ghoti's long-term direction needs many small, single-purpose, supervised agents with shared local memory and honest status boundaries.

This plan prepares evaluation only. RUFLO is not installed, not cloned by this milestone, and not wired into Ghoti runtime.

## What To Evaluate First

- Core purpose and architecture.
- License and commercial-use implications.
- Whether it runs locally on Windows.
- Whether it requires cloud services, API keys, browser logins, paid accounts, Docker, GPUs, or background daemons.
- Whether it supports multiple agents in parallel.
- Whether agents can be constrained to a repo-local sandbox.
- Whether agents can share local memory without leaking private data.
- Whether it can expose clear operator approvals before file writes, browser actions, shell commands, network calls, or external account use.
- Whether logs are durable and reviewable.

## Local Install Prerequisites To Check Later

- Git availability.
- Node/npm or Python requirements.
- Rust requirements, if any.
- Docker requirement, if any.
- Windows shell compatibility.
- Environment variables and secrets required.
- Ability to run without broad filesystem permissions.

No install should happen until a later milestone explicitly approves it.

## Account / Auth Risk Questions

- Does RUFLO require personal accounts?
- Does it require browser cookies, OAuth, Claude/Codex/OpenAI/Anthropic credentials, or hosted dashboards?
- Can it run with the user's accounts only after explicit approval?
- Can credentials be avoided for a first local smoke test?
- Are account actions visible, reversible, and approval-gated?
- Could it accidentally trigger usage-limit bypass, account abuse, or TOS violations?

## Parallel Agents Questions

- Can agents run concurrently?
- Can each agent have a single narrow role?
- Can agent permissions be scoped by role?
- Can agents be paused, inspected, or canceled?
- Does the tool provide per-agent logs?
- Can results be merged without autonomous code execution?

## Shared-Memory Design Questions

- Is shared memory file-based, database-backed, or service-backed?
- Can memory stay local to the repo or a clearly approved runtime directory?
- Can sensitive data be excluded or redacted?
- Can memory entries include provenance and timestamps?
- Can the operator review and delete memory entries manually?
- Can memory be read-only for agents until explicit approval is granted?

## Safety Gates

- RUFLO must remain research-only until a separate integration milestone.
- Any clone/install/run must be explicitly approved.
- No broad filesystem permissions until sandboxing is proven.
- No browser/account actions without explicit approval.
- No external network actions beyond approved docs/license review.
- No autonomous file writes, shell commands, PRs, commits, pushes, purchases, posts, messages, scraping, or account changes.
- Any future action path must preserve Ghoti approval gates and durable logs.

## Future Isolated Sandbox Test Plan

1. Read public README/license/docs without cloning, if possible.
2. Fill `14_context/external_repo_evaluation_template.md` for RUFLO.
3. If approved, clone into a clearly named isolated folder under the approved third-party area.
4. Inspect dependency manifests before installing.
5. Run static checks only.
6. If approved, run a no-network or minimal-local smoke test.
7. Confirm generated files are ignored and not staged.
8. Verify no credentials or personal accounts are required for the smoke test.
9. Record all results in the finish-line log.

## Do-Not-Do List

- Do not use RUFLO for usage-limit bypass.
- Do not use it for account abuse.
- Do not use it for autonomous external actions.
- Do not connect paid/cloud services without explicit approval.
- Do not grant broad filesystem permissions until sandboxed.
- Do not connect personal accounts, browser cookies, OAuth flows, or API keys without explicit approval.
- Do not wire RUFLO into Ghoti runtime until safety gates, logs, and approvals are proven.

## Current Status

- Priority: TOP PRIORITY for multi-agent orchestration evaluation.
- Source/docs/license evaluated read-only: YES — see `14_context/ruflo_read_only_source_docs_license_evaluation.md`.
- Installed: NO.
- Cloned by this milestone: NO.
- Runtime wired: NO.
- Approval status for clone/install: not granted in this milestone.
