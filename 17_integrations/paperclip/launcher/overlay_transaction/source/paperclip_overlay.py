"""Apply or roll back the accepted Paperclip overlay (e04e2ae -> e8ad1fd) on one source checkout.

The smallest transaction around the package's manual steps: exact preimage gate before any write,
a journal, source switch by Git checkout, whole-directory swap of ui/dist and cli/dist (old and new
hashed chunks are never mixed), postimage verification, rollback, and recovery of an interrupted run.

    python -I paperclip_overlay.py preflight <target> <package> <txn-dir>
    python -I paperclip_overlay.py apply     <target> <package> <txn-dir>
    python -I paperclip_overlay.py rollback  <target> <package> <txn-dir>
    python -I paperclip_overlay.py recover   <target> <package> <txn-dir>

<txn-dir> must be new for apply and on the same volume as <target>. It holds the journal and the exact
backups. The tool does not start services, read configuration or touch anything outside <target> and
<txn-dir>. Exit status 0 = done or a documented no-op; 2 = rejected before any write; 1 = failed.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PACKAGE_INDEX_SHA256 = "20e991d6a0ee3d4aa1f959540b912b2430c5ec840a963ccf7106f7fc4efa7d63"
BASE, BASE_TREE = "e04e2ae1a0d47cdedf5380b5a0d94f280a82d5d1", "89e3964b370d6cd1474be03c04a3c3328521947f"
TARGET, TARGET_TREE = "e8ad1fd98142e6a4f53172f143381a4fa4100dd7", "bdab2ce706f3e682781ad0e93da935155b937867"
BUNDLE, BUNDLE_REF = "source/paperclip-e04e2ae..e8ad1fd.bundle", "release-47f0df4-on-e04"
FETCH_REF = "refs/paperclip-overlay/e8ad1fd"
OUTPUTS = ("ui/dist", "cli/dist")
# Launcher-pinned deployed files: raw bytes, not Git-normalised content. Unchanged by the overlay.
PINNED = {
    "server/src/adapters/utils.ts": "46e22ffde9f24ab90d094a0ffdba2c352b547dba1f40ef45cc68d9b9f279bf1c",
    "packages/adapter-utils/src/service-declarations.test.ts": "844395e3bc274c725c0d9eb5f32f20f9fae31dbcf2b84e0f8ec2a9064cbcc0e1",
}
ALLOWED_TRACKED_CHANGES = {"packages/adapter-utils/src/service-declarations.test.ts"}
STAGE_TEST_HOOK = "PAPERCLIP_OVERLAY_TEST_STOP_AFTER"  # rehearsal only: simulate an interruption


class Rejected(Exception):
    pass


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


GIT_ENV = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}  # status/preflight must not refresh the index


def git(target, *args):
    result = subprocess.run(["git", "-C", str(target), *args], capture_output=True, text=True, env=GIT_ENV)
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def tree_manifest(root):
    root = Path(root)
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob("*")) if p.is_file()} if root.is_dir() else None


def tsv(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    return [dict(zip(header, line.split("\t"))) for line in lines[1:] if line]


def load_package(package):
    package = Path(package)
    index = package / "PACKAGE_SHA256.txt"
    if not index.is_file() or sha(index) != PACKAGE_INDEX_SHA256:
        raise Rejected("package index digest differs from the accepted package")
    listed = {}
    for line in index.read_text(encoding="utf-8").splitlines():
        digest, name = line.split(" *", 1)
        listed[name[2:] if name.startswith("./") else name] = digest
    actual = {p.relative_to(package).as_posix() for p in package.rglob("*") if p.is_file()} - {"PACKAGE_SHA256.txt"}
    if set(listed) != actual or any(sha(package / name) != digest for name, digest in listed.items()):
        raise Rejected("package members differ from the accepted index")
    emitted = {}
    for row in tsv(package / "EMITTED_FILES.tsv"):
        emitted.setdefault(row["artifact"], {"old": {}, "new": {}})
        if row["installed_sha256"] != "absent":
            emitted[row["artifact"]]["old"][row["path"]] = row["installed_sha256"]
        if row["new_sha256"] != "absent":
            emitted[row["artifact"]]["new"][row["path"]] = row["new_sha256"]
    for name in OUTPUTS:
        if tree_manifest(package / "artifacts" / name) != emitted[name]["new"]:
            raise Rejected(f"package artifacts/{name} differ from EMITTED_FILES.tsv")
    sources = {row["path"]: row for row in tsv(package / "SOURCE_FILES.tsv")}
    return package, emitted, sources


def tracked_changes(target):
    # Content comparison, as the launcher's own `git diff HEAD` check does; `git status` without an index
    # refresh would also list stat-only differences (deployed LF bytes that normalise to the same content).
    return set(git(target, "diff", "--name-only", "HEAD").splitlines())


def state_of(target, emitted, sources, which):
    """Return a list of mismatches against the baseline ('old') or the overlay result ('new')."""
    problems = []
    head, tree = (BASE, BASE_TREE) if which == "old" else (TARGET, TARGET_TREE)
    if git(target, "rev-parse", "HEAD") != head or git(target, "rev-parse", "HEAD^{tree}") != tree:
        problems.append(f"HEAD is not {head[:12]} / tree {tree[:12]}")
    if tracked_changes(target) - ALLOWED_TRACKED_CHANGES:
        problems.append(f"unexpected tracked changes: {sorted(tracked_changes(target) - ALLOWED_TRACKED_CHANGES)}")
    for path, digest in PINNED.items():
        if not (target / path).is_file() or sha(target / path) != digest:
            problems.append(f"pinned deployed file bytes differ: {path}")
    column = "installed_raw_sha256" if which == "old" else "expected_installed_sha256(autocrlf=true)"
    for path, row in sources.items():
        actual = sha(target / path) if (target / path).is_file() else "absent"
        if actual != row[column]:
            problems.append(f"source {which}image differs: {path}")
    for name in OUTPUTS:
        if tree_manifest(target / name) != emitted[name][which]:
            problems.append(f"{name} is not the exact {which} manifest")
    return problems


def write_journal(txn, journal, stage):
    journal["stage"] = stage
    journal.setdefault("stages", []).append(stage)
    tmp = txn / "journal.json.tmp"
    tmp.write_text(json.dumps(journal, indent=2), encoding="utf-8")
    os.replace(tmp, txn / "journal.json")
    if os.environ.get(STAGE_TEST_HOOK) == stage:
        raise SystemExit(f"TEST INTERRUPTION after stage {stage}")


def preflight(target, package):
    target = Path(target).resolve()
    package, emitted, sources = load_package(package)
    if git(target, "config", "--get", "core.autocrlf") != "true":
        raise Rejected("target checkout must use core.autocrlf=true (installed byte convention)")
    if not state_of(target, emitted, sources, "new"):
        return target, package, emitted, sources, "ALREADY_APPLIED"
    problems = state_of(target, emitted, sources, "old")
    if problems:
        raise Rejected("baseline/preimage mismatch: " + "; ".join(problems))
    return target, package, emitted, sources, "READY"


def swap_output(target, txn, name, source_dir):
    """Replace one output directory whole: current -> txn/replaced, source_dir -> target."""
    current, parked = target / name, txn / "replaced" / name
    parked.parent.mkdir(parents=True, exist_ok=True)
    if current.exists():
        os.rename(current, parked)
    os.rename(source_dir, current)


def apply(target, package, txn):
    target, package, emitted, sources, status = preflight(target, package)
    if status == "ALREADY_APPLIED":
        print(json.dumps({"status": "ALREADY_APPLIED", "writes": 0}))
        return 0
    txn = Path(txn).resolve()
    if txn.exists():
        raise Rejected("transaction directory already exists; use recover or rollback")
    if os.stat(target).st_dev != os.stat(txn.parent).st_dev:
        raise Rejected("transaction directory must be on the target's volume")
    txn.mkdir(parents=True)
    head_ref = subprocess.run(["git", "-C", str(target), "symbolic-ref", "-q", "HEAD"], capture_output=True, text=True).stdout.strip()
    journal = {"schema": "paperclip_overlay_txn/1", "target": str(target), "package_index": PACKAGE_INDEX_SHA256,
               "base": BASE, "result": TARGET, "original_head_ref": head_ref or None}
    write_journal(txn, journal, "prepared")
    # Exact backups of the outputs (for rollback) and the new outputs staged next to them.
    for name in OUTPUTS:
        shutil.copytree(target / name, txn / "backup" / name)
        shutil.copytree(package / "artifacts" / name, txn / "new" / name)
        if tree_manifest(txn / "backup" / name) != emitted[name]["old"] or tree_manifest(txn / "new" / name) != emitted[name]["new"]:
            raise RuntimeError(f"staged copy of {name} is not exact")
    write_journal(txn, journal, "staged")
    git(target, "fetch", "--no-tags", str(package / BUNDLE), f"{BUNDLE_REF}:{FETCH_REF}")
    if git(target, "rev-parse", FETCH_REF) != TARGET:
        raise RuntimeError("bundle did not provide the accepted commit")
    write_journal(txn, journal, "fetched")
    git(target, "checkout", "--quiet", "--detach", TARGET)
    write_journal(txn, journal, "source_switched")
    for name in OUTPUTS:
        swap_output(target, txn, name, txn / "new" / name)
    write_journal(txn, journal, "outputs_switched")
    problems = state_of(target, emitted, sources, "new")
    if problems:
        raise RuntimeError("postimage verification failed: " + "; ".join(problems))
    write_journal(txn, journal, "complete")
    print(json.dumps({"status": "APPLIED", "txn": str(txn)}))
    return 0


def rollback(target, package, txn):
    target = Path(target).resolve()
    package, emitted, sources = load_package(package)
    txn = Path(txn).resolve()
    journal = json.loads((txn / "journal.json").read_text(encoding="utf-8"))
    if Path(journal["target"]) != target:
        raise Rejected("journal belongs to a different target")
    stages = journal["stages"]
    if "source_switched" in stages or git(target, "rev-parse", "HEAD") != BASE:
        git(target, "checkout", "--quiet", journal["original_head_ref"].removeprefix("refs/heads/")
            if journal["original_head_ref"] else BASE)
    elif journal["original_head_ref"] and subprocess.run(["git", "-C", str(target), "symbolic-ref", "-q", "HEAD"],
                                                          capture_output=True, text=True).stdout.strip() != journal["original_head_ref"]:
        git(target, "checkout", "--quiet", journal["original_head_ref"].removeprefix("refs/heads/"))
    for name in OUTPUTS:
        if tree_manifest(target / name) != emitted[name]["old"]:
            backup = txn / "backup" / name
            if tree_manifest(backup) != emitted[name]["old"]:
                raise RuntimeError(f"backup of {name} is not the exact preimage; refusing to restore")
            rolled = txn / "rolled-back-from" / name
            rolled.parent.mkdir(parents=True, exist_ok=True)
            if (target / name).exists():
                os.rename(target / name, rolled)
            shutil.copytree(backup, target / name)
    subprocess.run(["git", "-C", str(target), "update-ref", "-d", FETCH_REF], capture_output=True)
    problems = state_of(target, emitted, sources, "old")
    if problems:
        raise RuntimeError("rollback verification failed: " + "; ".join(problems))
    journal["rolled_back"] = True
    write_journal(txn, journal, "rolled_back")
    print(json.dumps({"status": "ROLLED_BACK", "txn": str(txn)}))
    return 0


def recover(target, package, txn):
    """An interrupted apply is recovered by rolling back to the exact baseline; re-run apply afterwards."""
    journal = json.loads((Path(txn) / "journal.json").read_text(encoding="utf-8"))
    if journal["stage"] in ("complete", "rolled_back"):
        print(json.dumps({"status": "NOTHING_TO_RECOVER", "stage": journal["stage"]}))
        return 0
    return rollback(target, package, txn)


def main(argv):
    command, target, package = argv[:3]
    try:
        if command == "preflight":
            status = preflight(target, package)[4]
            print(json.dumps({"status": status}))
            return 0
        return {"apply": apply, "rollback": rollback, "recover": recover}[command](target, package, argv[3])
    except Rejected as error:
        print(json.dumps({"status": "REJECTED", "reason": str(error)}))
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
