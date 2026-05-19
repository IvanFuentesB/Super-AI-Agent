# Diagram Update Rule

Public diagrams must stay aligned with real audited capability.

## Rules

- Do not show UI-TARS click, type, hotkey, or desktop control as enabled.
- Do not show external repo runtime wiring unless a later audited milestone enables it.
- Do not show live account actions, posting, uploading, trading, or money movement.
- Keep approval gates visible in every workflow that could become risky.
- If README diagrams change, update `docs/assets/github/README.md` and the latest audit report in the same branch.
- If a diagram uses an imported image, verify the raw source remains ignored and the copied filename is sanitized.

## Review Prompt

Before publishing a diagram, ask: "Could a reader reasonably think Ghoti can perform a risky action that is not actually audited and enabled?" If yes, revise it.
