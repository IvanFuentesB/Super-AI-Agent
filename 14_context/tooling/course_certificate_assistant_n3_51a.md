# Course/Certificate Assistant — N+3.51A

Generated: 2026-05-06

## Summary

Local study planning tool. Generates plans, trackers, certificate logs.

**Hard rule: NO fake certificates, NO cheating, NO assessment submission.**

## Commands Run

```powershell
python 03_scripts/course_certificate_assistant.py --help
python 03_scripts/course_certificate_assistant.py --policy
python 03_scripts/course_certificate_assistant.py --plan --course-name "Python Automation Foundations" --provider "Local/Online" --hours 10 --deadline "2026-06-01" --dry-run
python 03_scripts/course_certificate_assistant.py --tracker --course-name "Python Automation Foundations" --dry-run
python 03_scripts/course_certificate_assistant.py --certificate-log --course-name "Python Automation Foundations" --provider "Local/Online" --dry-run
python 03_scripts/course_certificate_assistant.py --plan ... --apply
python 03_scripts/course_certificate_assistant.py --tracker ... --apply
python 03_scripts/course_certificate_assistant.py --certificate-log ... --apply
python 03_scripts/course_certificate_assistant.py --status
```

## Status

| Item | Value |
|------|-------|
| Plans dir | EXISTS — 1 file |
| Trackers dir | EXISTS — 1 file |
| Cert log dir | EXISTS — 1 file |
| Policy | Printed — allowed and forbidden clearly stated |

## Automation State

- `--policy`: PASS
- `--plan --dry-run`: PASS
- `--tracker --dry-run`: PASS
- `--certificate-log --dry-run`: PASS
- `--plan --apply`: PASS (wrote plan file)
- `--tracker --apply`: PASS (wrote tracker file)
- `--certificate-log --apply`: PASS (wrote cert log template)
- `--status`: PASS

## What Is Automated

- Study plan file generation (template with goals, schedule, resources, reflection prompts)
- Progress tracker file generation
- Certificate log template generation

## What Is Still Manual

- Filling in actual course content
- Doing the course modules
- All assessments (human only)
- Claiming completion (only after legitimate completion)

## Output Dirs

```
14_context/courses/plans/
14_context/courses/trackers/
14_context/courses/certificate_log/
```

## Safety Rules

- NO fake certificates
- NO cheating
- NO assessment submission on behalf of user
- NO impersonation
- Human does all assessments
