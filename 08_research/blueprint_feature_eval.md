# Blueprint Feature Eval

## Classification
- Blueprint.am / Blueprint is a reference pattern and optional external inspiration.
- It is not a core dependency for Ghoti.
- It should not be treated as a required hosted service, pricing dependency, or integration foundation.

## What Looks Potentially Useful
- Hardware-project idea decomposition from plain-language prompts.
- Early BOM / parts suggestion workflows.
- Wiring or connection-planning assistance.
- Build or assembly-step generation.
- Firmware or setup checklist generation.
- Test and validation checklist generation.

## What Is Still Unknown
- Public API availability.
- Pricing, credits, and rate limits.
- Export formats and whether usable structured exports exist.
- Reliability for real electrical, firmware, or manufacturing work.
- Whether the product is stable enough to build against.
- Whether it supports direct workflow integration or is mainly a hosted UI.

## Practical Repo Position
- Keep Blueprint.am in research and integration-mapping only.
- Do not wire core runtime, supervisor, or desktop flows to it.
- If it is explored later, keep it isolated under research or experiments first.

## Internal Capability Idea We Can Build Ourselves Later
A future local-first hardware-project-assist module could help with:
- prompt -> structured hardware project spec
- project spec -> BOM draft
- project spec -> wiring / connection table
- project spec -> assembly checklist
- project spec -> firmware / setup checklist
- project spec -> validation / test checklist
- exportable markdown docs inside `C:\Users\ai_sandbox\Documents\AI_Managed_Only`

## Narrowest Realistic Internal V1
- Input:
  a single markdown or form-based project brief
- Output:
  - `project_spec.md`
  - `bom_draft.md`
  - `wiring_table.md`
  - `assembly_checklist.md`
  - `validation_checklist.md`
- Scope:
  guidance and structured drafting only, not automatic CAD or PCB generation

## Why Raw Blueprint Dependence Would Be A Mistake
- Hardware mistakes are more expensive than software mistakes.
- Hosted AI product scope can change quickly.
- Credits, pricing, or export restrictions could break a workflow later.
- The current Ghoti priority is supervised local operator control, not a hosted hardware-design dependency.

## Recommendation
- Treat Blueprint.am as inspiration for a later hardware-builder-assist module.
- Build any real dependency-free capability ourselves inside the managed workspace if and when hardware-project support becomes a priority.
