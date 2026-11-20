"""Run a launcher file's own installation_check() against a staged Paperclip target (test context only).

The launcher file is imported unmodified from its path and its raw SHA-256 is checked first. Only three
location constants are substituted: SOURCE (the staged intake), STATE (a synthetic state
directory) and NATIVE (see below). SOURCE_REVISION, DEPLOYED_SOURCE_FILES, HELPER_HASHES and every check are the file's own.
installation_check() only inspects: it starts no process other than its pinned read-only Git inspection.

    python -I launcher_preflight.py <launcher.py> <expected-raw-sha256> <staged-target> <synthetic-state> <native-helper-root>

NATIVE is set to the real reviewed helper worktree, exactly as the launcher test fixture does
(mock.patch.multiple(host, SOURCE=..., STATE=..., NATIVE=...)), because NATIVE is derived from the file location.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


def main(launcher, expected, target, state, native):
    raw = Path(launcher).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected:
        raise SystemExit(f"launcher bytes differ: {digest}")
    spec = importlib.util.spec_from_file_location("paperclip_host_under_test", launcher)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pinned = module.SOURCE_REVISION
    module.SOURCE, module.STATE, module.NATIVE = Path(target).resolve(), Path(state).resolve(), Path(native).resolve()
    try:
        revision = module.installation_check()
        result = {"result": "PASS", "revision": revision}
    except Exception as error:  # report the launcher's own refusal verbatim
        result = {"result": "REFUSED", "error": type(error).__name__, "message": str(error)[:300]}
    # Serving/entry layout the launcher relies on but does not itself inspect (server/src/app.ts order:
    # server/ui-dist first, then ui/dist). Read-only.
    src = module.SOURCE
    index_html = (src / "ui/dist/index.html").read_text(encoding="utf-8") if (src / "ui/dist/index.html").is_file() else ""
    entries = sorted(p.name for p in (src / "ui/dist/assets").glob("index-*.js")) if (src / "ui/dist/assets").is_dir() else []
    referenced = [e for e in entries if f"/assets/{e}" in index_html]
    layout = {
        "path_substitutions": {"SOURCE": str(module.SOURCE), "STATE": str(module.STATE), "NATIVE": str(module.NATIVE)},
        "server_ui_dist_present": (src / "server/ui-dist").exists(),
        "ui_dist_index_html": (src / "ui/dist/index.html").is_file(),
        "entry_chunks_referenced_by_index_html": referenced,
        "old_entry_chunk_present": (src / "ui/dist/assets/index-dTuk29mb.js").exists(),
        "ts_entry_points": {p: (src / p).is_file() for p in ("cli/src/index.ts", "cli/src/client/board-auth.ts",
                                                             "server/src/index.ts", "cli/node_modules/tsx/dist/cli.mjs")},
    }
    print(json.dumps({"launcher_sha256": digest, "pinned_revision": pinned, "target": str(module.SOURCE), **result,
                      "layout": layout}))


if __name__ == "__main__":
    main(*sys.argv[1:])
