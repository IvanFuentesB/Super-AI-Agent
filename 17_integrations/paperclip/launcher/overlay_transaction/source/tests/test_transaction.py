"""Regression tests for the overlay transaction (findings I1-I7 of the independent review, and the executed
interrupted-rollback failure). Real Git fixtures and real processes; crashes are real process exits."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture import Fixture, clean_env, git, h as overlay, sha  # noqa: E402

APPLY_POINTS = ["apply:begun", "apply:owned", "apply:staged", "apply:fetched", "apply:source:src/a.txt",
                "apply:source:src/new.txt", "apply:output-parked:ui/dist", "apply:output-installed:ui/dist",
                "apply:output-parked:cli/dist", "apply:output-installed:cli/dist", "apply:head", "apply:index",
                "apply:temp-ref-deleted"]
ROLLBACK_POINTS = ["rollback:begun", "rollback:head", "rollback:index", "rollback:source-out:src/a.txt",
                   "rollback:source-in:src/a.txt", "rollback:source-out:src/new.txt", "rollback:output-out:ui/dist",
                   "rollback:output-in:ui/dist", "rollback:output-out:cli/dist", "rollback:output-in:cli/dist",
                   "rollback:owner-released"]


def package_digest(f):
    return sorted((p.relative_to(f.package).as_posix(), sha(p.read_bytes())) for p in f.package.rglob("*") if p.is_file())


class Base(unittest.TestCase):
    def setUp(self):
        self.f = Fixture(self.id().rsplit(".", 1)[-1])
        self.base = self.f.snapshot()

    def assertBaseline(self, msg=""):
        snap = self.f.snapshot()
        diff = {k: (self.base[k], snap[k]) for k in snap if snap[k] != self.base[k]}
        self.assertEqual(diff, {}, msg)

    def apply_ok(self, name):
        code, out, err = self.f.run("apply", self.f.txn(name))
        self.assertEqual((code, out.get("status")), (0, "APPLIED"), err)
        return self.f.txn(name)


class InterruptedRollback(Base):
    """The executed RED: an interrupted rollback of a completed apply must be recognised and resumed."""

    def test_every_rollback_boundary_recovers_exactly_in_a_fresh_process(self):
        for i, point in enumerate(ROLLBACK_POINTS):
            with self.subTest(point=point):
                x = self.apply_ok(f"rb{i}")
                code, _, _ = self.f.run("rollback", x, env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT=point))
                self.assertEqual(code, 75, f"did not stop at {point}")
                journal = json.loads((x / "journal.json").read_text())
                self.assertTrue(journal["phase"].startswith("rollback-"), "rollback intent must precede mutation")
                code, out, err = self.f.run("recover", x)
                self.assertEqual(out.get("status"), "ROLLED_BACK", f"{point}: {out} {err}")
                self.assertNotEqual(out.get("status"), "NOTHING_TO_RECOVER")
                self.assertBaseline(point)
                code, out, _ = self.f.run("recover", x)  # idempotent
                self.assertEqual((code, out.get("status")), (0, "ALREADY_ROLLED_BACK"))

    def test_reviewer_partial_output_state_is_never_a_successful_noop(self):
        # The reviewer's observed state: journal apply-complete while ui/dist holds only index.html.
        x = self.apply_ok("partial")
        ui = self.f.target / "ui/dist"
        (ui / "assets").rename(self.f.root / "moved-assets")
        before = self.f.snapshot()
        code, out, _ = self.f.run("recover", x)
        self.assertEqual(code, 3, out)
        self.assertEqual(out["status"], "INCONSISTENT")
        self.assertEqual(self.f.snapshot(), before, "no write on an inconsistent state")


class InterruptedApply(Base):
    def test_every_apply_boundary_recovers_exactly_and_reapplies(self):
        for i, point in enumerate(APPLY_POINTS):
            with self.subTest(point=point):
                x = self.f.txn(f"ap{i}")
                code, _, _ = self.f.run("apply", x, env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT=point))
                self.assertEqual(code, 75, f"did not stop at {point}")
                code, out, err = self.f.run("recover", x)
                self.assertEqual(out.get("status"), "ROLLED_BACK", f"{point}: {out} {err}")
                self.assertBaseline(point)
        x = self.apply_ok("final")
        self.assertEqual(self.f.run("rollback", x)[1]["status"], "ROLLED_BACK")
        self.assertBaseline()

    def test_crash_during_recovery_of_an_interrupted_apply(self):
        x = self.f.txn("double")
        self.f.run("apply", x, env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT="apply:output-parked:ui/dist"))
        code, _, _ = self.f.run("recover", x, env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT="rollback:output-in:ui/dist"))
        self.assertEqual(code, 75)
        self.assertEqual(self.f.run("recover", x)[1]["status"], "ROLLED_BACK")
        self.assertBaseline()


class LaterWorkPreserved(Base):
    def _refused(self, x):
        before = self.f.snapshot()
        journal = (x / "journal.json").read_bytes()
        code, out, _ = self.f.run("rollback", x)
        self.assertEqual(code, 2, out)
        self.assertEqual(self.f.snapshot(), before, "a refused rollback must not write")
        self.assertEqual((x / "journal.json").read_bytes(), journal)

    def test_later_output_file_blocks_rollback(self):
        x = self.apply_ok("t1")
        (self.f.target / "ui/dist/later-work.txt").write_text("later")
        self._refused(x)

    def test_later_source_edit_blocks_rollback(self):
        x = self.apply_ok("t1")
        (self.f.target / "src/a.txt").write_bytes(b"edited later\r\n")
        self._refused(x)

    def test_stale_transaction_cannot_roll_back_a_later_installation(self):
        x1 = self.apply_ok("t1")
        self.assertEqual(self.f.run("rollback", x1)[1]["status"], "ROLLED_BACK")
        self.apply_ok("t2")
        before = self.f.snapshot()
        for cmd in ("rollback", "recover"):
            code, out, _ = self.f.run(cmd, x1)
            self.assertEqual(code, 2, (cmd, out))
        self.assertEqual(self.f.snapshot(), before)

    def test_edited_journal_identity_is_rejected(self):
        x = self.apply_ok("t1")
        j = json.loads((x / "journal.json").read_text())
        j["target_path"] = str(self.f.root / "elsewhere")
        (x / "journal.json").write_text(json.dumps(j))
        self._refused(x)


class Paths(Base):
    def _rejected_before_txn(self, txn, **kw):
        pkg = package_digest(self.f)
        code, out, _ = self.f.run("apply", txn, **kw)
        self.assertEqual(code, 2, out)
        self.assertFalse(Path(txn).exists(), "nothing may be created")
        self.assertEqual(package_digest(self.f), pkg)
        self.assertBaseline()

    def test_txn_inside_package(self):
        self._rejected_before_txn(self.f.package / "txn")

    def test_txn_inside_target_output(self):
        self._rejected_before_txn(self.f.target / "ui/dist/txn")

    def test_txn_inside_target_git_dir(self):
        self._rejected_before_txn(self.f.target / ".git/txn")

    def test_txn_through_a_junction_into_the_target(self):
        alias = self.f.root / "alias"
        import _winapi
        _winapi.CreateJunction(str(self.f.target / "ui"), str(alias))
        self._rejected_before_txn(alias / "txn")

    def test_target_inside_package_and_package_inside_target(self):
        code, out, _ = self.f.run("preflight", target=self.f.target, package=self.f.target)
        self.assertEqual(code, 2, out)


class GitIdentity(Base):
    def test_moved_original_branch_blocks_rollback(self):
        x = self.apply_ok("t1")
        git(self.f.target, "update-ref", f"refs/heads/{self.f.snapshot()['refs'].split()[0].split('/', 2)[2]}",
            self.f.target_commit)
        before = self.f.snapshot()
        code, out, _ = self.f.run("rollback", x)
        self.assertEqual(code, 2, out)
        self.assertEqual(self.f.snapshot(), before)

    def test_preexisting_overlay_ref_blocks_apply_and_survives(self):
        git(self.f.target, "update-ref", "refs/paperclip-overlay/foreign", self.f.base)
        base = self.f.snapshot()
        code, out, _ = self.f.run("apply", self.f.txn("t1"))
        self.assertEqual(code, 2, out)
        self.assertEqual(self.f.snapshot(), base)

    def test_foreign_overlay_ref_added_mid_transaction_is_not_deleted(self):
        x = self.f.txn("t1")
        self.f.run("apply", x, env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT="apply:staged"))
        git(self.f.target, "update-ref", "refs/paperclip-overlay/foreign", self.f.base)
        before = self.f.snapshot()
        code, out, _ = self.f.run("recover", x)
        self.assertEqual(code, 2, out)
        self.assertEqual(self.f.snapshot(), before)
        self.assertIn("refs/paperclip-overlay/foreign", self.f.snapshot()["refs"])


class Locking(Base):
    def test_live_lock_holder_blocks_every_operation_until_it_dies(self):
        holder = subprocess.Popen([sys.executable, "-I", "-c", (
            "import msvcrt,sys,time\nf=open(sys.argv[1],'a+b');f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)\n"
            "print('locked',flush=True)\ntime.sleep(600)"), str(self.f.target / ".git/paperclip-overlay.lock")],
            stdout=subprocess.PIPE, text=True)
        self.assertEqual(holder.stdout.readline().strip(), "locked")
        try:
            for cmd in ("preflight", "apply"):
                code, out, _ = self.f.run(cmd, self.f.txn("t1") if cmd == "apply" else None)
                self.assertEqual(code, 2, out)
                self.assertIn("locked", out["reason"])
            self.assertFalse(self.f.txn("t1").exists())
            self.assertBaseline()
        finally:
            holder.kill()
            holder.wait()
        self.apply_ok("t2")  # the OS released the dead holder's lock; nothing stale to steal

    def test_paused_apply_blocks_a_competing_rollback_and_apply(self):
        x1, ready = self.f.txn("t1"), self.f.root / "ready.txt"
        env = clean_env(PAPERCLIP_OVERLAY_TEST_PAUSE_AT="apply:source:src/a.txt",
                        PAPERCLIP_OVERLAY_TEST_PAUSE_FILE=str(ready))
        proc = subprocess.Popen([sys.executable, "-I", str(Path(__file__).parent / "run_with_spec.py"),
                                 str(self.f.spec_file), "apply", str(self.f.target), str(self.f.package), str(x1)],
                                env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.time() + 60
            while not ready.exists() and time.time() < deadline:
                time.sleep(0.2)
            self.assertTrue(ready.exists())
            mid = self.f.snapshot()
            for cmd, txn in (("rollback", x1), ("recover", x1), ("apply", self.f.txn("t2"))):
                code, out, _ = self.f.run(cmd, txn)
                self.assertEqual(code, 2, (cmd, out))
            self.assertEqual(self.f.snapshot(), mid)
            self.assertFalse(self.f.txn("t2").exists())
        finally:
            subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)], capture_output=True)
            proc.wait()
        self.assertEqual(self.f.run("recover", x1)[1]["status"], "ROLLED_BACK")
        self.assertBaseline()


class GitEnvironment(Base):
    def test_inherited_git_redirections_are_refused_without_writes(self):
        other = Fixture("other")
        other_before = other.snapshot()
        for var, value in (("GIT_DIR", str(other.target / ".git")), ("GIT_WORK_TREE", str(other.target)),
                           ("GIT_INDEX_FILE", str(other.target / ".git/index")), ("GIT_CONFIG_COUNT", "0")):
            with self.subTest(var=var):
                code, out, _ = self.f.run("apply", self.f.txn("t-" + var), env=clean_env(**{var: value}))
                self.assertEqual(code, 2, out)
                self.assertIn("inherited Git override", out["reason"])
                self.assertFalse(self.f.txn("t-" + var).exists())
        self.assertBaseline()
        self.assertEqual(other.snapshot(), other_before)

    def test_unreviewed_repository_config_is_refused(self):
        for key, value in (("filter.x.clean", "cat"), ("core.hooksPath", "hooks"), ("include.path", "x.cfg"),
                           ("core.fsmonitor", "true")):
            with self.subTest(key=key):
                git(self.f.target, "config", key, value)
                code, out, _ = self.f.run("apply", self.f.txn("t1"))
                self.assertEqual(code, 2, out)
                git(self.f.target, "config", "--unset", key)
        self.assertBaseline()

    def test_repository_hooks_never_run(self):
        sentinel = self.f.root / "hook-ran.txt"
        hooks = self.f.target / ".git/hooks"
        for name in ("reference-transaction", "post-checkout", "post-index-change"):
            (hooks / name).write_text(f"#!/bin/sh\necho {name} >> '{sentinel.as_posix()}'\n", newline="\n")
        base = self.f.snapshot()
        x = self.apply_ok("t1")
        self.assertEqual(self.f.run("rollback", x)[1]["status"], "ROLLED_BACK")
        self.assertFalse(sentinel.exists(), sentinel.read_text() if sentinel.exists() else "")
        self.assertEqual(self.f.snapshot(), base)


class RawBytes(Base):
    def test_lf_deployed_and_pinned_bytes_survive_apply_and_rollback(self):
        lf = (self.f.target / "src/lf-deployed.txt").read_bytes()
        pinned = (self.f.target / "src/pinned.txt").read_bytes()
        x = self.apply_ok("t1")
        self.assertEqual((self.f.target / "src/lf-deployed.txt").read_bytes(), lf)
        self.assertEqual((self.f.target / "src/pinned.txt").read_bytes(), pinned)
        self.f.run("rollback", x)
        self.assertEqual((self.f.target / "src/lf-deployed.txt").read_bytes(), lf)
        self.assertBaseline()

    def test_changed_pinned_bytes_are_refused(self):
        (self.f.target / "src/pinned.txt").write_bytes(b"pinned\nbytes\n")  # LF instead of the pinned CRLF
        code, out, _ = self.f.run("apply", self.f.txn("t1"))
        self.assertEqual(code, 2, out)
        self.assertFalse(self.f.txn("t1").exists())


class ContractCheckFollowUps(Base):
    """Regressions for the read-only contract check of d83bee9."""

    def _no_write(self, cmd, x, expect_code):
        before = self.f.snapshot()
        journal = (x / "journal.json").read_bytes() if (x / "journal.json").exists() else None
        code, out, _ = self.f.run(cmd, x)
        self.assertEqual(code, expect_code, out)
        self.assertEqual(self.f.snapshot(), before)
        if journal is not None:
            self.assertEqual((x / "journal.json").read_bytes(), journal)
        return out

    def test_recover_on_apply_complete_with_moved_branch_is_not_a_noop(self):
        x = self.apply_ok("t1")
        git(self.f.target, "update-ref", "refs/heads/fix/base-branch", self.f.target_commit)
        out = self._no_write("recover", x, 3)
        self.assertEqual(out["status"], "INCONSISTENT")

    def test_missing_owner_marker_after_apply_blocks_rollback(self):
        x = self.apply_ok("t1")
        (self.f.target / ".git/paperclip-overlay-owner.json").rename(self.f.root / "moved-marker.json")
        self._no_write("rollback", x, 2)

    def test_deleted_output_after_apply_blocks_rollback(self):
        x = self.apply_ok("t1")
        shutil.move(str(self.f.target / "cli/dist"), str(self.f.root / "moved-cli-dist"))
        self._no_write("rollback", x, 2)

    def test_occupied_evidence_slot_is_refused_before_any_write(self):
        x = self.apply_ok("t1")
        (x / "rb-out/ui/dist").mkdir(parents=True)
        self._no_write("rollback", x, 2)

    def test_invalid_journal_phase_is_refused(self):
        x = self.apply_ok("t1")
        j = json.loads((x / "journal.json").read_text())
        j["phase"] = "apply-mystery"
        j["history"].append("apply-mystery")
        (x / "journal.json").write_text(json.dumps(j))
        self._no_write("recover", x, 2)

    def test_stale_ref_lock_stops_before_writes(self):
        x = self.apply_ok("t1")
        (self.f.target / ".git/HEAD.lock").write_text("stale")
        out = self._no_write("rollback", x, 3)
        self.assertIn("lock", out["reason"])
        (self.f.target / ".git/HEAD.lock").unlink()
        self.assertEqual(self.f.run("rollback", x)[1]["status"], "ROLLED_BACK")
        self.assertBaseline()

    def test_test_hooks_are_refused_outside_marked_staging(self):
        (self.f.target / ".git/paperclip-overlay-test-staging").unlink()
        base = self.f.snapshot()
        code, out, _ = self.f.run("apply", self.f.txn("t1"), env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT="apply:begun"))
        self.assertEqual(code, 2, out)
        self.assertIn("test hooks refused", out["reason"])
        self.assertFalse(self.f.txn("t1").exists())
        self.assertEqual(self.f.snapshot(), base)

    def test_git_planted_in_current_directory_is_never_used(self):
        planted = self.f.root / "cwd"
        planted.mkdir()
        (planted / "git.exe").write_bytes(b"not git")
        (planted / "git.cmd").write_text("@echo planted > planted-ran.txt\r\n")
        argv = [sys.executable, "-I", str(Path(__file__).parent / "run_with_spec.py"), str(self.f.spec_file),
                "preflight", str(self.f.target), str(self.f.package)]
        r = subprocess.run(argv, capture_output=True, text=True, env=clean_env(), cwd=planted)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((planted / "planted-ran.txt").exists())

    def test_crash_before_the_transaction_directory_appears(self):
        x = self.f.txn("t1")
        code, _, _ = self.f.run("apply", x, env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT="apply:creating"))
        self.assertEqual(code, 75)
        self.assertFalse(x.exists(), "X must appear only with its journal")
        self.assertBaseline()
        self.apply_ok("t1")  # the same name is usable again; nothing in T was touched

    def test_crash_at_temp_ref_deletion_during_recovery(self):
        x = self.f.txn("t1")
        self.f.run("apply", x, env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT="apply:fetched"))
        code, _, _ = self.f.run("recover", x, env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT="rollback:temp-ref-deleted"))
        self.assertEqual(code, 75)
        self.assertEqual(self.f.run("recover", x)[1]["status"], "ROLLED_BACK")
        self.assertBaseline()


class OwnedMovesOnly(Base):
    """Regressions for the independent PR27 probes of 76c8c81: F1 (a missing output or source is restorable
    only with this transaction's own move evidence) and F2 (no link/reparse point inside .git)."""

    _no_write = ContractCheckFollowUps._no_write

    def _paused_rollback(self, name):
        x = self.apply_ok(name)
        code, _, _ = self.f.run("rollback", x, env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT="rollback:begun"))
        self.assertEqual(code, 75)
        return x

    def test_unowned_missing_output_after_rollback_intent_is_refused(self):
        x = self._paused_rollback("f1-out")
        moved = self.f.root / "owner-moved-ui"
        (self.f.target / "ui/dist").rename(moved)
        manifest = sorted(p.relative_to(moved).as_posix() for p in moved.rglob("*"))
        out = self._no_write("recover", x, 2)
        self.assertIn("ui/dist missing without this transaction's output move", out["reason"])
        self.assertEqual(sorted(p.relative_to(moved).as_posix() for p in moved.rglob("*")), manifest)
        self.assertFalse((self.f.target / "ui/dist").exists())

    def test_unowned_missing_source_after_rollback_intent_is_refused(self):
        x = self._paused_rollback("f1-src")
        (self.f.target / "src/a.txt").rename(self.f.root / "owner-moved-a.txt")
        out = self._no_write("recover", x, 2)
        self.assertIn("src/a.txt missing without this transaction's rollback move", out["reason"])

    def test_unparked_output_missing_mid_apply_swap_is_refused(self):
        x = self.f.txn("f1-apply")
        code, _, _ = self.f.run("apply", x, env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT="apply:output-installed:ui/dist"))
        self.assertEqual(code, 75)
        (self.f.target / "cli/dist").rename(self.f.root / "owner-moved-cli")  # never parked by the helper
        self._no_write("recover", x, 2)

    def test_owned_moves_still_recover(self):
        # Interrupted between moving new out to rb-out and moving parked back in: the owned case.
        x = self.apply_ok("f1-owned")
        code, _, _ = self.f.run("rollback", x, env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT="rollback:output-out:ui/dist"))
        self.assertEqual(code, 75)
        self.assertFalse((self.f.target / "ui/dist").exists())
        self.assertEqual(self.f.run("recover", x)[1]["status"], "ROLLED_BACK")
        self.assertBaseline()

    def test_ref_namespace_junction_is_refused_before_any_write(self):
        import _winapi
        external = self.f.root / "outside-refspace"
        external.mkdir()
        _winapi.CreateJunction(str(external), str(self.f.target / ".git/refs/paperclip-overlay"))
        before = self.f.snapshot()
        x = self.f.txn("f2")
        code, out, _ = self.f.run("apply", x, env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT="apply:fetched"))
        self.assertEqual(code, 2, out)
        self.assertIn("inside Git metadata", out["reason"])
        self.assertFalse(x.exists())
        self.assertEqual(list(external.iterdir()), [])
        self.assertEqual(self.f.snapshot(), before)

    def test_git_metadata_junction_blocks_rollback_before_any_write(self):
        import _winapi
        x = self.apply_ok("f2-rb")
        external = self.f.root / "outside-logs"
        external.mkdir()
        _winapi.CreateJunction(str(external), str(self.f.target / ".git/logs/paperclip-alias"))
        self._no_write("rollback", x, 2)
        self.assertEqual(list(external.iterdir()), [])


class PhysicalOwnership(unittest.TestCase):
    def test_metadata_validation_refuses_multiply_linked_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata = root / "metadata"
            metadata.mkdir()
            original = root / "fixture.txt"
            original.write_bytes(b"owned fixture")
            os.link(original, metadata / "linked")
            with self.assertRaisesRegex(overlay.Rejected, "non-owned file inside Git metadata"):
                overlay.check_git_metadata(metadata)
            self.assertEqual(original.read_bytes(), b"owned fixture")

    def test_absent_output_still_requires_path_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            absent = Path(directory) / "parent" / "output"
            self.assertIsNone(overlay.scan_tree(absent))
            with patch.object(overlay, "plain", side_effect=overlay.Rejected("unowned ancestor")):
                with self.assertRaisesRegex(overlay.Rejected, "unowned ancestor"):
                    overlay.scan_tree(absent)


if __name__ == "__main__":
    unittest.main(verbosity=2)
