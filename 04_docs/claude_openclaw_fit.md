# Claude Code And OpenClaw Fit

## Official Claude Code

The official `anthropics/claude-code` repo is cleaner reference material than leaked or snapshot-style claw repos because it is maintained by the vendor, points to current documentation, includes supported install paths, and documents plugins openly.

## Why It Matters Here

- useful reference for terminal agent UX
- useful reference for plugin and command structure
- useful reference for supported installation and operator workflow patterns

## OpenClaw

`openclaw/openclaw` is interesting as a much broader control-plane example with onboarding, channels, browser control, skills, and remote gateway ideas, but it is a far larger product than this repo needs right now.

## Likely Later Fit

- Claude Code: reference for operator experience, plugin concepts, and documentation quality
- OpenClaw: reference for control-plane ideas, browser concepts, and permission or remote-access patterns

## Reference Only For Now

- both repos stay intake material, not core code
- `awesome-claude-code` stays a discovery list, not a dependency
- no direct vendor fusion into the runtime MVP

## What To Adapt Carefully

- explicit command surfaces
- approval and confirmation ideas
- plugin or skill organization
- documentation and operator ergonomics

## What Not To Copy Blindly

- vendor-specific assumptions
- large runtime surfaces that exceed current scope
- channel-heavy personal assistant behavior that does not match this repo's owned-workflow focus
- any architecture that weakens inspectability or approval control
