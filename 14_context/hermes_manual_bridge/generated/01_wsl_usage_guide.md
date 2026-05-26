# WSL Usage Guide For Ghoti

WSL lets Windows run Ubuntu. From Windows PowerShell, run:

```powershell
wsl -d Ubuntu
```

To leave Ubuntu, type:

```bash
exit
```

## Path Mapping

- Windows repo path: `C:\Users\ai_sandbox\Documents\AI_Managed_Only`
- WSL repo path: `/mnt/c/Users/ai_sandbox/Documents/AI_Managed_Only`
- Prompt example: `ai_sandbox@Ivan-G14:/mnt/c/Users/ai_sandbox$`

The `/mnt/c` prefix means the Windows `C:\` drive from inside Ubuntu.
A prompt like `ai_sandbox@Ivan-G14:/mnt/c/Users/ai_sandbox$` means user `ai_sandbox`, machine
`Ivan-G14`, current Linux directory `/mnt/c/Users/ai_sandbox`.

## Hermes Truth

- Hermes path: `/home/ai_sandbox/.local/bin/hermes`
- Hermes version: `Hermes Agent v0.14.0 (2026.5.16)`
- Skills detected: `79`
- Readiness: `64%`

Safety: safe probes only, no live provider setup, no provider config,
no Telegram setup, no tokens, no browser automation, no computer-use
click/type, and no live APIs.
