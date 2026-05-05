# Merge Checklist — Agent Lane Branch

Run this checklist before merging any agent lane branch into the main branch.

## Pre-Merge Validation

- [ ] python 03_scripts/agent_lane_status.py --check -> PASS
- [ ] python 03_scripts/agent_lane_status.py --list -> no unexpected active locks
- [ ] git diff --check <base>...<branch> -> no trailing whitespace on new files
- [ ] All new files are within the agent's declared allowed_paths
- [ ] No shared locked files were modified by an agent that did not own the lock
- [ ] agent_lane_registry.json still parses as valid JSON
- [ ] active_locks.jsonl and lane_status.jsonl parse as valid JSONL

## Safety Gates

- [ ] No outbound/live/account actions in the diff
- [ ] No install commands, no repo clones, no new MCP connections
- [ ] No deletions of history, memory, task, or audit files
- [ ] No course/exam impersonation, no credential fabrication
- [ ] Human approval documented for any action that required it

## Content Review

- [ ] Commit message is accurate and follows repo convention
- [ ] New docs do not overwrite large historical sections
- [ ] CRLF/whitespace issues on new files are resolved (not masked)
- [ ] Dirty/unrelated files were not staged

## Post-Merge

- [ ] Append released status to lane_status.jsonl for the merged lane
- [ ] Update 14_context/current_state.md and 14_context/next_actions.md concisely
- [ ] Update 14_context/ghoti_finish_line_log.md with milestone summary
- [ ] Push to origin
