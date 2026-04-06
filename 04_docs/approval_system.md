# Minimum Approval System

## Purpose

Risky actions require explicit human approval.

## Default Mode

Ask first.

## Approval Levels

- `safe`
- `ask`
- `high_risk`

## Safe Examples

- Read files
- Summarize context files
- Search within workspace
- Propose plans

## Ask Examples

- Create files
- Edit files
- Multi-file changes
- Git commits
- Git pushes
- Package installs
- External integrations

## High Risk Examples

- Destructive deletes
- Secret or token changes
- Mass rewrites
- Remote automation on external accounts

## Required Approval Request Fields

- Action
- Reason
- Scope
- Affected files
- Rollback plan

## Rule

When uncertain, ask.
