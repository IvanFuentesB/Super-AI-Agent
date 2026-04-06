# gh Path And Auth

## Windows Availability

`gh` can exist in common locations such as:

- `%ProgramFiles%\GitHub CLI\gh.exe`
- `%ProgramFiles(x86)%\GitHub CLI\gh.exe`
- `%LocalAppData%\Programs\GitHub CLI\gh.exe`
- `%USERPROFILE%\scoop\apps\gh\current\bin\gh.exe`

## Installed vs PATH-Visible

- Installed means the binary exists somewhere on disk
- PATH-visible means the current shell can call `gh` directly
- Runtime checks should distinguish those two states clearly

## Auth Meaning

`gh auth status` answers whether the current shell can talk to GitHub through the GitHub CLI account state. Remote issue and PR creation depend on both:

- `gh` being found
- `gh` being authenticated

## Safe Next Steps When gh Is Missing

- diagnose whether `gh` is absent or only missing from PATH
- use per-process fallback resolution if a valid binary is found
- avoid global PATH edits unless explicitly approved
- keep remote GitHub actions gated until both presence and auth are confirmed
