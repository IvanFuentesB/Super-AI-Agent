# Browser And App Control Architecture

## Future Flow

planner -> approval gate -> executor -> observation loop -> audit log -> kill switch

## Boundaries

- planning-only and real execution must stay distinct
- execution should target the user's own systems and accounts only
- dangerous actions should require approval and logging

## Current Reality

- browser and app control are not implemented yet
- current runtime only supports planning and local file-backed scaffolding
