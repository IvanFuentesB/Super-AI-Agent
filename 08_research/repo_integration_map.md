# Repo Integration Map

## Core Now

### This Repo
- role: actual operator foundation
- includes: runtime MVP, dashboard MVP, browser playground, desktop playground, supervisor flow, approval flow, workspace policy, allowlisted executor, and narrow operator recipes
- rule: this is the only place where core behavior should be implemented

## DNA / Reference

### Claude Code
- status: reference and pattern source
- why: good comparison point for permissioned codebase work, command workflows, hooks, and GitHub-oriented coding loops
- current use: reference only, not merged into the core runtime

### Codex
- status: active execution layer and pattern source
- why: already useful for controlled repo work, branching, checks, and incremental implementation
- current use: operator-facing execution partner, not the only long-term model

### OpenClaw
- status: reference only
- why: useful for later control-plane and browser-channel ideas
- current use: DNA and comparison source, not a near-term dependency

### Official Playwright
- status: reference plus local browser playground dependency
- why: deterministic local browser control is the current browser foundation
- current use: directly used in the local browser playground only

### Windows-Use / Windows-MCP
- status: reference only
- why: likely later inputs for deeper Windows GUI control
- current use: evaluation only

### Open Interpreter / Open Computer Use
- status: reference only
- why: useful comparison points for broader computer-use patterns
- current use: evaluation only

### browser-use / Stagehand
- status: reference only
- why: useful browser-executor pattern sources for later steps
- current use: not integrated into the core runtime

## Later Experiment

### OpenHands / OpenHarness
- status: later experiment
- why: potentially useful for larger harness or agent workflows later
- current use: not part of the current foundation

### Claw Code
- status: later experiment
- why: interesting ideas, but current repo direction is not clean enough to make it a foundation
- current use: reference only, not core

### Kronos
- status: later experiment
- why: possible market or prediction research component
- current use: do not trust for production or real-money decisions; evaluate only if a clear research use appears

### MiroFish
- status: later experiment
- why: possible multi-agent simulation or prediction research component
- current use: experimental only if a justified fit emerges

### Blueprint.am / Blueprint
- status: later experiment
- why: possible hardware-project workflow support for diagrams, BOMs, or assembly guidance
- current use: not a core assistant dependency

### Gemma Local Routing / Eval Layers
- status: later experiment
- why: important for the future local model and council path
- current use: not yet a routing layer inside this repo

## Use-Only / Optional Utility

### career-ops
- status: optional utility and pattern source
- why: strong reference for internship and job-search operations
- current use: pattern source, not core runtime code

### pi-mono / seomachine / thepopebot / RedditVideoMakerBot
- status: optional utility only
- why: each may contain narrow reusable ideas, but none should shape the main architecture
- current use: side reference at most

### awesome-claude-code
- status: optional utility
- why: useful for prompts, tips, and operating patterns around Claude Code
- current use: documentation-style reference only

## Not Foundation

### Leak / Extraction Repos
- status: excluded from foundation
- why: provenance, malware, and maintenance risk
- rule: if reviewed at all, keep quarantined and reference-only

### Abuse-Oriented Automation
- status: excluded
- why: conflicts with the project direction toward legitimate, approval-based owned-account workflows

### Unrelated Side Tools
- status: excluded from core architecture
- why: they may still be useful elsewhere, but they should not distort the operator foundation

## Practical Rule
- Only this repo is core.
- Third-party repos are for patterns, evaluation, and narrow justified extraction.
- Nothing should be described as integrated unless it is actually wired into the runtime, dashboard, or checkers here.
