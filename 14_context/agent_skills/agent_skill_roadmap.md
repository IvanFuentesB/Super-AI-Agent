# Agent Skill Roadmap

Overview of how the four Ghoti agents divide skills. Status of each skill lives
in `14_context/tool_stack/skills_registry.json`; setup steps are in
`docs/GHOTI_AGENT_SKILLS_SETUP.md`.

## The four agents

| Agent | Role | Skill focus | Executes? |
|-------|------|-------------|-----------|
| Claude Code | Primary builder | Discipline + build/review/skill tooling | Yes (in repo, gated) |
| Codex | Auditor / second pass | Security, audit, merge-gate, token saving | Review-oriented |
| Hermes | Local coordinator | Status, memory, handoff summaries | No execution |
| ChatGPT / Cowork | Dashboards / artifacts | Artifact specs, connector views | No live integrations |

## Division of work

- Claude Code builds first: it carries the largest skill set (discipline skills
  already in workflow plus build/review/skill-creation tooling, several of which
  are manual-install candidates pending source confirmation).
- Codex audits second: a focused set centered on security review, rust guard
  audit, merge-gate, repo-intake audit, and token-saving discipline.
- Hermes coordinates locally and reads only: it summarizes status, compresses
  memory, and produces handoffs. No execution.
- ChatGPT / Cowork renders dashboards as artifact specs (Morning Dashboard,
  Ghoti Command Dashboard, connector views). These are specifications, not live
  integrations.

## Per-agent lists

- Claude Code: `claude_code_skills.md`
- Codex: `codex_skills.md`
- Hermes: `hermes_skills.md`
- ChatGPT / Cowork: `chatgpt_cowork_artifacts.md`

## Status legend

- `available_in_repo_workflow` (`manual_required: false`): use directly.
- `manual_install_documented` (`manual_required: true`): confirm canonical
  source, intake-first if a repo, then install into a project-scoped location.
  Never overwrite global/user skill folders.
