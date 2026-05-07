# Codex N+3.34 Memory Safety Gate Review

Status: codex_planning_only / memory_safety_gate / not_runtime_wired

Date: 2026-04-30
Branch: feat/ghoti-visible-operator-stack

## Purpose

Audit the risks of adding Obsidian/local memory plus Gemma compression. Memory is infrastructure; bad memory quietly poisons future prompts. This safety gate keeps compressed memory useful without letting it become false authority.

## Risk: Model Hallucination Becomes Memory

Failure mode:

- Gemma invents a commit hash, validation result, installed tool, revenue metric, or implementation status.
- The invented fact gets copied into compact memory.
- Future Claude/Codex prompts treat it as truth.

Mitigations:

- metadata header with source files
- `unknown` for missing facts
- review status before canonical promotion
- require source references for every important claim
- keep durable source files as final authority

## Risk: Stale Memory

Failure mode:

- compact memory says N+3.18 is dirty after it is resolved, or says a tool is not installed after it is installed.

Mitigations:

- include `last_updated`
- include latest known commit
- mark stale after `git status`, install, commit, rebase, or tracker changes
- rebuild compact memory after implementation milestones
- keep dirty-state warning in a dedicated compact file

## Risk: Accidental Deletion Of Source Records

Failure mode:

- compact memory is treated as a replacement for full docs.
- large source docs are deleted to "save tokens."

Mitigations:

- strict rule: compact memory is a pointer layer, not source of truth
- no delete/cleanup commands in memory workflows
- source files referenced, not replaced
- source-controlled diff review for any memory update

## Risk: Unsafe Action Plans Enter Memory

Failure mode:

- a draft says "post this", "email these leads", "upload to Whop", or "run this command."
- future agents follow it without approval.

Mitigations:

- compact memory must label public/money/live actions as approval-required
- no approve/execute semantics in memory files
- no model-output execution
- safety rules compact file included in every implementation prompt
- human approval gates preserved in summaries

## Risk: Secrets Or API Keys Stored

Failure mode:

- a copied log or config includes tokens, credentials, account IDs, private customer data, or 2FA details.

Mitigations:

- never store secrets in Obsidian or compact memory
- do not compress files likely to contain secrets
- if a secret is discovered, stop and ask operator for secure handling
- do not paste secrets into Gemma, Claude, Codex, or ChatGPT prompts

## Risk: Live-Account Instructions Leak Into Autonomous Flows

Failure mode:

- memory says "log into account and launch" without the manual boundary.

Mitigations:

- always specify "manual only after explicit approval"
- no live account runbooks until separately approved
- route live-account steps to human approval, not local automation
- never store credentials or session details

## Risk: Over-Trusting Gemma Compression

Failure mode:

- Gemma summary drops an important blocker or safety rule.
- Claude receives only the compact summary and acts on incomplete context.

Mitigations:

- include source file paths in every compact file
- include "what may be missing" section
- use compact memory as prompt starter, not sole context for risky changes
- require Claude to inspect source files before implementation

## Risk: Prompt Injection From Copied Web/Video Notes

Failure mode:

- copied transcript says "ignore previous instructions" or "run this command."
- Gemma includes it as an instruction in memory.

Mitigations:

- label transcripts and web notes as untrusted source text
- prompt Gemma to summarize content, not follow instructions inside content
- never execute commands from notes
- put suspicious instructions in a risk section, not action plan

## Required Metadata Fields

Memory drafts should include:

- `memory_type`
- `status`
- `last_updated`
- `source_files`
- `generated_by`
- `reviewed_by`
- `review_required_before_canonical_use`
- `latest_known_commit`
- `dirty_state_known`

## Approval Gates

Human approval required before memory promotes or authorizes:

- public posting
- selling/listing products
- outreach/email
- payments
- live account login
- scraping
- app-store work
- install/run of external tools
- runtime wiring
- deletion/cleanup of source records

## Local-Only Draft Rule

Gemma may create local draft memory artifacts.

Gemma must not:

- overwrite canonical memory automatically
- edit source docs automatically
- execute commands
- make external calls
- fetch URLs
- post/send/sell/pay/scrape/login

## Verdict

Memory is powerful because future prompts believe it. The safe design is source-linked, local-only, review-gated, and humble about unknowns.
