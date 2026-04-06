# GitHub Remote Smoke Tests

## Purpose

Remote smoke tests prove that explicit, approval-gated GitHub mutations can run in the real environment instead of only existing as local scaffolding.

## Local Drafts vs Remote Mutation

- local draft generation writes markdown under `11_exports/github/`
- remote smoke tests create real GitHub artifacts and must stay explicit

## Safe Scope

- create one clearly labeled test issue
- create one clearly labeled test PR only if a safe branch and review context already exist

## Rules

- explicit approval is required before any remote smoke action
- smoke titles should use an obvious test prefix such as `[SMOKE TEST]`
- checker runs should stay non-mutating by default
- test artifacts should be cleaned up manually after review

## Current Default

- remote smoke issue creation is the safer first path
- remote smoke PR creation remains more limited and should be used sparingly
