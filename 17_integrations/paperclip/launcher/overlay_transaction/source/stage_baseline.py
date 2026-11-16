"""Materialise a disposable staged copy of the installed Paperclip intake for the overlay rehearsal.

Copies only: the Git checkout of the installed commit (objects shared read-only from the intake), the raw bytes
of the launcher-pinned modified file, and every built dist directory. node_modules directories are junctions to
the intake's (read-only, never written by the rehearsal). Caches are replaced by sentinel files; the launcher's
state directory is replaced by a synthetic one. No credential, configuration, database or profile is copied.

    python -I stage_baseline.py <installed-intake> <staging-root>
"""
import _winapi
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PINNED_MODIFIED = "packages/adapter-utils/src/service-declarations.test.ts"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def manifest(root):
    """Raw hashes of every file under root, not following node_modules junctions or .git."""
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        for name in filenames:
            path = Path(dirpath, name)
            out[path.relative_to(root).as_posix()] = sha(path)
    return out


def main(intake, root):
    intake, root = Path(intake).resolve(), Path(root).resolve()
    if root.exists():
        raise SystemExit("staging root exists; refusing to reuse")
    target, state = root / "t", root / "state"
    head = run("git", "-C", str(intake), "rev-parse", "HEAD")
    branch = run("git", "-C", str(intake), "symbolic-ref", "--short", "HEAD")
    run("git", "clone", "--quiet", "--no-checkout", "--shared", str(intake), str(target))
    run("git", "-C", str(target), "config", "core.autocrlf", "true")
    run("git", "-C", str(target), "checkout", "--quiet", "-B", branch, head)
    shutil.copyfile(intake / PINNED_MODIFIED, target / PINNED_MODIFIED)
    # The intake keeps some tracked files as LF bytes (patched in place); a fresh autocrlf checkout writes CRLF.
    # Reproduce the deployed raw bytes, but only where the content is otherwise identical.
    raw_restored = []
    for rel in run("git", "-C", str(intake), "ls-files").splitlines():
        installed, staged = (intake / rel).read_bytes(), (target / rel).read_bytes()
        if installed != staged:
            if installed.replace(b"\r\n", b"\n") != staged.replace(b"\r\n", b"\n") and rel != PINNED_MODIFIED:
                raise SystemExit(f"staged {rel} differs from the intake beyond line endings")
            (target / rel).write_bytes(installed)
            raw_restored.append(rel)
    dists = sorted(p.relative_to(intake).as_posix() for p in intake.glob("**/dist")
                   if p.is_dir() and "node_modules" not in p.parts and ".git" not in p.parts)
    for rel in dists:
        shutil.copytree(intake / rel, target / rel)
    junctions = []
    for dirpath, dirnames, _ in os.walk(intake):
        rel = Path(dirpath).relative_to(intake)
        if ".git" in rel.parts or len(rel.parts) > 4:
            dirnames[:] = []
            continue
        if "node_modules" in dirnames and (target / rel).is_dir():
            _winapi.CreateJunction(str(intake / rel / "node_modules"), str(target / rel / "node_modules"))
            junctions.append((rel / "node_modules").as_posix())
        dirnames[:] = [d for d in dirnames if d not in ("node_modules", "dist")]
    # Sentinels for unrelated, untracked state that the overlay must not touch.
    for rel in (".cache/sentinel.txt", "server/node-compile-cache/sentinel.txt", "UNTRACKED_SENTINEL.txt"):
        (target / rel).parent.mkdir(parents=True, exist_ok=True)
        (target / rel).write_text("synthetic sentinel: " + rel + "\n", encoding="utf-8")
    for rel, text in {"config.json": '{"synthetic": true}\n', ".env": "SYNTHETIC_ONLY=1\n",
                      "db/sentinel.txt": "synthetic db sentinel\n", "secrets/sentinel.txt": "synthetic\n"}.items():
        (state / rel).parent.mkdir(parents=True, exist_ok=True)
        (state / rel).write_text(text, encoding="utf-8")
    # Compare the staged copy with the intake: every tracked file and every dist file, raw bytes.
    tracked = run("git", "-C", str(intake), "ls-files").splitlines()
    staged_vs_intake = [p for p in tracked if sha(target / p) != sha(intake / p)]
    dist_mismatch = [rel for rel in dists if manifest(target / rel) != manifest(intake / rel)]
    record = {"intake_head": head, "intake_branch": branch, "tracked_files": len(tracked), "raw_bytes_restored": raw_restored,
              "tracked_raw_mismatches": staged_vs_intake, "dist_dirs": dists, "dist_mismatches": dist_mismatch,
              "node_modules_junctions": junctions, "staged_manifest": manifest(target), "state_manifest": manifest(state)}
    (root / "baseline-record.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    print(json.dumps({k: (v if not isinstance(v, (dict, list)) or k in ("tracked_raw_mismatches", "dist_mismatches", "raw_bytes_restored")
                          else len(v)) for k, v in record.items()}))


if __name__ == "__main__":
    main(*sys.argv[1:])
