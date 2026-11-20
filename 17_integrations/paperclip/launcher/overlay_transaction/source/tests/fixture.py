"""Small real fixtures for the overlay helper: a Git target at BASE, a package (bundle, artifacts, TSVs and
index in the accepted format) carrying TARGET, and the matching Spec. Synthetic content only."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
HELPER_DIR = HERE.parent
sys.path.insert(0, str(HELPER_DIR))
import paperclip_overlay as h  # noqa: E402

FIXTURE_ROOT = Path(os.environ.get("OVERLAY_FIXTURE_ROOT", HELPER_DIR.parent / "pfx"))
BRANCH = "fix/base-branch"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def clean_env(**extra):
    """Caller environment for the helper: the launcher contract requires no inherited GIT_* variables."""
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    env.update(extra)
    return env


def git(cwd, *args, env=None):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True,
                          env=env or clean_env()).stdout.strip()


def write(path, text, crlf=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode("utf-8")
    path.write_bytes(data.replace(b"\n", b"\r\n") if crlf else data)


class Fixture:
    def __init__(self, name):
        FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix=name[:20] + "-", dir=FIXTURE_ROOT))
        self.builder, self.target, self.package = self.root / "b", self.root / "t", self.root / "p"
        self._build()

    def _build(self):
        b = self.builder
        b.mkdir()
        git(b, "init", "-q", "-b", "base")
        git(b, "config", "user.name", "fixture")
        git(b, "config", "user.email", "fixture@example.invalid")
        git(b, "config", "core.autocrlf", "false")
        write(b / ".gitignore", "dist/\n")
        write(b / "src/a.txt", "alpha\nbase\n")
        write(b / "src/b.txt", "bravo\nunchanged\n")
        write(b / "src/pinned.txt", "pinned\nbytes\n")
        write(b / "src/lf-deployed.txt", "deployed\nas\nlf\n")
        git(b, "add", "-A")
        git(b, "commit", "-q", "-m", "base")
        self.base = git(b, "rev-parse", "HEAD")
        git(b, "checkout", "-q", "-b", "release")
        write(b / "src/a.txt", "alpha\ntarget\nchanged\n")
        write(b / "src/new.txt", "new\nfile\n")
        git(b, "add", "-A")
        git(b, "commit", "-q", "-m", "target")
        self.target_commit = git(b, "rev-parse", "HEAD")
        # Target: clone of BASE only, autocrlf=true like the intake, on a named branch.
        t = self.target
        subprocess.run(["git", "-c", "core.autocrlf=true", "clone", "-q", "--single-branch", "-b", "base",
                        "--no-local", str(b), str(t)], check=True, capture_output=True, env=clean_env())
        git(t, "config", "core.autocrlf", "true")
        git(t, "checkout", "-q", "-b", BRANCH)
        git(t, "remote", "remove", "origin")
        git(t, "branch", "-D", "base")
        # A deployed file kept as LF bytes (content-equal), like the intake's 11 files.
        (t / "src/lf-deployed.txt").write_bytes(b"deployed\nas\nlf\n")
        # Untracked built outputs (old) and a sentinel.
        write(t / "ui/dist/index.html", '<script src="/assets/old-1111.js"></script>\n')
        write(t / "ui/dist/assets/old-1111.js", "console.log('old')\n")
        write(t / "cli/dist/index.js", "// old cli\n")
        write(t / "UNTRACKED_SENTINEL.txt", "sentinel\n")
        (t / ".git/paperclip-overlay-test-staging").write_text("fixture\n")  # enables test hooks here only
        # Package.
        p = self.package
        write(p / "artifacts/ui/dist/index.html", '<script src="/assets/new-2222.js"></script>\n')
        write(p / "artifacts/ui/dist/assets/new-2222.js", "console.log('new')\n")
        write(p / "artifacts/cli/dist/index.js", "// new cli\n")
        (p / "source").mkdir(parents=True)
        subprocess.run(["git", "-C", str(b), "bundle", "create", str(p / "source/fixture.bundle"),
                        f"{self.base}..release"], check=True, capture_output=True, env=clean_env())
        rows = ["artifact\tpath\tsize\tnew_sha256\tinstalled_sha256\tstatus"]
        for o in ("ui/dist", "cli/dist"):
            new = {q.relative_to(p / "artifacts" / o).as_posix(): sha(q.read_bytes())
                   for q in (p / "artifacts" / o).rglob("*") if q.is_file()}
            old = {q.relative_to(t / o).as_posix(): sha(q.read_bytes()) for q in (t / o).rglob("*") if q.is_file()}
            for rel in sorted(set(new) | set(old)):
                rows.append("\t".join([o, rel, "-", new.get(rel, "absent"), old.get(rel, "absent"), "x"]))
        write(p / "EMITTED_FILES.tsv", "\n".join(rows) + "\n")
        rows = ["path\tblob_base\tinstalled_raw_sha256\tblob_target\tgit_lf_sha256\texpected_installed_sha256(autocrlf=true)"]
        for path in ("src/a.txt", "src/new.txt"):
            blob = subprocess.run(["git", "-C", str(b), "show", f"{self.target_commit}:{path}"], capture_output=True,
                                  check=True, env=clean_env()).stdout
            installed = sha((t / path).read_bytes()) if (t / path).exists() else "absent"
            rows.append("\t".join([path, "-", installed, "-", sha(blob), sha(h.crlf(blob))]))
        write(p / "SOURCE_FILES.tsv", "\n".join(rows) + "\n")
        members = sorted(q for q in p.rglob("*") if q.is_file())
        (p / "PACKAGE_SHA256.txt").write_text(
            "".join(f"{sha(q.read_bytes())} *./{q.relative_to(p).as_posix()}\n" for q in members), encoding="utf-8")
        self.spec = h.Spec(
            package_index=sha((p / "PACKAGE_SHA256.txt").read_bytes()),
            base=self.base, base_tree=git(b, "rev-parse", f"{self.base}^{{tree}}"),
            target=self.target_commit, target_tree=git(b, "rev-parse", f"{self.target_commit}^{{tree}}"),
            bundle="source/fixture.bundle", bundle_ref="release",
            pinned={"src/pinned.txt": sha((t / "src/pinned.txt").read_bytes())})
        self.spec_file = self.root / "spec.json"
        spec = dict(self.spec.__dict__)
        spec["allowed_tracked_changes"] = sorted(spec["allowed_tracked_changes"])
        spec["outputs"] = list(spec["outputs"])
        self.spec_file.write_text(json.dumps(spec), encoding="utf-8")

    def txn(self, name):
        return self.root / name

    def run(self, command, txn=None, env=None, package=None, target=None, timeout=120):
        argv = [sys.executable, "-I", str(HERE / "run_with_spec.py"), str(self.spec_file), command,
                str(target or self.target), str(package or self.package)] + ([str(txn)] if txn else [])
        r = subprocess.run(argv, capture_output=True, text=True, env=env or clean_env(), timeout=timeout)
        out = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
        try:
            parsed = json.loads(out)
        except ValueError:
            parsed = {"raw": out}
        return r.returncode, parsed, r.stderr

    def snapshot(self):
        """Raw bytes of every work-tree file (outside .git), Git identity and refs, and index entries."""
        files = {}
        for dirpath, dirnames, filenames in os.walk(self.target):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            for n in filenames:
                q = Path(dirpath, n)
                files[q.relative_to(self.target).as_posix()] = sha(q.read_bytes())
        g = lambda *a: subprocess.run(["git", "-C", str(self.target), *a], capture_output=True, text=True,
                                      env=clean_env(GIT_OPTIONAL_LOCKS="0")).stdout.strip()
        marker = self.target / ".git/paperclip-overlay-owner.json"
        return {"files": files, "head_symbolic": g("symbolic-ref", "-q", "HEAD"), "head": g("rev-parse", "HEAD"),
                "refs": g("for-each-ref", "--format=%(refname) %(objectname)"),
                "index": g("ls-files", "-s"), "owner": marker.read_text() if marker.exists() else None}
