"""Final rehearsal of the overlay transaction against a staged target, with an enforced aggregate gate.

    python -I rehearse.py <staging-root> <package> <wrong-package-dir> <launcher-candidate> <installed-launcher> <native-helper-root> <report.json>

Every scenario has a unique id, a kind and a required predicate. The run passes only if every required
scenario ran and its predicate held; a failed predicate, an exception, a missing scenario, a duplicate or an
unexpected id makes the process exit 1. Report observations are evidence, never the verdict on their own.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PY = sys.executable
HELPER = HERE / "paperclip_overlay.py"
CANDIDATE_SHA = "eb39b400f2a35a640072b7e98046c671930422b3095a74d2ac606e560cd91fff"
INSTALLED_SHA = "677ceb55e017cccab0753bad537bad3c9c6bb8f38241419af9e467353fa48744"
BASE, TARGET, TARGET_TREE = ("e04e2ae1a0d47cdedf5380b5a0d94f280a82d5d1", "e8ad1fd98142e6a4f53172f143381a4fa4100dd7",
                             "bdab2ce706f3e682781ad0e93da935155b937867")
KINDS = {"check", "rejection", "application", "replay", "interruption", "recovery", "launcher"}


# ---------------------------------------------------------------- gate (pure; unit-tested)
def evaluate(required, results):
    """required: ordered list of ids. results: list of {"id","status"} with status PASS/FAIL/ERROR."""
    seen, problems = {}, []
    for r in results:
        if r["id"] in seen:
            problems.append(f"duplicate scenario {r['id']}")
        seen[r["id"]] = r["status"]
    for sid in required:
        if sid not in seen:
            problems.append(f"missing scenario {sid}")
        elif seen[sid] != "PASS":
            problems.append(f"{sid} {seen[sid]}")
    for sid in seen:
        if sid not in required:
            problems.append(f"unexpected scenario {sid}")
    return {"verdict": "PASS" if not problems and required else "FAIL", "problems": problems}


def run_scenarios(scenarios, required, stop_on_error=False):
    """scenarios: list of (id, kind, fn). fn returns (ok, observation). Exceptions are ERROR, never PASS."""
    results = []
    for sid, kind, fn in scenarios:
        if kind not in KINDS:
            results.append({"id": sid, "kind": kind, "status": "ERROR", "reason": "unknown kind"})
            continue
        started = time.monotonic()
        try:
            ok, observation = fn()
            status = "PASS" if ok is True else "FAIL"
            results.append({"id": sid, "kind": kind, "status": status, "observation": observation})
        except Exception as error:  # noqa: BLE001 - recorded, never counted as a pass
            results.append({"id": sid, "kind": kind, "status": "ERROR", "reason": f"{type(error).__name__}: {error}"})
            if stop_on_error:
                break
        results[-1]["seconds"] = round(time.monotonic() - started, 1)
        print(json.dumps({k: results[-1][k] for k in ("id", "kind", "status")}), flush=True)
    return results, evaluate(required, results)


# ---------------------------------------------------------------- staged target helpers
def env_without_git(**extra):
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    env.update(extra)
    return env


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Stage:
    def __init__(self, root, package, wrong_package, candidate, installed, native):
        self.root, self.t, self.state = Path(root), Path(root) / "t", Path(root) / "state"
        self.package, self.wrong_package = Path(package), Path(wrong_package)
        self.candidate, self.installed, self.native = candidate, installed, native
        self.sources = [line.split("\t")[0] for line in (self.package / "SOURCE_FILES.tsv").read_text().splitlines()[1:]]
        self.removed_git_env = sorted(k for k in os.environ if k.upper().startswith("GIT_"))

    def helper(self, command, txn=None, package=None, env=None, timeout=900):
        argv = [PY, "-I", str(HELPER), command, str(self.t), str(package or self.package)] + ([str(txn)] if txn else [])
        r = subprocess.run(argv, capture_output=True, text=True, env=env or env_without_git(), timeout=timeout)
        out = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "{}"
        try:
            parsed = json.loads(out)
        except ValueError:
            parsed = {"raw": out}
        return {"exit": r.returncode, "out": parsed, "stderr": r.stderr.strip()[-400:]}

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.t), *args], capture_output=True, text=True,
                              env=env_without_git(GIT_OPTIONAL_LOCKS="0")).stdout.strip()

    def identity(self):
        marker = self.t / ".git/paperclip-overlay-owner.json"
        return {"head_symbolic": self.git("symbolic-ref", "-q", "HEAD"), "head": self.git("rev-parse", "HEAD"),
                "refs": self.git("for-each-ref", "--format=%(refname) %(objectname)"),
                "index": hashlib.sha256(self.git("ls-files", "-s").encode()).hexdigest(),
                "owner": marker.read_text() if marker.exists() else None}

    def mutable(self):
        """Every path the transaction can write, plus Git identity, sentinels and synthetic state."""
        files = {}
        for rel in self.sources + ["server/src/adapters/utils.ts", "packages/adapter-utils/src/service-declarations.test.ts",
                                   ".cache/sentinel.txt", "server/node-compile-cache/sentinel.txt", "UNTRACKED_SENTINEL.txt"]:
            p = self.t / rel
            files[rel] = sha(p) if p.exists() else None
        for o in ("ui/dist", "cli/dist"):
            for p in sorted((self.t / o).rglob("*")) if (self.t / o).exists() else []:
                if p.is_file():
                    files[p.relative_to(self.t).as_posix()] = sha(p)
        for p in sorted(self.state.rglob("*")):
            if p.is_file():
                files["state/" + p.relative_to(self.state).as_posix()] = sha(p)
        return {"files": files, **self.identity()}

    def full(self):
        """Raw bytes of every staged file outside .git and node_modules, plus identity."""
        files = {}
        for base, label in ((self.t, "t"), (self.state, "state")):
            for dirpath, dirnames, filenames in os.walk(base):
                dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
                for n in filenames:
                    p = Path(dirpath, n)
                    files[f"{label}/{p.relative_to(base).as_posix()}"] = sha(p)
        return {"files": files, **self.identity()}

    def launcher(self, path, digest):
        r = subprocess.run([PY, "-I", str(HERE / "launcher_preflight.py"), path, digest, str(self.t), str(self.state),
                            str(self.native)], capture_output=True, text=True, env=env_without_git())
        return json.loads(r.stdout.strip().splitlines()[-1])


def diff(a, b):
    keys = set(a["files"]) | set(b["files"])
    files = sorted(k for k in keys if a["files"].get(k) != b["files"].get(k))
    other = sorted(k for k in a if k != "files" and a[k] != b[k])
    return files, other


# ---------------------------------------------------------------- the final rehearsal
def build(stage):
    ctx = {}
    s = stage

    def rejection(make, cleanup, txn_name, package=None, env=None):
        def fn():
            before = s.mutable()
            make()
            probe = s.mutable()
            txn = s.root / txn_name
            r = s.helper("apply", txn, package=package, env=env)
            after = s.mutable()
            cleanup()
            restored = s.mutable()
            files, other = diff(probe, after)
            ok = (r["exit"] == 2 and r["out"].get("status") == "REJECTED" and not txn.exists()
                  and not files and not other and diff(before, restored) == ([], []))
            return ok, {"helper": r, "changed": files, "identity_changed": other}
        return fn

    def noop():
        pass

    tampered = s.t / "ui/dist/index.html"
    pinned = s.t / "server/src/adapters/utils.ts"
    stale = s.t / "ui/dist/assets/index-STALE000.js"
    saved = {}

    def tamper():
        saved["idx"] = tampered.read_bytes()
        tampered.write_bytes(saved["idx"] + b"\n<!-- tampered -->\n")

    def untamper():
        tampered.write_bytes(saved["idx"])

    def lf_pinned():
        saved["pin"] = pinned.read_bytes()
        pinned.write_bytes(saved["pin"].replace(b"\r\n", b"\n"))

    def restore_pinned():
        pinned.write_bytes(saved["pin"])

    def add_stale():
        stale.write_bytes(b"// stale\n")

    def remove_stale():
        stale.unlink()

    def s01():
        ctx["baseline"], ctx["baseline_m"] = s.full(), s.mutable()
        r = s.helper("preflight")
        return r["exit"] == 0 and r["out"].get("status") == "READY", {"helper": r, "files": len(ctx["baseline"]["files"])}

    def s08():
        txn = s.root / "rh-apply"
        r = s.helper("apply", txn)
        ctx["applied"], ctx["applied_m"] = s.full(), s.mutable()
        files, other = diff(ctx["baseline"], ctx["applied"])
        ident = ctx["applied"]
        ok = (r["exit"] == 0 and r["out"].get("status") == "APPLIED" and len(files) == 149
              and ident["head"] == TARGET and ident["head_symbolic"] == "" and ident["owner"] is not None
              and s.git("rev-parse", "HEAD^{tree}") == TARGET_TREE and "paperclip-overlay" not in ident["refs"]
              and f"refs/heads/fix/ghoti-company-cache-shape {BASE}" in ident["refs"]
              and not (s.t / "ui/dist/assets/index-dTuk29mb.js").exists())
        return ok, {"helper": r, "changed_paths": len(files), "identity_changed": other}

    def s09():
        before = s.mutable()
        r = s.helper("apply", s.root / "rh-replay")
        files, other = diff(before, s.mutable())
        ok = (r["exit"] == 0 and r["out"].get("status") == "ALREADY_APPLIED" and not files and not other
              and not (s.root / "rh-replay").exists())
        return ok, {"helper": r}

    def s10():
        new, old = s.launcher(s.candidate, CANDIDATE_SHA), s.launcher(s.installed, INSTALLED_SHA)
        ok = (new["result"] == "PASS" and new["revision"] == TARGET and old["result"] == "REFUSED"
              and "revision changed" in old["message"] and new["layout"]["server_ui_dist_present"] is False
              and new["layout"]["entry_chunks_referenced_by_index_html"] == ["index-CMx55bgr.js"]
              and new["layout"]["old_entry_chunk_present"] is False)
        return ok, {"candidate": new, "installed": old}

    later = s.t / "ui/dist/later-work.txt"

    def s11():
        later.write_text("later work")
        before = s.mutable()
        journal = (s.root / "rh-apply/journal.json").read_bytes()
        r = s.helper("rollback", s.root / "rh-apply")
        files, other = diff(before, s.mutable())
        ok = (r["exit"] == 2 and not files and not other and (s.root / "rh-apply/journal.json").read_bytes() == journal
              and later.exists())
        later.unlink()  # remove only the file this scenario added
        return ok and s.mutable() == ctx["applied_m"], {"helper": r}

    def s12():
        txn, ready = s.root / "rh-apply", s.root / "rh-kill-ready.txt"
        env = env_without_git(PAPERCLIP_OVERLAY_TEST_PAUSE_AT="rollback:output-out:ui/dist",
                              PAPERCLIP_OVERLAY_TEST_PAUSE_FILE=str(ready))
        proc = subprocess.Popen([PY, "-I", str(HELPER), "rollback", str(s.t), str(s.package), str(txn)], env=env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.time() + 600
        while not ready.exists() and proc.poll() is None and time.time() < deadline:
            time.sleep(0.5)
        reached = ready.exists()
        kill = subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)], capture_output=True, text=True)
        code = proc.wait(60)
        phase = json.loads((txn / "journal.json").read_text())["phase"]
        observed = {"reached_boundary": reached, "taskkill": kill.returncode, "exit_code": code, "journal_phase": phase,
                    "ui_dist_present": (s.t / "ui/dist").exists(), "rb_out_present": (txn / "rb-out/ui/dist").exists(),
                    "parked_present": (txn / "parked/ui/dist").exists()}
        ctx["kill"] = observed
        ok = (reached and kill.returncode == 0 and code != 0 and phase.startswith("rollback-")
              and not observed["ui_dist_present"] and observed["rb_out_present"] and observed["parked_present"])
        return ok, observed

    def s13():
        r = s.helper("recover", s.root / "rh-apply")
        ctx["recovered"] = s.full()
        files, other = diff(ctx["baseline"], ctx["recovered"])
        ok = r["exit"] == 0 and r["out"].get("status") == "ROLLED_BACK" and not files and not other
        return ok, {"helper": r, "raw_differences": len(files), "identity_differences": other,
                    "branch": ctx["recovered"]["head_symbolic"]}

    def s14():
        r = s.helper("recover", s.root / "rh-apply")
        return r["exit"] == 0 and r["out"].get("status") == "ALREADY_ROLLED_BACK", {"helper": r}

    def s15():
        new, old = s.launcher(s.candidate, CANDIDATE_SHA), s.launcher(s.installed, INSTALLED_SHA)
        ok = (old["result"] == "PASS" and old["revision"] == BASE and new["result"] == "REFUSED"
              and old["layout"]["entry_chunks_referenced_by_index_html"] == ["index-dTuk29mb.js"])
        return ok, {"candidate": new, "installed": old}

    def s16():
        txn = s.root / "rh-int-apply"
        r1 = s.helper("apply", txn, env=env_without_git(PAPERCLIP_OVERLAY_TEST_STOP_AT="apply:output-installed:ui/dist"))
        r2 = s.helper("recover", txn)
        files, other = diff(ctx["baseline_m"], s.mutable())
        ok = r1["exit"] == 75 and r2["exit"] == 0 and r2["out"].get("status") == "ROLLED_BACK" and not files and not other
        return ok, {"interrupted": r1, "recover": r2, "mutable_differences": files, "identity_differences": other}

    def s17():
        txn = s.root / "rh-final"
        r = s.helper("apply", txn)
        final = s.full()
        files, other = diff(ctx["applied"], final)
        ok = r["exit"] == 0 and r["out"].get("status") == "APPLIED" and not files and other == ["owner"]
        return ok, {"helper": r, "differences_from_first_application": files, "identity_differences": other}

    def s18():
        before = s.mutable()
        r = s.helper("rollback", s.root / "rh-apply")
        files, other = diff(before, s.mutable())
        return r["exit"] == 2 and not files and not other, {"helper": r}

    scenarios = [
        ("S01-preflight-baseline", "check", s01),
        ("S02-reject-tampered-ui-index", "rejection", rejection(tamper, untamper, "rh-r2")),
        ("S03-reject-pinned-file-lf", "rejection", rejection(lf_pinned, restore_pinned, "rh-r3")),
        ("S04-reject-stale-extra-chunk", "rejection", rejection(add_stale, remove_stale, "rh-r4")),
        ("S05-reject-wrong-package", "rejection", rejection(noop, noop, "rh-r5", package=s.wrong_package)),
        ("S06-reject-txn-inside-package", "rejection", rejection_txn_inside_package(s)),
        ("S07-reject-inherited-git-dir", "rejection", rejection(noop, noop, "rh-r7",
                                                                env=env_without_git(GIT_DIR=str(s.t / ".git")))),
        ("S08-apply", "application", s08),
        ("S09-replay-apply", "replay", s09),
        ("S10-launcher-on-applied", "launcher", s10),
        ("S11-later-work-blocks-rollback", "rejection", s11),
        ("S12-real-kill-during-rollback", "interruption", s12),
        ("S13-recover-after-kill", "recovery", s13),
        ("S14-replay-recover", "replay", s14),
        ("S15-launcher-on-baseline", "launcher", s15),
        ("S16-interrupted-apply-recovers", "recovery", s16),
        ("S17-final-apply-identical", "application", s17),
        ("S18-stale-txn-cannot-touch-later-install", "rejection", s18),
    ]
    return scenarios


def rejection_txn_inside_package(s):
    def fn():
        before = s.mutable()
        pkg_before = sorted((p.relative_to(s.package).as_posix(), sha(p)) for p in s.package.rglob("*") if p.is_file())
        txn = s.package / "rh-r6"
        r = s.helper("apply", txn)
        files, other = diff(before, s.mutable())
        pkg_after = sorted((p.relative_to(s.package).as_posix(), sha(p)) for p in s.package.rglob("*") if p.is_file())
        ok = r["exit"] == 2 and not txn.exists() and pkg_before == pkg_after and not files and not other
        return ok, {"helper": r}
    return fn


def main(root, package, wrong_package, candidate, installed, native, out):
    stage = Stage(root, package, wrong_package, candidate, installed, native)
    scenarios = build(stage)
    required = [sid for sid, _, _ in scenarios]
    skip = os.environ.get("REHEARSE_TEST_OMIT")  # gate self-test only: omit a scenario on purpose
    if skip:
        scenarios = [sc for sc in scenarios if sc[0] != skip]
    results, gate = run_scenarios(scenarios, required)
    report = {"helper_sha256": sha(HELPER), "driver_sha256": sha(Path(__file__)), "staging_root": str(stage.root),
              "package": str(stage.package), "removed_inherited_git_env": stage.removed_git_env,
              "required": required, "results": results, "gate": gate}
    Path(out).write_text(json.dumps(report, indent=1, default=str), encoding="utf-8")
    print(json.dumps(gate))
    return 0 if gate["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
