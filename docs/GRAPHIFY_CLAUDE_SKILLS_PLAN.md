# Graphify And Claude Skills Plan

## Graphify

Graphify is a candidate for token-efficient knowledge graph extraction. It is
not installed, executed, or runtime-wired in this milestone.

Evaluation goals:

- represent repo knowledge as compact nodes/edges
- cache source intelligence packets
- reduce repeated premium-model context
- feed local worker summaries into Codex/Claude audit packets

## Claude Skills

Claude skills must be detected before use. Do not assume a skill exists because
a prompt mentions it.

Current plan:

- detect expected skills/rules
- document missing skills
- recover/register skills later if local and safe
- do not install external skill packs in this milestone
