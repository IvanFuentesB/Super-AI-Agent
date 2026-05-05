# Agent Lane Lock Template

Use this for human-readable lock notes. Machine-readable active locks go in `active_locks.jsonl`.

## Lock

- lock_id:
- agent_id:
- lane_type:
- model_or_tool:
- branch:
- task_slug:
- locked_files:
- allowed_paths:
- forbidden_paths:
- started_at:
- expected_outputs:
- safe_to_interrupt:
- status:
- human_approval_required_for_merge: yes
- notes:

## Safety Confirmation

- no external tool install:
- no live account action:
- no posting/email/payment/scraping:
- no model-output execution:
- no shared-file overlap:
