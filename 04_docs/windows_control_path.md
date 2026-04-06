# Windows Control Path

## Near-Term Path

- Playwright and browser control first
- deterministic local browser flows before broader GUI automation

## Likely Windows GUI Paths Later

- `Windows-Use`: agent-style Windows GUI control at the accessibility layer
- `Windows-MCP`: lower-level Windows MCP bridge for app and UI interaction

## Later Experiments

- `open-interpreter`: broad local code and system control reference
- `open-computer-use`: wider computer-use platform reference

## Why Browser Control Is Safer First

- narrower scope
- easier verification
- easier rollback
- less chance of hidden OS-level side effects

## What Would Need To Be Added Later

- approval gates before risky actions
- observation loop for visible state checks
- audit log for what happened
- kill switch for immediate stop
