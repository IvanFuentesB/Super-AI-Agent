# UI-TARS - Static Intake Report (N+6.12A)

**Priority:** high (named computer-use stack candidate)
**Source:** **not recorded** (confidence: ambiguous)
**Local clone:** none | **cloned:** false
**License:** unknown | **static_inspected:** false
**safe_to_run:** false | **runtime_wired:** false
**Status:** `source_needed`

## Why this is a source-needed report, not a clone

The committed repo references UI-TARS only as "intake/planning only" (e.g. the
N+4.1F and N+5.0A observation work). No exact clone URL is recorded, and there are
multiple distinct upstream projects under the UI-TARS name (a model vs. a desktop
app vs. SDKs). The mission rule is explicit: **do not guess** which upstream is
intended. So UI-TARS is documented here and **not** cloned from a guessed URL.

## Useful patterns (from prior planning notes, not from a clone)

1. Vision-language GUI grounding - parse a screenshot into elements/actions.
2. Observation-only screen parsing, which aligns with the existing N+5.0A
   observation adapter and the N+6.5A observation harness.

## Risks

- Desktop control if ever run; large model weights; live API.
- Ambiguous source - cloning the wrong repo would be a real mistake.

## First safe next test

The operator supplies the exact source URL. Then: static clone + license/README
inspection only, **no** runtime, **no** model download, **no** desktop control.

## License / terms

`license_or_terms_check_needed: true` - cannot be assessed until the exact upstream
is identified.
