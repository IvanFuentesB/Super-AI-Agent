# Codex Master Batch Prompt

## Workspace
<absolute path>

## Task Goal
<what should be achieved>

## Context To Read First
- 14_context/current_state.md
- 14_context/next_actions.md
- 14_context/decisions.md
- 14_context/open_questions.md
- 14_context/recent_failures.md
- 14_context/status_board.md

## Constraints
- keep changes scoped
- no hype
- no fake claims
- prefer small reversible steps
- ask before risky or destructive actions
- do not modify unrelated files

## Required Process
1. Read the context files first
2. Show exact target paths
3. Show the plan first
4. Apply only the requested changes
5. Validate results
6. Commit changes
7. Push branch if origin exists
8. Report final status

## Git Instructions
- stay on current branch unless branch creation is requested
- if a new capability is being added, create a feat/<name> branch
- commit with an explicit message
- push after commit
- do not merge unless explicitly asked

## Final Report
- changed file list
- compact diff summary
- current branch
- latest commit hash
- whether push succeeded
- whether working tree is clean
