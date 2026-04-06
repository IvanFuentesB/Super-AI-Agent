# Git Workflow

## Main Branch Purpose

`main` is the stable foundation branch for the current working system.

## When To Stay On Main

Stay on `main` for small documentation updates, context refreshes, and low-risk changes that keep the current foundation coherent.

## When To Create A Branch

Create a branch for features, fixes, experiments, or any change that is large enough to review separately or might need rollback on its own.

## Branch Naming

- `feat/<name>`
- `fix/<name>`
- `docs/<name>`
- `chore/<name>`
- `exp/<name>`

## When To Commit

Commit when a small, coherent step is complete and the change can be described clearly in one message.

## When To Push

Push after a useful checkpoint is committed, especially when the branch should be backed up or shared across tools and sessions.

## When To Tag Versions

Do not tag every checkpoint. Tag only when a meaningful baseline is stable and worth returning to.

## Current Tag Policy

- No version tag yet
- The first intended foundation tag is `v0.1.0` after the base workflow is stable
