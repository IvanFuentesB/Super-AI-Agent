"""N+6.36B regression tests for repo-write-capable Python fallback."""

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
LAUNCHER_PATH = REPO_ROOT / "03_scripts" / "ghoti_product_launcher.py"


def _load_launcher():
    spec = importlib.util.spec_from_file_location("ghoti_product_launcher_n636b", LAUNCHER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ContextPackWriterFallbackTests(unittest.TestCase):
    def test_resolver_finds_python_that_can_write_repo(self):
        launcher = _load_launcher()
        executable = launcher._resolve_repo_write_python()
        self.assertIsNotNone(executable)
        self.assertTrue(Path(executable).is_file())
        self.assertFalse(any(REPO_ROOT.glob(".ghoti_python_write_probe_*")))

    def test_launcher_context_pack_succeeds_with_active_python(self):
        result = subprocess.run(
            [sys.executable, str(LAUNCHER_PATH), "--context-pack", "--json"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["local_only"])
        self.assertFalse(payload["external_api_used"])
        self.assertFalse(any(REPO_ROOT.glob(".ghoti_python_write_probe_*")))


if __name__ == "__main__":
    unittest.main()
