"""Apply or roll back the accepted Paperclip overlay (e04e2ae -> e8ad1fd) on one source checkout.

Contract: TRANSACTION.md (schema paperclip_overlay_txn/2). In short: an exact preimage gate before any write,
a target-scoped OS lock held for the whole operation, a journal written before each step it announces,
atomic per-file / per-directory moves whose position is always re-derived from the target, idempotent
rollback that touches only components still owned by this transaction, and bounded Git execution.

    python -I paperclip_overlay.py preflight <target> <package>
    python -I paperclip_overlay.py apply     <target> <package> <txn-dir>
    python -I paperclip_overlay.py rollback  <target> <package> <txn-dir>
    python -I paperclip_overlay.py recover   <target> <package> <txn-dir>

Exit status: 0 done or a verified no-op; 2 rejected, nothing written by this invocation; 3 inconsistent
state, nothing written by this invocation (inspect, do not guess); 1 unexpected failure (run recover).
"""
from dataclasses import dataclass, field
import hashlib
import json
import msvcrt
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import uuid

SCHEMA = "paperclip_overlay_txn/2"
STOP_HOOK = "PAPERCLIP_OVERLAY_TEST_STOP_AT"  # rehearsal/test only: simulate a crash at a named point
GIT_ENV_ALLOWED = {"SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT"}
LOCAL_CONFIG_ALLOWED = {"core.repositoryformatversion", "core.filemode", "core.bare", "core.logallrefupdates",
                        "core.symlinks", "core.ignorecase"}


@dataclass(frozen=True)
class Spec:
    package_index: str
    base: str
    base_tree: str
    target: str
    target_tree: str
    bundle: str
    bundle_ref: str
    outputs: tuple = ("ui/dist", "cli/dist")
    pinned: dict = field(default_factory=dict)
    allowed_tracked_changes: frozenset = frozenset()


ACCEPTED = Spec(
    package_index="20e991d6a0ee3d4aa1f959540b912b2430c5ec840a963ccf7106f7fc4efa7d63",
    base="e04e2ae1a0d47cdedf5380b5a0d94f280a82d5d1", base_tree="89e3964b370d6cd1474be03c04a3c3328521947f",
    target="e8ad1fd98142e6a4f53172f143381a4fa4100dd7", target_tree="bdab2ce706f3e682781ad0e93da935155b937867",
    bundle="source/paperclip-e04e2ae..e8ad1fd.bundle", bundle_ref="release-47f0df4-on-e04",
    pinned={"server/src/adapters/utils.ts": "46e22ffde9f24ab90d094a0ffdba2c352b547dba1f40ef45cc68d9b9f279bf1c",
            "packages/adapter-utils/src/service-declarations.test.ts":
                "844395e3bc274c725c0d9eb5f32f20f9fae31dbcf2b84e0f8ec2a9064cbcc0e1"},
    allowed_tracked_changes=frozenset({"packages/adapter-utils/src/service-declarations.test.ts"}),
)


class Rejected(Exception):
    """Refused before this invocation wrote any transaction state (exit 2)."""


class Inconsistent(Exception):
    """Unclassifiable state found before this invocation wrote any transaction state (exit 3)."""


PAUSE_HOOK = "PAPERCLIP_OVERLAY_TEST_PAUSE_AT"  # rehearsal/test only: wait at a named point for an external kill
TEST_MARKER = "paperclip-overlay-test-staging"  # .git/<marker>: created only by fixtures and stage_baseline.py
_TEST_HOOKS = {"enabled": False}


def enable_test_hooks(target):
    requested = sorted(k for k in os.environ if k.upper().startswith("PAPERCLIP_OVERLAY_TEST_"))
    is_staging = (Path(target) / ".git" / TEST_MARKER).is_file()
    if requested and not is_staging:
        raise Rejected(f"test hooks refused outside a marked staging target: {requested}")
    _TEST_HOOKS["enabled"] = bool(requested) and is_staging


def checkpoint(name):
    if not _TEST_HOOKS["enabled"]:
        return
    if os.environ.get(STOP_HOOK) == name:
        os._exit(75)  # simulated crash: no cleanup, no journal update, lock released by the OS
    if os.environ.get(PAUSE_HOOK) == name:
        ready = os.environ.get("PAPERCLIP_OVERLAY_TEST_PAUSE_FILE")
        if ready:
            Path(ready).write_text(str(os.getpid()), encoding="utf-8")
        import time
        while True:  # the harness terminates this process (a real OS kill) at this exact boundary
            time.sleep(1)


# ---------------------------------------------------------------- paths
def plain(path, *, must_exist=True, allow_hardlinks=False, missing_parents=False):
    """Absolute lexical path with no link/reparse component and (for files) a single link."""
    path = Path(os.path.abspath(path))
    if str(path).startswith(("\\\\", "//")):
        raise Rejected(f"network path refused: {path}")
    for item in (*reversed(path.parents), path):
        try:
            st = item.lstat()
        except FileNotFoundError:
            if must_exist or (item != path and not missing_parents):
                raise Rejected(f"path does not exist: {item}")
            continue
        if stat.S_ISLNK(st.st_mode) or getattr(st, "st_file_attributes", 0) & 0x400:
            raise Rejected(f"link/reparse path refused: {item}")
        if not allow_hardlinks and stat.S_ISREG(st.st_mode) and st.st_nlink != 1:
            raise Rejected(f"hardlinked file refused: {item}")
    return path


def overlaps(a, b):
    a, b = os.path.normcase(str(a)), os.path.normcase(str(b))
    return a == b or a.startswith(b.rstrip("\\/") + os.sep) or b.startswith(a.rstrip("\\/") + os.sep)


def check_roots(target, package, txn=None):
    """Plain (no link/reparse) lexical paths, then canonical physical paths (8.3 short names and case
    resolved by realpath) for every comparison and for the journal binding."""
    plain(target)
    plain(package, allow_hardlinks=True)
    roots = {"target": plain(os.path.realpath(target)),
             "package": plain(os.path.realpath(package), allow_hardlinks=True)}
    if txn is not None:
        plain(txn, must_exist=False)
        roots["txn"] = Path(os.path.realpath(txn))
        plain(roots["txn"], must_exist=False)
    names = list(roots)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if overlaps(roots[a], roots[b]):
                raise Rejected(f"{a} and {b} roots overlap: {roots[a]} / {roots[b]}")
    if txn is not None and os.stat(roots["target"]).st_dev != os.stat(roots["txn"].parent).st_dev:
        raise Rejected("transaction directory must be on the target's volume")
    return roots


def scan_tree(root):
    """Exact manifest of a directory; refuses links/reparse points and hardlinked files inside it."""
    root = plain(root, must_exist=False, missing_parents=True)
    if not root.exists():
        return None
    if not root.is_dir():
        raise Rejected(f"expected an owned directory: {root}")
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            st = Path(dirpath, name).lstat()
            if stat.S_ISLNK(st.st_mode) or getattr(st, "st_file_attributes", 0) & 0x400:
                raise Rejected(f"link/reparse inside owned output: {Path(dirpath, name)}")
            if stat.S_ISREG(st.st_mode) and st.st_nlink != 1:
                raise Rejected(f"hardlinked file inside owned output: {Path(dirpath, name)}")
        for name in filenames:
            p = Path(dirpath, name)
            out[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def durable_copy(src, dest):
    data = Path(src).read_bytes()
    fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_BINARY)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    return hashlib.sha256(data).hexdigest()


def durable_write(dest, data):
    fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_BINARY)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write(path, data):
    path = Path(path)
    tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_BINARY)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, path)


# ---------------------------------------------------------------- git
def refuse_inherited_git():
    inherited = sorted(k for k in os.environ if k.upper().startswith("GIT_") and k.upper() != "GIT_PAGER")
    if inherited:
        raise Rejected(f"inherited Git override refused before inspection: {inherited}")


def find_git(forbidden_roots):
    """git.exe from absolute PATH entries only (never the current directory), outside every owned root."""
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry or not os.path.isabs(entry):
            continue
        candidate = Path(entry) / "git.exe"
        if candidate.is_file():
            exe = plain(candidate, allow_hardlinks=True)  # read-only use, as the reviewed helper allows
            if any(overlaps(exe, root) for root in forbidden_roots):
                raise Rejected(f"git executable inside an owned root refused: {exe}")
            return str(exe)
    raise Rejected("git.exe not found on absolute PATH entries")


class Git:
    def __init__(self, target, roots):
        refuse_inherited_git()
        self.exe = find_git(list(roots.values()))
        self.target = str(target)
        env = {k: v for k, v in os.environ.items() if k.upper() in GIT_ENV_ALLOWED}
        env.update({"HOME": self.target, "USERPROFILE": self.target, "GIT_OPTIONAL_LOCKS": "0",
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0",
                    "GIT_NO_REPLACE_OBJECTS": "1", "GIT_CONFIG_COUNT": "6",
                    "GIT_CONFIG_KEY_0": "core.fsmonitor", "GIT_CONFIG_VALUE_0": "false",
                    "GIT_CONFIG_KEY_1": "core.untrackedCache", "GIT_CONFIG_VALUE_1": "false",
                    "GIT_CONFIG_KEY_2": "core.autocrlf", "GIT_CONFIG_VALUE_2": "true",
                    "GIT_CONFIG_KEY_3": "core.hooksPath", "GIT_CONFIG_VALUE_3": os.devnull,
                    "GIT_CONFIG_KEY_4": "gc.auto", "GIT_CONFIG_VALUE_4": "0",
                    "GIT_CONFIG_KEY_5": "maintenance.auto", "GIT_CONFIG_VALUE_5": "false"})
        self.env = env

    def run(self, *args, check=True, binary=False):
        r = subprocess.run([self.exe, "-C", self.target, *args], capture_output=True, env=self.env,
                           cwd=self.target, timeout=120)
        if check and r.returncode:
            raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.decode(errors='replace').strip()}")
        return r if not check else (r.stdout if binary else r.stdout.decode().strip())

    def ok(self, *args):
        return self.run(*args, check=False).returncode == 0

    def value(self, *args):
        r = self.run(*args, check=False)
        return r.stdout.decode().strip() if r.returncode == 0 else None


def check_git_metadata(dotgit):
    """No link or reparse point anywhere inside .git: Git would follow one and write refs, objects or the
    index outside the target (an internal junction at refs/paperclip-overlay, for example)."""
    pending = [plain(dotgit)]
    while pending:
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                st = entry.stat(follow_symlinks=False)
                if stat.S_ISLNK(st.st_mode) or getattr(st, "st_file_attributes", 0) & 0x400:
                    raise Rejected(f"link/reparse point inside Git metadata refused: {entry.path}")
                if stat.S_ISDIR(st.st_mode):
                    pending.append(entry.path)
                # Windows DirEntry.stat may omit the link count. lstat fills it in.
                elif not stat.S_ISREG(st.st_mode) or (st.st_nlink or os.lstat(entry.path).st_nlink) != 1:
                    raise Rejected(f"non-owned file inside Git metadata: {entry.path}")


def check_repo(git, target, sources):
    dotgit = target / ".git"
    if not dotgit.is_dir():
        raise Rejected("target .git must be a real directory (no gitlink/worktree redirection)")
    check_git_metadata(dotgit)
    top = git.value("rev-parse", "--show-toplevel")
    if not top or os.path.normcase(os.path.abspath(top)) != os.path.normcase(str(target)):
        raise Rejected("Git resolved a different worktree")
    gitdir = git.value("rev-parse", "--absolute-git-dir")
    if not gitdir or os.path.normcase(os.path.abspath(gitdir)) != os.path.normcase(str(dotgit)):
        raise Rejected("Git resolved a different git directory")
    common = git.value("rev-parse", "--path-format=absolute", "--git-common-dir")
    if (not common or os.path.normcase(os.path.abspath(common)) != os.path.normcase(str(dotgit))
            or (dotgit / "commondir").exists()):
        raise Rejected("Git common directory redirection refused")
    for line in git.run("config", "--local", "--list").splitlines():
        key, _, value = line.partition("=")
        key = key.lower()
        parts = key.split(".")
        if key in LOCAL_CONFIG_ALLOWED:
            continue
        if len(parts) >= 3 and ((parts[0] == "remote" and parts[-1] in ("url", "fetch"))
                                or (parts[0] == "branch" and parts[-1] in ("remote", "merge"))):
            continue
        if key == "core.autocrlf" and value.lower() == "true":
            continue
        raise Rejected(f"unreviewed repository configuration refused: {key}")
    attrs = git.run("check-attr", "filter", "text", "eol", "crlf", "working-tree-encoding", "ident",
                    "--", *sources).splitlines()
    bad = [a for a in attrs if not a.endswith(": unspecified")]
    if bad:
        raise Rejected(f"conversion/filter attributes on overlay paths refused: {bad[:4]}")
    stale = [q for q in [dotgit / "index.lock", dotgit / "HEAD.lock", dotgit / "packed-refs.lock"]
             + list((dotgit / "refs").rglob("*.lock")) if q.exists()]
    if stale:
        raise Inconsistent(f"Git lock files present; inspect the interrupted Git operation first: {stale[:4]}")


# ---------------------------------------------------------------- package
def tsv(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    return [dict(zip(header, line.split("\t"))) for line in lines[1:] if line]


def load_package(package, spec):
    index = package / "PACKAGE_SHA256.txt"
    if not index.is_file() or sha_file(index) != spec.package_index:
        raise Rejected("package index digest differs from the accepted package")
    listed = {}
    for line in index.read_text(encoding="utf-8").splitlines():
        digest, name = line.split(" *", 1)
        listed[name[2:] if name.startswith("./") else name] = digest
    actual = {p.relative_to(package).as_posix() for p in package.rglob("*") if p.is_file()} - {"PACKAGE_SHA256.txt"}
    if set(listed) != actual or any(sha_file(package / n) != d for n, d in listed.items()):
        raise Rejected("package members differ from the accepted index")
    emitted = {o: {"old": {}, "new": {}} for o in spec.outputs}
    for row in tsv(package / "EMITTED_FILES.tsv"):
        if row["installed_sha256"] != "absent":
            emitted[row["artifact"]]["old"][row["path"]] = row["installed_sha256"]
        if row["new_sha256"] != "absent":
            emitted[row["artifact"]]["new"][row["path"]] = row["new_sha256"]
    for o in spec.outputs:
        if scan_tree(package / "artifacts" / o) != emitted[o]["new"]:
            raise Rejected(f"package artifacts/{o} differ from EMITTED_FILES.tsv")
    sources = {r["path"]: (r["installed_raw_sha256"], r["expected_installed_sha256(autocrlf=true)"])
               for r in tsv(package / "SOURCE_FILES.tsv")}
    return emitted, sources


# ---------------------------------------------------------------- state
def classify(git, target, spec, emitted, sources, txn_id=None, branch_ref=None):
    """Position of every owned component. Pure reads."""
    s = {}
    sym = git.value("symbolic-ref", "-q", "HEAD")
    head = git.value("rev-parse", "HEAD")
    s["head_symbolic"], s["head_oid"] = sym, head
    ref = branch_ref or sym
    s["branch_ref"], s["branch_oid"] = ref, (git.value("rev-parse", "--verify", "-q", ref) if ref else None)
    if sym and sym == ref and head == spec.base:
        s["head"] = "old"
    elif sym is None and head == spec.target:
        s["head"] = "new"
    else:
        s["head"] = "foreign"
    s["index"] = ("old" if git.ok("diff-index", "--cached", "--quiet", spec.base, "--") else
                  "new" if git.ok("diff-index", "--cached", "--quiet", spec.target, "--") else "foreign")
    s["sources"] = {}
    for path, (old, new) in sources.items():
        p = plain(target / path, must_exist=False)
        raw = sha_file(p) if p.exists() else "absent"
        s["sources"][path] = "old" if raw == old else "new" if raw == new else "missing" if raw == "absent" else "foreign"
    s["outputs"] = {}
    for o in spec.outputs:
        m = scan_tree(target / o)
        s["outputs"][o] = ("missing" if m is None else "old" if m == emitted[o]["old"] else
                           "new" if m == emitted[o]["new"] else "foreign")
    s["pinned_ok"] = all((target / p).is_file() and sha_file(target / p) == d for p, d in spec.pinned.items())
    refs = git.run("for-each-ref", "--format=%(refname) %(objectname)", "refs/paperclip-overlay/").splitlines()
    s["overlay_refs"] = dict(r.split(" ", 1) for r in refs if r)
    s["owner"] = read_owner(target)
    s["tracked_changes"] = sorted(set(git.run("diff", "--name-only", "HEAD").splitlines()) - spec.allowed_tracked_changes)
    base_ok = s["pinned_ok"] and not s["tracked_changes"] and not s["overlay_refs"]
    s["is_old"] = (base_ok and s["head"] == "old" and s["index"] == "old" and s["owner"] is None
                   and all(v == "old" or (v == "missing" and sources[k][0] == "absent") for k, v in s["sources"].items())
                   and all(v == "old" for v in s["outputs"].values()))
    s["is_new"] = (base_ok and s["head"] == "new" and s["index"] == "new" and s["owner"] is not None
                   and all(v == "new" for v in s["sources"].values()) and all(v == "new" for v in s["outputs"].values())
                   and (txn_id is None or s["owner"] == txn_id)
                   and (branch_ref is None or s["branch_oid"] == spec.base))
    return s


def read_owner(target):
    marker = target / ".git" / "paperclip-overlay-owner.json"
    if not marker.exists():
        return None
    try:
        return json.loads(plain(marker).read_text(encoding="utf-8")).get("txn_id") or "unreadable-owner-marker"
    except (ValueError, AttributeError):
        return "unreadable-owner-marker"


# ---------------------------------------------------------------- lock, journal, marker
class TargetLock:
    """OS byte-range lock on T/.git/paperclip-overlay.lock. Opening it creates the (empty) lock file once;
    that file is the only write a refused invocation may make and is not transaction state."""

    def __init__(self, target):
        self.path = plain(target / ".git" / "paperclip-overlay.lock", must_exist=False)

    def __enter__(self):
        self.fh = open(self.path, "a+b")
        try:
            self.fh.seek(0)
            msvcrt.locking(self.fh.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            self.fh.close()
            raise Rejected("target is locked by another live overlay operation")
        return self

    def __exit__(self, *exc):
        try:
            self.fh.seek(0)
            msvcrt.locking(self.fh.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            self.fh.close()


def write_journal(txn, journal, phase):
    journal["phase"] = phase
    journal["history"].append(phase)
    atomic_write(txn / "journal.json", json.dumps(journal, indent=1).encode("utf-8"))


def load_journal(txn, roots, spec):
    path = txn / "journal.json"
    if not path.is_file():
        raise Rejected("no transaction journal in that directory")
    j = json.loads(plain(path).read_text(encoding="utf-8"))
    expected = {"schema": SCHEMA, "package_index": spec.package_index, "base": spec.base, "target": spec.target,
                "target_tree": spec.target_tree, "target_path": str(roots["target"]),
                "package_path": str(roots["package"]), "txn_path": str(roots["txn"])}
    for key, value in expected.items():
        if j.get(key) != value:
            raise Rejected(f"journal {key} does not match this invocation/accepted spec")
    if not (isinstance(j.get("txn_id"), str) and len(j["txn_id"]) == 32 and j["txn_id"].isalnum()):
        raise Rejected("journal txn_id invalid")
    if j.get("temp_ref") != f"refs/paperclip-overlay/{j['txn_id']}" or not str(j.get("branch_ref", "")).startswith("refs/heads/"):
        raise Rejected("journal Git identities invalid")
    if j.get("branch_oid") != spec.base or ".." in j["branch_ref"] or j["branch_ref"].endswith(".lock"):
        raise Rejected("journal branch identity invalid")
    if j.get("phase") not in PHASES or not j.get("history") or j["history"][-1] != j["phase"]:
        raise Rejected("journal phase invalid")
    if j.get("outputs") != list(spec.outputs):
        raise Rejected("journal outputs do not match the accepted spec")
    return j


PHASES = ("apply-begun", "apply-staged", "apply-fetched", "apply-sources-switched", "apply-outputs-switched",
          "apply-git-switched", "apply-complete", "rollback-begun", "rollback-git-restored",
          "rollback-sources-restored", "rollback-outputs-restored", "rollback-complete")


def crlf(data):
    return data if b"\0" in data or b"\r" in data else data.replace(b"\n", b"\r\n")


# ---------------------------------------------------------------- operations
def prologue(target, package, txn=None):
    refuse_inherited_git()
    roots = check_roots(target, package, txn)
    enable_test_hooks(roots["target"])
    return roots, Git(roots["target"], roots)


def preflight(target, package, spec=ACCEPTED):
    roots, git = prologue(target, package)
    with TargetLock(roots["target"]):
        emitted, sources = load_package(roots["package"], spec)
        check_repo(git, roots["target"], list(sources))
        s = classify(git, roots["target"], spec, emitted, sources)
    if s["is_new"]:
        return {"status": "ALREADY_APPLIED", "owner": s["owner"]}
    if not s["is_old"]:
        raise Rejected("baseline/preimage mismatch: " + json.dumps(_mismatch(s)))
    return {"status": "READY"}


def _mismatch(s):
    return {k: s[k] for k in ("head", "index", "owner", "overlay_refs", "tracked_changes", "pinned_ok")} | {
        "sources": {k: v for k, v in s["sources"].items() if v not in ("old",)},
        "outputs": s["outputs"]}


def apply(target, package, txn, spec=ACCEPTED):
    roots, git = prologue(target, package, txn)
    T, P, X = roots["target"], roots["package"], roots["txn"]
    with TargetLock(T):
        emitted, sources = load_package(P, spec)
        check_repo(git, T, list(sources))
        s = classify(git, T, spec, emitted, sources)
        if s["is_new"]:
            return {"status": "ALREADY_APPLIED", "owner": s["owner"], "writes": 0}
        if not s["is_old"]:
            raise Rejected("baseline/preimage mismatch: " + json.dumps(_mismatch(s)))
        if X.exists():
            raise Rejected("transaction directory already exists; use recover or rollback with it")
        for path in sources:  # every source write path must be plain and its parent present
            plain(T / path, must_exist=(sources[path][0] != "absent"))
            plain((T / path).parent)
        txn_id = uuid.uuid4().hex
        creating = X.parent / f".{X.name}.creating-{txn_id}"
        creating.mkdir()
        journal = {"schema": SCHEMA, "txn_id": txn_id, "package_index": spec.package_index, "base": spec.base,
                   "target": spec.target, "target_tree": spec.target_tree, "target_path": str(T),
                   "package_path": str(P), "txn_path": str(X), "branch_ref": s["head_symbolic"],
                   "branch_oid": spec.base, "temp_ref": f"refs/paperclip-overlay/{txn_id}",
                   "outputs": list(spec.outputs), "sources": sorted(sources), "history": []}
        write_journal(creating, journal, "apply-begun")
        checkpoint("apply:creating")
        os.rename(creating, X)  # X appears only together with its first journal
        checkpoint("apply:begun")
        atomic_write(T / ".git" / "paperclip-overlay-owner.json",
                     json.dumps({"txn_id": txn_id, "txn_path": str(X)}).encode("utf-8"))
        checkpoint("apply:owned")
        for path, (old, _) in sources.items():
            if old != "absent":
                dest = X / "src-old" / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                if durable_copy(plain(T / path), dest) != old or sha_file(dest) != old:
                    raise RuntimeError(f"source backup not exact: {path}")
        for o in spec.outputs:
            shutil.copytree(P / "artifacts" / o, X / "new" / o)
            if scan_tree(X / "new" / o) != emitted[o]["new"]:
                raise RuntimeError(f"staged {o} not exact")
        write_journal(X, journal, "apply-staged")
        checkpoint("apply:staged")
        git.run("fetch", "--no-tags", "--no-write-fetch-head", str(P / spec.bundle), f"{spec.bundle_ref}:{journal['temp_ref']}")
        if git.value("rev-parse", journal["temp_ref"]) != spec.target or git.value("rev-parse", f"{spec.target}^{{tree}}") != spec.target_tree:
            raise RuntimeError("bundle did not provide the accepted commit/tree")
        for path, (_, new) in sources.items():
            data = crlf(git.run("cat-file", "blob", f"{spec.target}:{path}", binary=True))
            if hashlib.sha256(data).hexdigest() != new:
                raise RuntimeError(f"computed afterimage differs from the package: {path}")
            dest = X / "src-new" / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            durable_write(dest, data)
        write_journal(X, journal, "apply-fetched")
        checkpoint("apply:fetched")
        for path in sources:
            os.replace(X / "src-new" / path, T / path)
            checkpoint(f"apply:source:{path}")
        write_journal(X, journal, "apply-sources-switched")
        for o in spec.outputs:
            (X / "parked" / o).parent.mkdir(parents=True, exist_ok=True)
            os.rename(T / o, X / "parked" / o)
            checkpoint(f"apply:output-parked:{o}")
            os.rename(X / "new" / o, T / o)
            checkpoint(f"apply:output-installed:{o}")
        write_journal(X, journal, "apply-outputs-switched")
        git.run("update-ref", "--no-deref", "HEAD", spec.target, spec.base)
        checkpoint("apply:head")
        git.run("read-tree", spec.target)
        checkpoint("apply:index")
        git.run("update-ref", "-d", journal["temp_ref"], spec.target)
        checkpoint("apply:temp-ref-deleted")
        write_journal(X, journal, "apply-git-switched")
        s = classify(git, T, spec, emitted, sources, txn_id, journal["branch_ref"])
        if not s["is_new"]:
            raise RuntimeError("postimage verification failed: " + json.dumps(_mismatch(s)))
        write_journal(X, journal, "apply-complete")
    return {"status": "APPLIED", "txn": str(X), "txn_id": txn_id}


def _restorable(s, X, journal, spec, emitted, sources):
    """Every component must be old, new or an owned transient that this transaction can restore."""
    problems = []
    phase, txn_id = journal["phase"], journal["txn_id"]
    in_rollback = phase.startswith("rollback-")
    if phase == "apply-complete" and not s["is_new"]:
        problems.append("journal says apply-complete but the target is not exactly this transaction's applied state")
    if not s["pinned_ok"]:
        problems.append("pinned deployed file bytes differ")
    if s["branch_ref"] != journal["branch_ref"] or s["branch_oid"] != spec.base:
        problems.append("original branch moved or renamed")
    if s["head"] == "foreign":
        problems.append("HEAD is neither the original branch at BASE nor detached at TARGET")
    if s["index"] == "foreign":
        problems.append("index matches neither BASE nor TARGET")
    released = X / "owner-released.json"
    released_by_us = released.is_file() and json.loads(plain(released).read_text(encoding="utf-8")).get("txn_id") == txn_id
    if s["owner"] is None:
        if not (phase == "apply-begun" or (in_rollback and released_by_us)):
            problems.append("owner marker missing although this transaction had taken ownership")
    elif s["owner"] != txn_id:
        problems.append("target owned by another transaction")
    for ref, oid in s["overlay_refs"].items():
        if ref != journal["temp_ref"] or oid != spec.target:
            problems.append(f"foreign overlay ref {ref}")
    if s["tracked_changes"]:
        extra = [p for p in s["tracked_changes"] if p not in sources]
        if extra:
            problems.append(f"tracked changes outside the overlay: {extra[:5]}")
    # A missing source or output is restorable only when this transaction's own move explains it: the
    # displaced afterimage sits, exact, in this transaction's evidence slot. Anything else is unowned.
    history = journal["history"]
    for path, state in s["sources"].items():
        old, new = sources[path]
        displaced = plain(X / "rb-src" / path, must_exist=False, missing_parents=True)
        if state == "foreign":
            problems.append(f"source changed after the transaction: {path}")
            continue
        if state == "missing" and old != "absent" and not (in_rollback and sha_file_or(displaced) == new):
            problems.append(f"source {path} missing without this transaction's rollback move (rb-src)")
        if state in ("new", "missing") and old != "absent" and sha_file_or(X / "src-old" / path) != old:
            problems.append(f"no exact backup to restore {path}")
        if state == "new" and displaced.exists():
            problems.append(f"rollback evidence slot already used: rb-src/{path}")
    for o, state in s["outputs"].items():
        displaced = plain(X / "rb-out" / o, must_exist=False, missing_parents=True)
        if state == "foreign":
            problems.append(f"{o} changed after the transaction")
            continue
        if state == "missing":
            # apply parked the old tree but had not installed new/<o> yet; or rollback moved new to rb-out/<o>
            apply_move = ("apply-sources-switched" in history and "apply-outputs-switched" not in history
                          and scan_tree(X / "new" / o) == emitted[o]["new"])
            rollback_move = in_rollback and scan_tree(displaced) == emitted[o]["new"]
            if not (apply_move or rollback_move):
                problems.append(f"{o} missing without this transaction's output move (new or rb-out)")
        if state in ("new", "missing") and scan_tree(X / "parked" / o) != emitted[o]["old"]:
            problems.append(f"no exact parked {o} to restore")
        if state == "new" and displaced.exists():
            problems.append(f"rollback evidence slot already used: rb-out/{o}")
    return problems


def sha_file_or(path):
    path = plain(path, must_exist=False, missing_parents=True)
    return sha_file(path) if path.is_file() else None


def rollback(target, package, txn, spec=ACCEPTED, *, from_recover=False):
    roots, git = prologue(target, package, txn)
    T, P, X = roots["target"], roots["package"], roots["txn"]
    with TargetLock(T):
        emitted, sources = load_package(P, spec)
        journal = load_journal(X, roots, spec)
        check_repo(git, T, list(sources))
        s = classify(git, T, spec, emitted, sources, journal["txn_id"], journal["branch_ref"])
        phase = journal["phase"]
        if phase == "rollback-complete":
            if s["is_old"]:
                return {"status": "ALREADY_ROLLED_BACK", "writes": 0}
            raise Rejected("transaction already rolled back; the target no longer belongs to it")
        if phase == "apply-complete" and from_recover:
            if s["is_new"]:
                return {"status": "NOTHING_TO_RECOVER", "phase": phase, "verified": "applied state exact"}
            raise Inconsistent("journal says apply-complete but the target is not exactly this transaction's "
                               "applied state: " + json.dumps(_mismatch(s)))
        problems = _restorable(s, X, journal, spec, emitted, sources)
        if problems:
            raise Rejected("rollback refused, nothing written: " + "; ".join(problems))
        if not phase.startswith("rollback-"):
            write_journal(X, journal, "rollback-begun")
        checkpoint("rollback:begun")
        # 1. Git metadata
        if s["head"] == "new":
            git.run("symbolic-ref", "HEAD", journal["branch_ref"])
            checkpoint("rollback:head")
        if git.value("rev-parse", "HEAD") != spec.base:
            raise RuntimeError("HEAD does not resolve to BASE after restoring the branch")
        if not git.ok("diff-index", "--cached", "--quiet", spec.base, "--"):
            git.run("read-tree", spec.base)
            checkpoint("rollback:index")
        write_journal(X, journal, "rollback-git-restored")
        # 2. Sources
        for path, (old, new) in sources.items():
            p = T / path
            if p.exists() and sha_file(p) == new:
                dest = X / "rb-src" / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    raise RuntimeError(f"rollback evidence slot already used: {dest}")
                os.replace(p, dest)
                checkpoint(f"rollback:source-out:{path}")
            if old != "absent" and not p.exists():
                os.replace(plain(X / "src-old" / path), p)
                checkpoint(f"rollback:source-in:{path}")
        write_journal(X, journal, "rollback-sources-restored")
        # 3. Outputs
        for o in spec.outputs:
            current = scan_tree(T / o)
            if current == emitted[o]["new"]:
                (X / "rb-out" / o).parent.mkdir(parents=True, exist_ok=True)
                if (X / "rb-out" / o).exists():
                    raise RuntimeError(f"rollback evidence slot already used: rb-out/{o}")
                os.rename(T / o, X / "rb-out" / o)
                checkpoint(f"rollback:output-out:{o}")
                current = None
            if current is None:
                os.rename(X / "parked" / o, T / o)
                checkpoint(f"rollback:output-in:{o}")
        write_journal(X, journal, "rollback-outputs-restored")
        # 4. Owned temp ref and owner marker
        if git.value("rev-parse", "--verify", "-q", journal["temp_ref"]) == spec.target:
            git.run("update-ref", "-d", journal["temp_ref"], spec.target)
            checkpoint("rollback:temp-ref-deleted")
        if read_owner(T) == journal["txn_id"]:
            os.replace(plain(T / ".git" / "paperclip-overlay-owner.json"), X / "owner-released.json")
            checkpoint("rollback:owner-released")
        s = classify(git, T, spec, emitted, sources, branch_ref=journal["branch_ref"])
        if not s["is_old"]:
            raise RuntimeError("rollback verification failed: " + json.dumps(_mismatch(s)))
        write_journal(X, journal, "rollback-complete")
    return {"status": "ROLLED_BACK", "txn": str(X)}


def recover(target, package, txn, spec=ACCEPTED):
    """Interrupted apply -> roll back; interrupted rollback -> resume; terminal phases are verified, not assumed."""
    return rollback(target, package, txn, spec, from_recover=True)


def main(argv, spec=ACCEPTED):
    if not argv or argv[0] not in ("preflight", "apply", "rollback", "recover") or len(argv) != (3 if argv[0] == "preflight" else 4):
        print(__doc__)
        return 64
    command, *args = argv
    try:
        result = {"preflight": preflight, "apply": apply, "rollback": rollback, "recover": recover}[command](*args, spec=spec)
        print(json.dumps(result))
        return 0
    except Rejected as error:
        print(json.dumps({"status": "REJECTED", "reason": str(error)}))
        return 2
    except Inconsistent as error:
        print(json.dumps({"status": "INCONSISTENT", "reason": str(error)}))
        return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
