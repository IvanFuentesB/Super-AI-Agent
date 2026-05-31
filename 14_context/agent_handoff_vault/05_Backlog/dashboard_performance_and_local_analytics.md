# Backlog — Dashboard Performance and Local Analytics

Milestone where noted: N+6.4A
Date: 2026-05-31
Status: BACKLOG ONLY — documented direction, not built in this milestone.

This note records a desired product direction so it is not lost. Nothing here is
implemented yet. No analytics system is built, wired, or enabled by this note.

## Direction 1 — Dashboard should feel fast and reliable

The Ghoti dashboard / UI should eventually feel extremely fast, reliable, and
low-friction. The target feel is industrial / utility-grade: instant, predictable
navigation — not a flashy, slow web app. Speed and reliability are the product.

Qualities to aim for (future work, not built here):

- Fast, predictable view/page transitions.
- Low input-to-response latency for common actions.
- Reliable behavior under repeated use; no surprising slow paths.
- Minimal visual noise; utility over decoration.

## Direction 2 — Local-first product analytics (future)

If/when analytics are added, they must be local-first and privacy-preserving.
Candidate metrics to consider measuring **locally** later:

- Page / view transition events and timing.
- Feature usage counts.
- Command usage counts.
- Task completion counts and task failure counts.
- Latency / performance timing for key actions.
- Error counts.
- Local dashboard reliability metrics.

## Hard constraints for any future analytics

- No external tracking by default.
- No user secrets collected.
- No invasive telemetry.
- No analytics leaving the machine without explicit human approval.
- Local-first storage only; opt-in, inspectable, and reversible.

## Why this is backlog-only now

Per the N+6.4A milestone, this direction is documented but intentionally not
built. Adding an analytics system now would exceed the milestone's scope
(register current truth + skills workflow). Building it later requires its own
milestone with a safety review and explicit human approval.
