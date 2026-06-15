# Ghoti ChatGPT / Cowork Productivity Setup

ChatGPT/Cowork is the strategy, architecture, human-facing dashboard/artifact,
and routine-design lane. Use:

- `23_configs/assistant_productivity/chatgpt_cowork_productivity.example.json`
- `14_context/assistant_productivity/chatgpt_cowork_ready_prompts.md`

The Morning Dashboard artifact remains useful as a compact daily view. The
future Ghoti Command Dashboard should combine repo status, tool-stack status,
open PRs, approvals, handoffs, and top actions without becoming a live control
surface.

Operator-reported Cowork connectors are Gmail, Google Calendar, and Figma.
Ghoti records them as disabled in its runtime and limits proposed use to
read/draft/propose modes. Desired future views are GitHub, Notion, Ghoti status,
tool-stack status, and PR status. No connector credentials belong in the repo.

ChatGPT handles strategy and polished artifacts; Claude Code implements; Codex
audits; Hermes compresses status and memory; the human approves risky actions.
