"""Run the overlay rehearsal scenarios against a staged target and record the results.

    python -I rehearse.py <staging-root> <package> <wrong-package> <report.json>
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
GIT_ENV = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(target, *args):
    return subprocess.run(["git", "-C", str(target), *args], capture_output=True, text=True, env=GIT_ENV).stdout.strip()


def fingerprint(root):
    target, state = root / "t", root / "state"
    files = {}
    for base, label in ((target, "t"), (state, "state")):
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
            for name in filenames:
                p = Path(dirpath, name)
                files[f"{label}/{p.relative_to(base).as_posix()}"] = sha(p)
    junctions = {p.relative_to(target).as_posix(): os.path.realpath(p) for p in target.rglob("node_modules")
                 if os.path.isjunction(p)}
    return {"files": files, "head": git(target, "rev-parse", "HEAD"),
            "head_ref": git(target, "symbolic-ref", "-q", "HEAD") or None,
            "refs": git(target, "for-each-ref", "--format=%(refname) %(objectname)"), "junctions": junctions}


def diff(a, b):
    keys = set(a["files"]) | set(b["files"])
    changed = sorted(k for k in keys if a["files"].get(k) != b["files"].get(k))
    other = {k: (a[k], b[k]) for k in ("head", "head_ref", "refs", "junctions") if a[k] != b[k]}
    return changed, other


def tool(cmd, root, package, txn=None, stop_after=None):
    env = {**os.environ}
    env.pop("PAPERCLIP_OVERLAY_TEST_STOP_AFTER", None)
    if stop_after:
        env["PAPERCLIP_OVERLAY_TEST_STOP_AFTER"] = stop_after
    argv = [PY, "-I", str(HERE / "paperclip_overlay.py"), cmd, str(root / "t"), str(package)] + ([str(txn)] if txn else [])
    started = time.monotonic()
    r = subprocess.run(argv, capture_output=True, text=True, env=env)
    return {"argv": [Path(a).name if i < 3 else a for i, a in enumerate(argv)], "exit": r.returncode,
            "stdout": r.stdout.strip()[-600:], "stderr": r.stderr.strip()[-400:],
            "seconds": round(time.monotonic() - started, 1)}


def main(root, package, wrong_package, out):
    root, package = Path(root).resolve(), Path(package).resolve()
    if any(root.glob(f"{Path(out).stem}-txn*")):
        raise SystemExit("transaction directories for this run name already exist")
    target = root / "t"
    report = {"staging_root": str(root), "package": str(package), "scenarios": []}
    base_fp = fingerprint(root)
    report["baseline"] = {"head": base_fp["head"], "head_ref": base_fp["head_ref"], "files": len(base_fp["files"])}

    def record(name, result, expect, before, after, extra=None):
        changed, other = diff(before, after)
        entry = {"scenario": name, "expect": expect, **result, "changed_paths": len(changed),
                 "changed_sample": changed[:12], "non_file_changes": other, **(extra or {})}
        report["scenarios"].append(entry)
        print(json.dumps({k: entry[k] for k in ("scenario", "exit", "stdout", "changed_paths")})[:400])
        return changed, other

    n = 0

    def txn():
        nonlocal n
        n += 1
        return root / f"{Path(out).stem}-txn{n}"

    # 1. Preflight on the exact baseline.
    record("preflight-baseline", tool("preflight", root, package), "READY, no writes", base_fp, fingerprint(root))

    # 2. Wrong preimages and wrong package: rejected before any write.
    probes = {
        "tampered ui/dist/index.html": target / "ui/dist/index.html",
        "pinned utils.ts converted to LF": target / "server/src/adapters/utils.ts",
        "extra stale chunk in ui/dist": target / "ui/dist/assets/index-STALE000.js",
    }
    for label, path in probes.items():
        original = path.read_bytes() if path.exists() else None
        if label.startswith("tampered"):
            path.write_bytes(original + b"\n<!-- tampered -->\n")
        elif label.startswith("pinned"):
            path.write_bytes(original.replace(b"\r\n", b"\n"))
        else:
            path.write_bytes(b"// stale chunk\n")
        before, t = fingerprint(root), txn()
        result = tool("apply", root, package, t)
        changed, other = record(f"reject: {label}", result, "REJECTED exit 2; no txn dir; no change", before,
                                fingerprint(root), {"txn_dir_created": t.exists()})
        if original is None:
            path.unlink()
        else:
            path.write_bytes(original)
    before, t = fingerprint(root), txn()
    record("reject: wrong package (superseded LF draft)", tool("apply", root, Path(wrong_package), t),
           "REJECTED exit 2", before, fingerprint(root), {"txn_dir_created": t.exists()})
    assert fingerprint(root) == base_fp, "probe restoration failed"

    # 3. Interruption after each journal stage, then recover -> exact baseline.
    for stage in ("prepared", "staged", "fetched", "source_switched", "outputs_switched"):
        t = txn()
        interrupted = tool("apply", root, package, t, stop_after=stage)
        mid = fingerprint(root)
        recovered = tool("recover", root, package, t)
        after = fingerprint(root)
        changed, other = diff(base_fp, after)
        report["scenarios"].append({"scenario": f"interrupt after {stage} -> recover", "interrupted": interrupted,
                                    "changed_while_interrupted": len(diff(base_fp, mid)[0]), "recover": recovered,
                                    "exact_baseline_after_recover": not changed and not other,
                                    "residual": changed[:10], "residual_other": other})
        print(stage, interrupted["stdout"][-80:], "|", recovered["stdout"], "| exact:", not changed and not other)

    # 3b. Crash in the middle of the output swap: ui/dist already moved away, cli/dist not yet.
    t = txn()
    interrupted = tool("apply", root, package, t, stop_after="source_switched")
    os.rename(target / "ui/dist", t / "replaced-by-simulated-crash-ui-dist")
    recovered = tool("recover", root, package, t)
    changed, other = diff(base_fp, fingerprint(root))
    report["scenarios"].append({"scenario": "crash mid-output-swap (ui/dist missing) -> recover",
                                "recover": recovered, "exact_baseline_after_recover": not changed and not other,
                                "residual": changed[:10], "residual_other": other})
    print("mid-swap", recovered["stdout"], "| exact:", not changed and not other)

    # 4. Full application.
    t_apply = txn()
    applied = tool("apply", root, package, t_apply)
    applied_fp = fingerprint(root)
    changed, other = diff(base_fp, applied_fp)
    src = sorted({c for c in changed if not c.startswith(("t/ui/dist/", "t/cli/dist/"))})
    report["scenarios"].append({"scenario": "apply on exact baseline", "apply": applied,
                                "changed_paths": len(changed), "changed_outside_outputs": src,
                                "ui_dist_paths_changed": sum(c.startswith("t/ui/dist/") for c in changed),
                                "cli_dist_paths_changed": sum(c.startswith("t/cli/dist/") for c in changed),
                                "non_file_changes": other, "head_tree": git(target, "rev-parse", "HEAD^{tree}"),
                                "mixed_old_and_new_entry_chunks": sorted(p.name for p in (target / "ui/dist/assets").glob("index-*.js")
                                                                         if p.name in ("index-dTuk29mb.js",))})
    print("apply", applied["stdout"], len(changed), src)

    # 5. Repeat application: documented no-op.
    t = txn()
    record("repeat apply", tool("apply", root, package, t), "ALREADY_APPLIED, 0 writes", applied_fp,
           fingerprint(root), {"txn_dir_created": t.exists()})

    # 6. Rollback: exact old source and outputs.
    rolled = tool("rollback", root, package, t_apply)
    changed, other = diff(base_fp, fingerprint(root))
    report["scenarios"].append({"scenario": "rollback after apply", "rollback": rolled,
                                "exact_baseline_after_rollback": not changed and not other,
                                "residual": changed[:10], "residual_other": other})
    print("rollback", rolled["stdout"], "| exact:", not changed and not other)

    # 7. Re-apply after rollback, then leave the staged target applied for the launcher preflight.
    t_final = txn()
    reapplied = tool("apply", root, package, t_final)
    changed, other = diff(applied_fp, fingerprint(root))
    report["scenarios"].append({"scenario": "re-apply after rollback", "apply": reapplied,
                                "identical_to_first_application": not changed, "residual": changed[:10],
                                "non_file_changes": other})
    print("reapply", reapplied["stdout"], "| identical:", not changed)
    report["final_state"] = {"head": git(target, "rev-parse", "HEAD"), "tree": git(target, "rev-parse", "HEAD^{tree}"),
                             "txn": str(t_final)}
    Path(out).write_text(json.dumps(report, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:])
