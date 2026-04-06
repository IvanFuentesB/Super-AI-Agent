# AI Council Architecture

## What An AI Council Means Here

An AI council in this project is a planning layer that assigns different model roles to the same task instead of treating one model as the whole system.

## Core Roles

- lead: primary planner or drafter for the task
- reviewer: second-pass checker for quality, risk, or clarity
- executor: the layer that turns the plan into files, commands, and Git changes
- local fallback: a local model profile used when privacy, speed, or availability favors local execution

## When To Prefer Local Vs Cloud

- prefer local when privacy is stricter, drafts are lightweight, or a fast local fallback is enough
- prefer cloud when cross-domain planning, heavier synthesis, or stronger review quality is more important

## Routing Examples By Task Type

- coding: lead with a strong coding model, reviewer for risk and regression checks, local fallback when privacy matters
- planning: lead with a planning-heavy model, optional reviewer for important decisions
- structured docs: lead with a writing or structure-heavy model, reviewer for clarity
- research synthesis: lead with a synthesis-heavy model, reviewer for grounding and gaps
- content ideation: lead with a creative planning model, reviewer for tone, legitimacy, and business fit

## Why This Layer Exists

This layer exists so routing decisions are explicit, inspectable, and file-backed instead of hidden in ad hoc prompts.

## What Is Not Implemented Yet

- no live provider APIs
- no automatic model routing engine
- no real multi-model execution loop
- no browser or app integrations
