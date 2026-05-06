# Ruflo Source and Install — N+3.56-FIX

**Script**: `03_scripts/ruflo_install_gate.py`

## What changed in N+3.56-FIX

- Added `--source-status` mode with explicit status codes.
- Truthful clean-checkout messaging: source absent = NOT unsafe, needs bootstrap.
- If source present and `--apply`, auto-writes `23_configs/ruflo_source.example.json`.

## Status codes from --source-status
| Code | Meaning |
|------|---------|
| `SOURCE_PRESENT` | Ruflo dir exists with package.json |
| `SOURCE_MISSING_BOOTSTRAPPABLE` | Dir absent, but ruflo_source.example.json exists |
| `SOURCE_MISSING_NO_CONFIG` | Dir absent, no config — expected in clean checkout |
| `PACKAGE_LOCK_PRESENT` | package-lock.json exists |
| `PACKAGE_LOCK_MISSING` | package-lock.json absent (npm ci blocked) |
| `NPM_PRESENT` | npm found |
| `NPM_MISSING` | npm not found (install Node.js) |
| `NODE_MODULES_INSTALLED` | deps installed |
| `NODE_MODULES_MISSING` | deps not installed |
| `RUNTIME_WIRING_NO` | Ruflo not wired to runtime (always) |

## Validation commands
```bash
python 03_scripts/ruflo_install_gate.py --help
python 03_scripts/ruflo_install_gate.py --source-status
python 03_scripts/ruflo_install_gate.py --status
python 03_scripts/ruflo_install_gate.py --install --dry-run
python 03_scripts/ruflo_install_gate.py --smoke
python 03_scripts/ruflo_install_gate.py --report --dry-run
python 03_scripts/ruflo_install_gate.py --catalog --dry-run
```

## Clean checkout behavior
In a clean git clone, `21_repos/third_party/evals/ruflo/` may be absent.
This is expected and is NOT a safety failure.
The `--source-status` command will say `SOURCE_MISSING_NO_CONFIG` and explain what to do.

## Install safety rules (unchanged)
- Only `npm ci --ignore-scripts` is allowed.
- Blocked if lifecycle scripts detected.
- Blocked if package-lock.json missing.
- Blocked if npm not found.
- No runtime launch after install.
