# Ghoti Agent Skills Setup

How to set up skills for the four agents in the Ghoti stack: Claude Code, Codex,
Hermes, and ChatGPT / Cowork. Skills are reusable discipline or capability
bundles. Some are already part of this repo's workflow; others need a manual
install with a confirmed canonical source.

## Two kinds of skills

- `available_in_repo_workflow` (`manual_required: false`): already part of this
  repo's prompting/discipline. Use them directly in agent prompts. No install
  step. Examples: karpathy-guidelines, context-engineering, verification-loop,
  incremental-implementation, search-first/source-driven-development,
  code-review-security, mcp-builder, skill-creator (Claude Code);
  security-review, rust-guard-audit, merge-gate, repo-intake-audit (Codex).
- `manual_install_documented` (`manual_required: true`): external skills that
  need a confirmed source before install. Treat the canonical source as
  unverified until checked. Examples: superclaude, bmad, archon,
  claude-task-master, claude-mem, hooks-mastery, ccstatusline, claudekit,
  official-anthropic-skills-repo, and all Hermes / ChatGPT-Cowork entries.

## Do NOT overwrite user or global skill folders

Never overwrite or clobber a user's global / personal skill directories. Install
external skills into a project-scoped or explicitly chosen location, by the
human, after confirming the canonical source. The skills registry records status
only; listing a skill never installs it.

## Per-agent lists

- Overview and division of work: `14_context/agent_skills/agent_skill_roadmap.md`
- Claude Code: `14_context/agent_skills/claude_code_skills.md`
- Codex: `14_context/agent_skills/codex_skills.md`
- Hermes: `14_context/agent_skills/hermes_skills.md`
- ChatGPT / Cowork (artifact specs): `14_context/agent_skills/chatgpt_cowork_artifacts.md`

## Status source of truth

- Registry: `14_context/tool_stack/skills_registry.json`
  (per-agent entries with `manual_required`, `status`, `enabled`, `next_action`).
- Skills awaiting manual install vs already in workflow:
  `14_context/tool_intake/skills_queue.md`
- Regenerate the registry:
  `python 03_scripts/tool_stack/ghoti_tool_stack.py --write-skills-templates`

## Manual install workflow (for manual_required skills)

1. Confirm the canonical source/URL (do not assume; many names collide).
2. Run the source through repo intake first if it is a repo
   (`docs/GHOTI_REPO_INTAKE_SAFETY.md`).
3. Install into a project-scoped location chosen by the human. Do not touch
   global/user skill folders.
4. Update `status` and `enabled` in `skills_registry.json` only after a
   successful, reviewed install.
