#!/usr/bin/env python3
"""N+4.4D tests: preview path containment security fix."""
import json
import os
import pathlib
import re
import subprocess
import tempfile
import time
import unittest
import urllib.parse
import urllib.request

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
DASHBOARD_DIR = REPO_ROOT / "01_projects" / "dashboard_mvp"
SERVER_JS = DASHBOARD_DIR / "server.js"


class N44DPathContainmentStaticTests(unittest.TestCase):
    """Static checks on server.js."""

    @classmethod
    def setUpClass(cls):
        cls.server_text = SERVER_JS.read_text(encoding="utf-8")

    def test_server_defines_is_path_inside_repo(self):
        self.assertIn("function isPathInsideRepo(", self.server_text)

    def test_server_uses_path_relative_for_containment(self):
        # The new helper must use path.relative for real boundary check.
        idx = self.server_text.find("function isPathInsideRepo(")
        self.assertGreater(idx, 0)
        helper_block = self.server_text[idx : idx + 2000]
        self.assertIn("path.relative(", helper_block)
        self.assertIn("path.resolve(", helper_block)

    def test_server_no_longer_uses_startswith_repo_root_for_containment(self):
        # No startsWith(repoRoot) anywhere — that was the vulnerable check.
        self.assertNotIn("startsWith(repoRoot)", self.server_text)
        self.assertNotIn("startsWith(REPO_ROOT)", self.server_text)

    def test_is_repo_local_path_calls_is_path_inside_repo(self):
        idx = self.server_text.find("function isRepoLocalPath(")
        self.assertGreater(idx, 0)
        block = self.server_text[idx : idx + 1500]
        self.assertIn("isPathInsideRepo(", block)

    def test_preview_endpoint_uses_is_path_inside_repo(self):
        idx = self.server_text.find("/api/desktop-operator/preview")
        self.assertGreater(idx, 0)
        block = self.server_text[idx : idx + 2000]
        self.assertIn("isPathInsideRepo(", block)

    def test_no_shell_true_in_server(self):
        self.assertNotIn("shell: true", self.server_text)
        self.assertNotIn("shell:true", self.server_text)

    def test_preview_endpoint_requires_html_extension(self):
        idx = self.server_text.find("/api/desktop-operator/preview")
        block = self.server_text[idx : idx + 2000]
        self.assertIn(".html", block)
        self.assertIn(".htm", block)
        self.assertIn("only .html or .htm previews allowed", block)

class N44DPathContainmentNodeHelperTests(unittest.TestCase):
    """Exercise the isPathInsideRepo helper directly via a small Node harness."""

    def _run_node_check(self, repo_root: str, candidate: str) -> bool:
        # Extract the isPathInsideRepo function from server.js and call it.
        server_text = SERVER_JS.read_text(encoding="utf-8")
        start = server_text.find("function isPathInsideRepo(")
        self.assertGreater(start, 0)
        # Find matching closing brace by scanning balanced braces from the
        # first '{' after the function header.
        brace_start = server_text.find("{", start)
        depth = 0
        idx = brace_start
        while idx < len(server_text):
            ch = server_text[idx]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
            idx += 1
        helper_src = server_text[start : idx + 1]
        node_script = (
            "const path = require('path');"
            f"const repoRoot = {json.dumps(repo_root)};"
            + helper_src
            + f"const result = isPathInsideRepo({json.dumps(candidate)});"
            "console.log(result ? 'INSIDE' : 'OUTSIDE');"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(node_script)
            script_path = f.name
        try:
            proc = subprocess.run(["node", script_path], capture_output=True, timeout=15)
            out = proc.stdout.decode("utf-8", "ignore").strip()
            return out == "INSIDE"
        finally:
            try:
                os.unlink(script_path)
            except OSError:
                pass

    def test_sibling_prefix_outside_path_rejected(self):
        repo_root = str(REPO_ROOT)
        sibling = repo_root + "_evil" + os.sep + "fake.html"
        self.assertFalse(self._run_node_check(repo_root, sibling),
                         f"Sibling-prefix path must be rejected: {sibling}")

    def test_normal_outside_path_rejected(self):
        self.assertFalse(self._run_node_check(str(REPO_ROOT), "C:\\Windows\\System32\\drivers\\etc\\hosts"))

    def test_traversal_rejected(self):
        # path.relative will produce a string starting with "..".
        self.assertFalse(self._run_node_check(str(REPO_ROOT), "..\\..\\evil.html"))

    def test_repo_root_itself_rejected(self):
        self.assertFalse(self._run_node_check(str(REPO_ROOT), str(REPO_ROOT)))

    def test_valid_inside_relative_path_accepted(self):
        self.assertTrue(self._run_node_check(str(REPO_ROOT), "14_context\\current_state.md"))

    def test_valid_inside_absolute_path_accepted(self):
        target = str(REPO_ROOT / "14_context" / "current_state.md")
        self.assertTrue(self._run_node_check(str(REPO_ROOT), target))

class N44DPreviewEndpointLiveTests(unittest.TestCase):
    """Spawn the dashboard server and hit /api/desktop-operator/preview."""

    PORT = 3210

    @classmethod
    def setUpClass(cls):
        # Free up the port if a previous run left it bound.
        cls.proc = subprocess.Popen(
            ["node", "server.js"],
            cwd=str(DASHBOARD_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Wait for the server to be ready by polling /api/health.
        deadline = time.time() + 15
        cls.ready = False
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{cls.PORT}/api/health", timeout=2) as r:
                    if r.status == 200:
                        cls.ready = True
                        break
            except Exception:
                time.sleep(0.5)
        # Detect port from log if needed
        if not cls.ready:
            try:
                stdout_bytes = cls.proc.stdout.read1(4096) if cls.proc.stdout else b""
                stdout_text = stdout_bytes.decode("utf-8", "ignore")
                m = re.search(r"://[^:]+:(\d+)", stdout_text)
                if m:
                    cls.PORT = int(m.group(1))
                    # Retry once
                    try:
                        with urllib.request.urlopen(f"http://127.0.0.1:{cls.PORT}/api/health", timeout=5) as r:
                            cls.ready = (r.status == 200)
                    except Exception:
                        pass
            except Exception:
                pass

    @classmethod
    def tearDownClass(cls):
        try:
            cls.proc.terminate()
            cls.proc.wait(timeout=5)
        except Exception:
            try:
                cls.proc.kill()
            except Exception:
                pass

    def _get(self, candidate: str):
        enc = urllib.parse.quote(candidate, safe="")
        url = f"http://127.0.0.1:{self.PORT}/api/desktop-operator/preview?path={enc}"
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                return r.status, r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore") if e.fp else ""
            return e.code, body

    def test_sibling_prefix_outside_rejected_400(self):
        if not self.ready:
            self.skipTest("Dashboard server not ready in time")
        bad = str(REPO_ROOT) + "_evil" + os.sep + "fake.html"
        status, body = self._get(bad)
        self.assertEqual(status, 400, body)
        payload = json.loads(body)
        self.assertFalse(payload["ok"])

    def test_normal_outside_rejected_400(self):
        if not self.ready:
            self.skipTest("Dashboard server not ready in time")
        status, body = self._get("C:\\Windows\\System32\\drivers\\etc\\hosts")
        self.assertEqual(status, 400, body)

    def test_traversal_rejected_400(self):
        if not self.ready:
            self.skipTest("Dashboard server not ready in time")
        status, body = self._get("..\\..\\evil.html")
        self.assertEqual(status, 400, body)

    def test_non_html_rejected_400(self):
        if not self.ready:
            self.skipTest("Dashboard server not ready in time")
        status, body = self._get("01_projects/dashboard_mvp/server.js")
        self.assertEqual(status, 400, body)

    def test_secret_pattern_rejected_400(self):
        if not self.ready:
            self.skipTest("Dashboard server not ready in time")
        status, body = self._get(".env.html")
        self.assertEqual(status, 400, body)


if __name__ == "__main__":
    unittest.main()