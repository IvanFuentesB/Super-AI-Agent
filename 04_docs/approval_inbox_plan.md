# Approval Inbox Plan

## Purpose

The approval inbox is the local review surface for actions that should not continue silently.

## Approval Request Fields

- approval id
- related task id
- action label
- reason
- risk level
- status
- source
- scope
- rollback plan
- admin-required flag
- requested time
- updated time
- human note

## Risk Levels

- `safe`: no approval required
- `ask`: normal explicit review required
- `high_risk`: stronger review required before proceeding
- `admin`: human must handle or explicitly approve any admin-like step

## Approval Statuses

- `pending`
- `approved`
- `denied`
- `deferred`
- `expired`

## When Approval Is Required

- remote GitHub write actions
- uncertain terminal commands
- package or environment changes with unclear impact
- actions that may touch external accounts or remote state

## Admin-Required Situations

- actions that would need elevated shell behavior
- machine-wide changes
- system configuration changes
- anything that would be risky to run silently even on the local machine

## Inbox Rule

If the task is uncertain, risky, or admin-like, it should become a visible approval request instead of continuing automatically.
