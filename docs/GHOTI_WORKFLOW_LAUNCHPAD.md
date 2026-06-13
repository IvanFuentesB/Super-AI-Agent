# Ghoti Workflow Launchpad -- Templates, Roles, and Task Waves

**Status:** Working local MVP (all workflows are suggestion_only)
**Source of truth:** `03_scripts/agent_os/workflow_templates.py`

---

## Summary

The Agent OS ships 7 workflow templates and a 6-role roster. A template is
pure data: goal, roles, ordered steps with owned path prefixes, deliverables,
and an explicit `wont_do` line. Planning a workflow renders an ASCII plan
packet and a deterministic task-wave preview; nothing is executed. Templates
generate plans, checklists, and drafts only - they do NOT post, buy, send, or
control a browser, and every role runs in `suggestion_only` mode.

## The 7 workflow templates

| Id | Goal | Roles | Will not do |
|----|------|-------|-------------|
| `coding-task` | Ship one small, tested code change on a feature branch | planner, coder, auditor | No pushes, merges, or edits outside the planned file ownership |
| `repo-audit` | Produce an honest repo health and risk report | auditor, operator | No fixes applied; findings only |
| `content-video` | Draft a video idea package ready for human review | researcher, content, planner | No posting, no uploads, no account access; drafts only |
| `business-research` | Draft a research plan for one online-business hypothesis | researcher, planner | No purchases, no signups, no live market scraping |
| `email-draft` | Produce a reviewed email draft the human sends manually | content, auditor | No account access, no sending, no contact scraping |
| `automation-n8n` | Design one automation flow on paper before any wiring | planner, operator | No live workflow creation, no credentials, no external calls |
| `computer-use-prep` | Verify every precondition for future supervised computer-use | operator, auditor | No mouse/keyboard control, no browser automation, observation only |

### Steps and deliverables per template

- **coding-task**: planner writes the task brief (goal, files, success
  criteria); coder implements the change plus a focused test; auditor reviews
  the diff against the brief. Deliverables: task brief, implementation
  handoff packet, audit checklist.
- **repo-audit**: operator collects status (git, tests, audit, locks);
  auditor ranks risks and unverified claims. Deliverable: repo audit report
  draft.
- **content-video**: researcher pulls context from memory and lists 5 idea
  candidates; content drafts a script outline plus 5 title variants for the
  top idea; planner assembles the manual publish checklist (a human does
  every live step). Deliverables: idea list, script draft, title variants,
  manual publish checklist.
- **business-research**: planner defines the hypothesis and success
  criteria; researcher drafts research questions and a source checklist for
  the human. Deliverables: hypothesis brief, research checklist.
- **email-draft**: content drafts the email body from the stated intent;
  auditor checks tone, claims, and recipients and flags risks. Deliverables:
  email draft, send checklist.
- **automation-n8n**: planner describes trigger, steps, data in/out, and
  failure modes; operator lists required approval gates and manual setup
  steps. Deliverables: automation flow design, approval gate list.
- **computer-use-prep**: operator checks adapter dry-run, policy checker,
  and feature flags; auditor confirms every live-action path is still
  blocked. Deliverable: computer-use precondition checklist.

## The 6-role roster

Roles map to lanes in `14_context/agent_lanes/agent_lane_registry.json`.
Every role is `suggestion_only` in this milestone.

| Role | Mission | Lane (`lane_ref`) |
|------|---------|-------------------|
| Planner | Turn goals into small, verifiable task waves with clear file ownership | `chatgpt_strategy` |
| Coder | Implement one approved task at a time on a feature branch | `claude_code_impl` |
| Auditor | Adversarially verify finished work before it is merged | `codex_audit` |
| Researcher | Collect local context and draft research plans for human-run searches | `gemma_local_worker` |
| Content | Draft scripts, titles, and checklists; humans publish manually | `gemma_local_worker` |
| Operator | Run safe local recipes/checks and keep the evidence trail honest | `python_automation_worker` |

## Task waves

```bash
python 03_scripts/agent_os/ghoti_agent_os.py --task-wave coding-task --json
```

A task wave groups template steps deterministically so that no two tasks in
the same wave share a role or an owned path prefix. The result is a preview
(`simulation_only: true` in the JSON): wave count, task count, and per-wave
task lists with owned paths. It tells you what could run in parallel if the
plan were executed by human-driven lanes; it launches nothing.

## Ownership verification

```bash
python 03_scripts/agent_os/ghoti_agent_os.py --ownership-check --json
# or with a custom repo-local wave file:
python 03_scripts/agent_os/ghoti_agent_os.py --ownership-check --wave-input <repo-local.json> --json
```

The check flags any path prefix two agents share. When the Rust binary is
built (`rust/ghoti_policy_checker`, invoked with `--ownership-input
<wave.json>`), it produces the verdict and the JSON records
`rust_checker_used: true`; otherwise a Python mirror applies the same
prefix-overlap rule. The default input is one assignment set per roster role
derived from every template step, and the self-check suite proves both that
a deliberate overlap is caught and that the default wave has none.

## Policy gating

Every template declares its capabilities (subsets of `repo_read`,
`status_read`, `plan_render`, `local_policy_check`,
`report_write_repo_local`). Before a plan or worker suggestion is written,
the capabilities pass through the deny-by-default operator recipe policy
(`23_configs/operator_recipe_policy.example.json`). A template asking for a
blocked capability would be refused, and the gate fails closed if the policy
module cannot load.

## Be explicit about the boundary

Templates generate plans, checklists, and drafts. They do NOT post, buy,
send, upload, sign in, scrape, or control a browser. The deliverable of
every workflow is a file a human reads; the live step - merging code,
publishing a video, sending an email, wiring an automation - is always
performed manually by the human operator.
