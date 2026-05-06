# Codex N+3.57 - Bridge And Course Helper Audit

## Verdict

PENDING TARGET BRANCH.

The bridge and course helper fixes cannot be audited because `origin/feat/ghoti-agent-claude-n3-56-fix-bridge-ruflo-gemma-clean-pass` is missing.

## Required Bridge Proof Once Branch Exists

Codex must validate:

- `03_scripts/cc_codex_bridge.py --help`
- `03_scripts/cc_codex_bridge.py --status`
- `03_scripts/cc_codex_bridge.py --init --dry-run`
- `03_scripts/cc_codex_bridge.py --write-pair --title audit-smoke --body "Manual bridge smoke only." --dry-run`

Expected truth:

- CC/Codex automatic = NO.
- Clipboard automation = NO.
- External API calls = NO.
- Auto-send = NO.
- Human copy-paste required = YES.
- `--status` is read-only.
- `--init --dry-run` writes nothing.
- `--init` or equivalent can create missing bridge dirs safely when explicitly applied.

## Required Course Helper Proof Once Branch Exists

Codex must validate:

```powershell
python 03_scripts/course_certificate_assistant.py --policy
python 03_scripts/course_certificate_assistant.py --plan --course-name "Audit Smoke Course" --provider "Local Test" --goal "Create legitimate study plan only" --dry-run
python 03_scripts/course_certificate_assistant.py --tracker --course-name "Audit Smoke Course" --dry-run
```

Expected truth:

- `--goal` is supported.
- No fake certificates.
- No cheating.
- No assessment submission.
- No impersonation.
- Human does all assessments.

## Current Status

N+3.56 had a conditional gap: the course helper rejected `--goal`, and bridge verification was PARTIAL until bridge dirs existed. N+3.57 cannot confirm those fixes until the target branch is pushed.
