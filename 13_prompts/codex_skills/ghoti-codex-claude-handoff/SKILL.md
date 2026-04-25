# ghoti-codex-claude-handoff

**Status:** skill_package_created / not_runtime_wired
**Bridge truth:** manual_handoff_only
**Created:** 2026-04-25
**Branch:** feat/ghoti-visible-operator-stack

---

## Purpose

Keep ChatGPT, Codex app, Claude chat, and Claude Code handoffs precise, safe, and honest.

This skill documents the manual handoff workflow for Ghoti / Super-AI-Agent. It does not create or claim an automatic Claude Code <-> Codex bridge. It does not wire Codex plugins, Claude skills, or Claude Code into Ghoti runtime.

---

## When to Use

Use this skill when preparing:

- A Claude Code execution prompt.
- A Codex app execution/review prompt.
- A Claude chat reasoning prompt.
- A new ChatGPT thread handoff.
- A finish-line handoff after a milestone.
- A recovery prompt after Claude Code auth, quota, context, or prompt-file issues.

Use it any time the operator needs to move work between human chat, Codex app, Claude chat, and Claude Code without overclaiming automation.

---

## Forbidden Uses

- Claiming an automatic Claude Code <-> Codex bridge exists.
- Claiming Codex plugins/skills are wired into Ghoti runtime unless repo code proves it.
- Launching Claude Code after prompt-file copy/check failure.
- Using stale `14_context/ghoti_current_prompt.md` without confirming it was just copied for the current task.
- Treating a Claude Code prompt file as approval for broad autonomous work.
- Autonomous code execution beyond the approved repo task.
- Using paid/cloud integrations without explicit approval.
- Deploying, connecting external services, or adding secrets.
- Unsafe, spam, fake engagement, cap/quota bypass, money movement, legal filing, weapon guidance, or unauthorized scraping workflows.
- Staging `.claude/skills/`, runtime data, output artifacts, third-party repo contents, CV files, or prompt scratch files unless explicitly required.

---

## Required Manual Handoff Workflow

1. Identify the target operator surface:

- ChatGPT: architecture, memory, synthesis, next prompt creation.
- Codex app: repo execution, auditing, edits, tests, commits, pushes when approved.
- Claude chat: reasoning, critique, prompt sharpening, strategy.
- Claude Code: terminal/repo execution from one prepared prompt file.

2. State the bridge truth in every handoff:

```text
Claude Code <-> Codex automatic bridge: manual_handoff_only.
Codex plugins/skills are session/operator capabilities, not Ghoti runtime wiring unless proven.
```

3. Include model/mode guidance.
4. Include repo truth and dirty-file rules.
5. Include exact files to read first.
6. Include exact files allowed to edit.
7. Include exact files not to stage.
8. Include validation commands.
9. Include final report format.

---

## Required Model / Mode Section Rules

Every prompt must state recommended model and effort/mode.

Examples:

```text
Recommended Claude Code model/effort:
- Model: sonnet
- Effort: high
- Permission mode: bypassPermissions only when explicitly approved for repo-local work
```

```text
Recommended Codex mode:
- Use current Codex app session
- High effort for repo edits; medium effort for read-only audit
- No deployment or external service connection
```

```text
Recommended Claude chat mode:
- Use for reasoning, critique, and prompt sharpening
- Do not represent Claude chat as executing repo changes
```

If the model is uncertain, say so. Do not pretend a specific model is available if it has not been confirmed.

---

## Required Prompt-File Rules For Claude Code

Claude Code execution prompts get exactly one downloadable file named:

```text
ghoti_current_prompt.md
```

The operator should copy that downloaded file to:

```text
14_context\ghoti_current_prompt.md
```

Claude Code prompts must include exact PowerShell commands and exact paste text.

Required PowerShell sequence:

```powershell
cd C:\Users\ai_sandbox\Documents\AI_Managed_Only

if (!(Test-Path "14_context\ghoti_current_prompt.md")) {
  Write-Error "Missing 14_context\ghoti_current_prompt.md. Stop before launching Claude Code."
  exit 1
}

Get-Item "14_context\ghoti_current_prompt.md" | Select-Object FullName,Length,LastWriteTime
Get-Content "14_context\ghoti_current_prompt.md" -TotalCount 20
```

Only after confirming the prompt file was just copied for the current task, launch Claude Code:

```powershell
claude --model sonnet --effort high --permission-mode bypassPermissions
```

Exact paste text for Claude Code:

```text
Read and execute the task in:
C:\Users\ai_sandbox\Documents\AI_Managed_Only\14_context\ghoti_current_prompt.md

Stay inside repo root. Do not stage blocked/local files. Do not push unless the prompt explicitly tells you to push.
```

If the prompt source file is missing, stale, or fails the `Get-Item` / `Get-Content` checks, stop before launching Claude Code.

---

## Required Plain-Text Rules For Codex

Codex prompts are plain copy-paste text only.

Do not require a downloadable file for Codex. Include all required context in the prompt:

- Repo root.
- Branch.
- Latest pushed commit.
- Exact task.
- Files to inspect first.
- Allowed files to edit.
- Blocked files.
- Validation commands.
- Commit/push instructions.
- Final report format.

Codex should directly inspect the repo, edit needed files, validate, commit, and push only if the prompt explicitly requests that.

---

## Required Plain-Text Rules For Claude Chat

Claude chat prompts are plain copy-paste text only.

Use Claude chat for:

- Reasoning.
- Architecture critique.
- Prompt sharpening.
- Risk review.
- Planning.

Do not ask Claude chat to claim it changed repo files. If Claude chat suggests implementation, route execution through Codex app or Claude Code with a clear manual handoff.

---

## Required Plain-Text Rules For New ChatGPT Handoffs

New ChatGPT thread handoffs are full detailed plain copy-paste text only.

Include:

- Repo root.
- Branch.
- Latest pushed commit.
- Current milestone state.
- What is real.
- What is scaffold.
- Dirty files intentionally left unstaged.
- Exact next requested action.
- Safety constraints.

Do not depend on hidden memory for critical repo state.

---

## Required Downloadable-File Rule For Claude Code Only

Only Claude Code gets a downloadable prompt file.

Rules:

- File name must be exactly `ghoti_current_prompt.md`.
- The file must be copied into `14_context\ghoti_current_prompt.md`.
- The operator must verify file exists, size is plausible, and timestamp matches the current task.
- The prompt file should not be staged unless a later milestone explicitly says to commit it.
- Codex, Claude chat, and ChatGPT handoffs remain plain copy-paste text.

---

## Required Repo Truth Section

Every handoff prompt must include:

```text
Repo root: C:\Users\ai_sandbox\Documents\AI_Managed_Only
GitHub: IvanFuentesB/Super-AI-Agent
Branch: feat/ghoti-visible-operator-stack
Latest confirmed pushed commit: <hash and message>
Dirty/local-only files not to stage:
- 21_repos/third_party/.gitkeep
- .claude/skills/
- 01_projects/mcp_server/test.txt
- 14_context/ghoti_current_prompt_N1_6.md
- CV .docx files
- output/
- runtime data and screenshot artifacts
- local temp/probe files
```

If the current commit or branch is unknown, require the executor to run:

```powershell
git status --short
git branch --show-current
git log --oneline -5
git log --oneline origin/feat/ghoti-visible-operator-stack -5
git diff --cached --name-status
```

---

## Required Safety / Truth Labels

Use these labels when applicable:

- `manual_handoff_only`
- `skill_package_created / not_runtime_wired`
- `strategy_only / not_runtime_wired`
- `scaffold_only`
- `diagnostic_only`
- `local_only`
- `approval_gated`
- `not_implemented`
- `unproven`
- `blocked`

Preserve these truths:

- Ghoti is not autonomous yet.
- Claude Code <-> Codex automatic bridge is `manual_handoff_only`.
- Codex skills/plugins are session/operator capabilities, not Ghoti runtime integrations unless proven.
- OpenClaw is reference/prep only, not wired into Ghoti runtime.
- Gemma/Ollama is diagnostic/status only and does not drive the operator.
- Browser overlay is browser-based, not native always-on-top.
- Capture gallery means local screenshot frames saved on this machine, not AI screen sharing.

---

## Recovery: Prompt File Missing Or Stale

If `14_context\ghoti_current_prompt.md` is missing:

1. Stop.
2. Do not launch Claude Code.
3. Ask the operator to copy the current downloadable `ghoti_current_prompt.md` into `14_context\ghoti_current_prompt.md`.
4. Re-run `Get-Item` and `Get-Content` checks.

If the file exists but appears stale:

1. Stop.
2. Compare LastWriteTime, first lines, branch, milestone, and latest commit.
3. Do not use the stale file.
4. Ask the operator to replace it with the current task prompt.

If the file path is correct but contents are wrong:

1. Stop.
2. Do not launch Claude Code.
3. Regenerate or recopy the prompt file.

---

## Recovery: Claude Code Auth Fails

If Claude Code shows `401`, `authentication_error`, login failure, or quota/auth-related startup failure:

1. Stop execution.
2. Do not ask Claude Code to continue the task.
3. Run `/login` inside Claude Code if the interface is available.
4. If `/login` does not work, exit Claude Code and re-authenticate manually.
5. Return to ChatGPT/Codex with exact error text.
6. Do not attempt cap/quota bypass.

---

## Required Final Report Format

Final handoff/work reports should include:

```markdown
- target surface: ChatGPT / Codex app / Claude chat / Claude Code
- bridge truth: manual_handoff_only
- model/mode used or recommended
- prompt format used: plain text or ghoti_current_prompt.md file
- repo root
- branch
- latest commit known
- files changed, if any
- validation commands/results, if any
- dirty files intentionally left unstaged
- runtime wiring truth
- blocked/auth/stale-prompt issues
- next recommended handoff/action
```

---

*Status: skill_package_created / not_runtime_wired*

*Bridge truth: manual_handoff_only*

*This skill is a Codex operator-side workflow document. It is not wired into the Ghoti runtime, dashboard, approval queue, MCP server, Claude Code, or executor.*
