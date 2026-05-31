# Ghoti Skill Registry

Milestone: N+6.4A
Date: 2026-05-31

A registry of skills known to Ghoti's agents and their current enablement
status. "Status" describes how a skill may be used today, not a promise of
automation. Anything marked NOT enabled must not be claimed as working.

## Status legend

- guidance-only — a playbook/checklist that shapes how work is done; no runtime
  execution, no live actions.
- manual — a documented recipe a human or coordinator runs by hand.
- NOT enabled — visible somewhere (for example in a tool list) but not approved
  and not turned on for Ghoti.

## Ghoti-owned local skills

| Skill | Type | Status |
|-------|------|--------|
| goal | repo playbook | manual |
| ultraplan | repo playbook | manual |
| ghoti-status | repo playbook | manual |
| prompt-bus | repo playbook | manual |

## External / adopted guidance skills

| Skill | Source | Status |
|-------|--------|--------|
| karpathy-guidelines | Anthropic skill (Karpathy anti-pitfall principles) | guidance-only (intake: `karpathy_guidelines_intake.md`) |

## Hermes-visible tools (informational)

These names may appear in `hermes skills list`. Their presence is not
enablement. For Ghoti:

| Tool | Status for Ghoti |
|------|------------------|
| codex | manual (audit role; not auto-wired) |
| claude-code | manual (implementation role; not auto-wired) |
| hermes-agent | local coordinator (llama3.1:8b) |
| memory | manual (vault-backed notes) |
| obsidian | manual (durable shared memory) |
| github | manual (human-approved git/push only) |
| plan | guidance-only |
| test-driven-development | guidance-only |
| mcp | NOT enabled for Ghoti |
| browser | NOT enabled for Ghoti (no click/type/screen control) |
| computer-use | NOT enabled for Ghoti (no desktop control) |

## Rules

- A skill changes how work is documented or shaped; it does not grant new
  permissions.
- External skills are inspected before adoption and stay guidance-only unless a
  separate, human-approved milestone wires them in.
- browser, computer-use, mcp, and Telegram are not enabled here.
