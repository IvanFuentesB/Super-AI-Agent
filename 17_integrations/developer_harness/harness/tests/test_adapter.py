import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import openjarvis_adapter as adapter


class AdapterTests(unittest.TestCase):
    def test_default_does_not_import_or_call_runtime(self):
        with patch.object(adapter, "_run_agent", side_effect=AssertionError("called")):
            self.assertEqual(adapter.evaluate()["status"], "disabled")

    def test_disabled_cli_is_machine_readable(self):
        result = subprocess.run([sys.executable, "openjarvis_adapter.py"],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "disabled")

    def test_only_explicit_installed_model_is_allowed(self):
        self.assertEqual(adapter.select_model("qwen3:4b", ["qwen3:4b"]), "qwen3:4b")
        with self.assertRaises(ValueError):
            adapter.select_model("missing", ["gemma3:4b"])

    def test_no_automatic_model_selection_or_cloud(self):
        for model in ("", "https://example.com", "cloud/model", "model\nother", "gpt-oss:120b-cloud"):
            with self.subTest(model=model), self.assertRaises(ValueError):
                adapter.select_model(model, [model])

    def test_small_arithmetic_accepted(self):
        for expression in ("17 * 23 + 9", "400 * 2", "(17*23)+9"):
            adapter.validate_expression(expression)

    def test_resource_and_code_expressions_refused(self):
        for expression in ("9**9999", "9^99", "__import__('os')", "1/0",
                           "9" * 10, "1+" * 60, "sqrt(4)", "", None, "(((1)))" * 20):
            with self.subTest(expression=expression), self.assertRaises(ValueError):
                adapter.validate_expression(expression)

    def test_explicit_enable_cannot_bypass_host_adoption(self):
        with patch.object(adapter, "_run_agent", side_effect=AssertionError("called")):
            result = adapter.evaluate(enable=True, model="qwen3:4b")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["inference_used"])

    def test_real_transport_is_not_an_offline_fixture(self):
        with self.assertRaises(ValueError):
            adapter.run_recording_fixture("gemma3:4b", None)

    def test_limits_are_fixed(self):
        self.assertLessEqual(adapter.MAX_TURNS, 4)
        self.assertLessEqual(adapter.MAX_REQUESTS, 4)
        self.assertLessEqual(adapter.DEADLINE_SECONDS, 120)
        self.assertLessEqual(adapter.MAX_RESPONSE_BYTES, 131072)

    def test_role_configs_do_not_override_permissions(self):
        import pathlib
        import tomllib
        roles = pathlib.Path(".codex/agents")
        self.assertEqual({p.stem for p in roles.glob("*.toml")},
                         {"explorer", "implementer", "tester", "reviewer", "integrator"})
        for path in roles.glob("*.toml"):
            data = tomllib.loads(path.read_text())
            self.assertTrue(data["developer_instructions"])
            self.assertNotIn("sandbox_mode", data)
            self.assertNotIn("approval_policy", data)
            self.assertNotIn("mcp_servers", data)


if __name__ == "__main__":
    unittest.main()
