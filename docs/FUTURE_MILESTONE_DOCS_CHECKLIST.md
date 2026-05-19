# Future Milestone Docs Checklist

Every future milestone that changes public-facing capability should update docs in the same branch.

## Required Updates

- README capability section
- README limitations section
- README roadmap section
- SECURITY.md if the risk posture changes
- CONTRIBUTING.md if contributor rules change
- `docs/DIAGRAM_UPDATE_RULE.md` if diagrams gain new surfaces
- `docs/PUBLIC_RELEASE_SECURITY_CHECKLIST.md` if the release gate changes
- latest milestone report under `14_context/`

## Capability Truth

Future docs must say whether the feature is:

- planning-only
- static inspection only
- dry-run only
- local artifact generation
- approval-gated local action
- live external action

Live external action remains out of scope until a later explicit audited milestone.
