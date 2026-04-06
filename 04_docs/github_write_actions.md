# GitHub Write Actions

## Scope Now

- Issue draft generation
- PR draft generation
- Local branch creation helper
- Optional remote issue creation
- Optional remote PR creation

## Local vs Remote

- Local drafts are file-backed exports under `11_exports/github/`
- Local branch creation changes the local repo only
- Remote issue and PR creation mutate GitHub state and require explicit approval

## Approval Rule

Remote mutation must never happen implicitly. The CLI requires an explicit approve flag before local branch creation, remote issue creation, or remote PR creation.

## Dependency

Remote GitHub actions depend on `gh`. If `gh` is missing, the runtime should refuse cleanly and explain that only read-only Git support is available.

## Out of Scope Now

- merges
- force pushes
- repo settings changes
- mass issue creation
- destructive remote actions
