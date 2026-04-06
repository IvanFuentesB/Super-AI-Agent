# Operator Mode Plan

## Purpose

Operator mode should feel like a clear local control surface for safe actions, not a page full of raw tool output.

## What Operator Mode Should Feel Like

- obvious about what the user can do right now
- visible and inspectable
- local-first in execution surface, not hidden behind background behavior
- explicit about what is live, what is scaffold-only, and what does not exist yet

## Current Operator Capabilities

- read current capability summary
- read GitHub repo status and remote-capability readiness
- generate internship, showcase, and portfolio scaffolds
- trigger the local browser smoke demo
- trigger the local visible browser demo
- review recent artifacts and recent actions

## Current Limits

- no browser executor loop
- no approval queue UI
- no native desktop or Windows app control
- no live mail, Notion, or LinkedIn adapters
- no remote control surface

## Important Distinctions

- local visible browser demo: opens Chromium locally, runs one deterministic click path, and proves visible browser automation
- browser executor: would need a broader observation loop, recovery logic, and stronger approval boundaries
- full desktop or app control: would require Windows-specific control layers, stronger safety constraints, and a clearer kill-switch path

## What Should Come Next

1. manually test the cleaned-up dashboard as an operator surface
2. decide the next executor path instead of expanding in multiple directions at once
3. improve approval and action-history visibility in the dashboard
4. only then move toward a richer browser executor or desktop-control playground
