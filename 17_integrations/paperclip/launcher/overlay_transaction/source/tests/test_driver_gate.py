"""The rehearsal gate must never report success for a failed, crashed, omitted, duplicated or unexpected scenario."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import rehearse  # noqa: E402

PASS = lambda: (True, {})  # noqa: E731
REQUIRED = ["A", "B", "C"]


def run(scenarios):
    return rehearse.run_scenarios(scenarios, REQUIRED)[1]


class Gate(unittest.TestCase):
    def test_all_required_passing_is_the_only_pass(self):
        self.assertEqual(run([("A", "check", PASS), ("B", "rejection", PASS), ("C", "recovery", PASS)])["verdict"], "PASS")

    def test_failed_predicate_fails_the_aggregate(self):
        gate = run([("A", "check", PASS), ("B", "rejection", lambda: (False, {})), ("C", "recovery", PASS)])
        self.assertEqual(gate["verdict"], "FAIL")
        self.assertIn("B FAIL", gate["problems"])

    def test_crashing_scenario_fails_and_is_not_a_pass(self):
        def boom():
            raise RuntimeError("never reached its assertions")
        results, gate = rehearse.run_scenarios([("A", "check", PASS), ("B", "rejection", boom), ("C", "recovery", PASS)],
                                               REQUIRED)
        self.assertEqual(gate["verdict"], "FAIL")
        self.assertEqual([r["status"] for r in results], ["PASS", "ERROR", "PASS"])

    def test_omitted_scenario_fails_the_aggregate(self):
        gate = run([("A", "check", PASS), ("C", "recovery", PASS)])
        self.assertEqual(gate["verdict"], "FAIL")
        self.assertIn("missing scenario B", gate["problems"])

    def test_truthy_but_not_true_is_not_a_pass(self):
        gate = run([("A", "check", PASS), ("B", "rejection", lambda: ("yes", {})), ("C", "recovery", lambda: (1, {}))])
        self.assertEqual(gate["verdict"], "FAIL")

    def test_duplicate_and_unexpected_ids_fail(self):
        self.assertEqual(run([("A", "check", PASS), ("A", "check", PASS), ("B", "rejection", PASS),
                              ("C", "recovery", PASS)])["verdict"], "FAIL")
        self.assertEqual(run([("A", "check", PASS), ("B", "rejection", PASS), ("C", "recovery", PASS),
                              ("D", "check", PASS)])["verdict"], "FAIL")

    def test_unknown_kind_and_empty_required_fail(self):
        self.assertEqual(run([("A", "check", PASS), ("B", "mystery", PASS), ("C", "recovery", PASS)])["verdict"], "FAIL")
        self.assertEqual(rehearse.evaluate([], [])["verdict"], "FAIL")

    def test_driver_main_returns_nonzero_when_a_scenario_is_omitted(self):
        # Exercise the real main() wiring with stubbed scenarios: omission through the documented hook.
        import os
        original_build, original_stage = rehearse.build, rehearse.Stage
        rehearse.Stage = lambda *a: type("S", (), {"removed_git_env": [], "root": Path("."), "package": Path(".")})()
        rehearse.build = lambda stage: [("A", "check", PASS), ("B", "rejection", PASS), ("C", "recovery", PASS)]
        out = Path(__file__).with_name("gate-selftest-report.json")
        try:
            os.environ["REHEARSE_TEST_OMIT"] = "B"
            self.assertEqual(rehearse.main(".", ".", ".", ".", ".", ".", str(out)), 1)
            os.environ.pop("REHEARSE_TEST_OMIT")
            self.assertEqual(rehearse.main(".", ".", ".", ".", ".", ".", str(out)), 0)
        finally:
            os.environ.pop("REHEARSE_TEST_OMIT", None)
            rehearse.build, rehearse.Stage = original_build, original_stage
            out.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
