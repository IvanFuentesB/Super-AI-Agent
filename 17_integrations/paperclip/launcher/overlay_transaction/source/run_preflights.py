"""Run launcher_preflight.py for each (launcher, target-state) pair with GIT_* variables removed from the
environment (the launcher refuses inherited Git overrides). Records exactly which variables were removed.

    python -I run_preflights.py <python-for-launcher> <staged-target> <synthetic-state> <native-helper-root> <label> <launcher> <sha256> [...]
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main(python, target, state, native, label, *pairs):
    removed = sorted(k for k in os.environ if k.upper().startswith("GIT_") and k.upper() != "GIT_PAGER")
    env = {k: v for k, v in os.environ.items() if k not in removed}
    for launcher, digest in zip(pairs[::2], pairs[1::2]):
        r = subprocess.run([python, "-I", str(HERE / "launcher_preflight.py"), launcher, digest, target, state, native],
                           capture_output=True, text=True, env=env)
        out = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
        print(json.dumps({"label": label, "launcher": launcher, "exit": r.returncode, "removed_env": removed,
                          "result": json.loads(out) if out.startswith("{") else out, "stderr": r.stderr.strip()[-600:]}))


if __name__ == "__main__":
    main(*sys.argv[1:])
