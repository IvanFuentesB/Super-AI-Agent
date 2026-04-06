# First Install / Repair Batch Plan

Last updated: 2026-04-05

## Scope

This is the exact first low-risk install and repair batch plan only.

Included:

- Python repair
- PowerShell 7
- `uv`
- `gh`
- `pnpm`

Not included:

- PATH cleanup
- Ollama
- Docker
- WSL2
- browser changes
- registry edits outside what installers do themselves

## Current verified facts

- Python 3.13 components are registered as installed, but `python`, `py`, and `pip` do not resolve.
- No on-disk Python install path was found in the common locations checked from this account.
- `pwsh`, `uv`, `gh`, and `pnpm` are not installed.

## Low-risk installation strategy

### Step 0: Snapshot before changes

Run these first later:

```powershell
where.exe python
where.exe py
where.exe pip
where.exe pwsh
where.exe uv
where.exe gh
where.exe pnpm
winget list | Select-String -Pattern 'Python|PowerShell|GitHub CLI|pnpm|uv'
```

### Step 1: Repair Python without touching PATH yet

Rationale:

- Python is in a half-installed or unreachable state.
- The safest first attempt is a repair-style reinstall using the official Python package and launcher.
- Keep `PrependPath=0` for now so PATH is not changed in this batch.
- Reinstall the launcher explicitly so `py` has a chance to work without doing broader PATH edits.

Planned commands:

```powershell
winget install --id Python.Launcher --exact --force --accept-source-agreements --accept-package-agreements
winget install --id Python.Python.3.13 --exact --force --accept-source-agreements --accept-package-agreements --override "/quiet InstallAllUsers=0 PrependPath=0 Include_launcher=1 Include_pip=1 Include_test=0"
```

Verification after Python step:

```powershell
where.exe py
py -V
py -0p
py -m pip --version
```

If `py` works but `python` still does not, stop there for this batch. Do not touch PATH yet.

### Step 2: Install PowerShell 7

```powershell
winget install --id Microsoft.PowerShell --exact --accept-source-agreements --accept-package-agreements
```

Verification:

```powershell
where.exe pwsh
pwsh -v
```

### Step 3: Install `uv`

```powershell
winget install --id astral-sh.uv --exact --accept-source-agreements --accept-package-agreements
```

Verification:

```powershell
where.exe uv
uv --version
```

### Step 4: Install `gh`

```powershell
winget install --id GitHub.cli --exact --accept-source-agreements --accept-package-agreements
```

Verification:

```powershell
where.exe gh
gh --version
```

### Step 5: Install `pnpm`

```powershell
winget install --id pnpm.pnpm --exact --accept-source-agreements --accept-package-agreements
```

Verification:

```powershell
where.exe pnpm
pnpm --version
```

## Recommended stop points

Stop after Python if it still fails verification.

If Python is still broken after the reinstall and launcher repair:

- do not continue to tool installs blindly
- do not edit machine PATH in the same batch
- inspect the actual installed Python files first

## Why PATH is not part of this batch

Python docs explicitly note that PATH setup is only reliably simple for a single system-wide install, while the Windows launcher is the better selector for multiple versions.

That makes launcher-first verification safer than jumping straight to PATH edits.

Sources used:

- https://docs.python.org/3.13/using/windows.html
- `winget show --id Python.Python.3.13`
- `winget show --id Python.Launcher`
- `winget show --id Microsoft.PowerShell`
- `winget show --id astral-sh.uv`
- `winget show --id GitHub.cli`
- `winget show --id pnpm.pnpm`
