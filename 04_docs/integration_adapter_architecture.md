# Integration Adapter Architecture

## Why Adapters Exist

Adapters keep provider- and service-specific logic out of the core runtime. They make capability boundaries, approval requirements, and execution modes explicit instead of burying them inside one-off commands.

## Live Vs Planning-Only

- live adapter: can read from or act against a real system
- planning-only adapter: produces plans, summaries, or draft packs without touching the live system

## Approval Gating

- read-only actions can be allowed first
- write, send, or publish actions should require explicit approval
- approval rules should stay separate from adapter logic

## Intended Adapter Classes

- GitHub
- mail
- Notion
- LinkedIn later

## Current Order

1. GitHub live read-only
2. mail planning
3. Notion planning
4. LinkedIn planning later

## Separate Later Layer

Browser and app executors are still a separate later layer, not part of this first adapter foundation.
