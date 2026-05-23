# Future Milestone Docs Checklist

Every future milestone that changes public-facing capability should update docs
in the same branch.

## Required Updates

- README capability section
- README limitations section
- README roadmap section
- SECURITY.md if risk posture changes
- CONTRIBUTING.md if contributor rules change
- Hermes/provider docs if model routing changes
- Public release checklist if the release gate changes
- Latest milestone report under `14_context/`

## Capability Truth

Future docs must say whether a feature is:

- planning-only
- local bootstrap only
- static inspection only
- dry-run only
- local artifact generation
- approval-gated local action
- live external action

Live external action remains out of scope until a later explicit audited
milestone.
