import pathlib
import sys
import unittest
from unittest.mock import patch

import httpx

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "openjarvis-source" / "src"))
sys.path.insert(0, str(ROOT / "harness"))

import openjarvis_adapter as adapter


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.budget = adapter.Budget()

    def test_default_is_off_without_creating_transport(self):
        with patch.object(adapter, "local_client", side_effect=AssertionError("network")):
            self.assertEqual(adapter.evaluate(), {"status": "disabled", "inference_used": False,
                                                   "next_action": "Explicit --enable and installed --model required"})

    def test_explicit_enable_still_cannot_start_live_inference(self):
        with patch.object(adapter, "_run_agent", side_effect=AssertionError("live inference")) as run_agent:
            result = adapter.evaluate(enable=True, model="gemma3:4b")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["inference_used"])
        run_agent.assert_not_called()

    def test_cloud_alias_is_rejected_even_if_listed_as_installed(self):
        for alias in ("qwen3:4b-cloud", "gpt-oss:120b-cloud", "cloud/qwen3:4b"):
            with self.subTest(alias=alias), self.assertRaises(ValueError):
                adapter.select_model(alias, [alias])

    def test_foreign_url_is_refused_before_mock_transport(self):
        called = []
        transport = httpx.MockTransport(lambda request: called.append(request))
        with adapter.local_client(self.budget, transport) as client:
            with self.assertRaises(ValueError):
                client.get("https://example.com/")
        self.assertEqual(called, [])

    def test_redirect_is_refused(self):
        transport = httpx.MockTransport(lambda request: httpx.Response(302, headers={"location": "/api/tags"}))
        with adapter.local_client(self.budget, transport) as client:
            with self.assertRaisesRegex(ValueError, "Redirect or encoded"):
                client.get("/api/tags")

    def test_compressed_response_is_refused(self):
        transport = httpx.MockTransport(lambda request: httpx.Response(
            200, headers={"content-encoding": "gzip"}, stream=httpx.ByteStream(b"compressed")))
        with adapter.local_client(self.budget, transport) as client:
            with self.assertRaisesRegex(ValueError, "Redirect or encoded"):
                client.get("/api/tags")

    def test_oversized_response_is_refused_even_without_content_length(self):
        body = b"x" * (adapter.MAX_RESPONSE_BYTES + 1)
        transport = httpx.MockTransport(lambda request: httpx.Response(200, stream=httpx.ByteStream(body)))
        with adapter.local_client(self.budget, transport) as client:
            with self.assertRaisesRegex(ValueError, "Response size"):
                client.get("/api/tags")

    def test_request_budget_and_deadline_are_enforced(self):
        transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"ok": True}))
        with adapter.local_client(self.budget, transport) as client:
            for _ in range(adapter.MAX_REQUESTS):
                self.assertEqual(client.get("/api/tags").status_code, 200)
            with self.assertRaisesRegex(TimeoutError, "Request budget"):
                client.get("/api/tags")

        expired = adapter.Budget()
        expired.deadline = adapter.time.monotonic() - 1
        with adapter.local_client(expired, transport) as client:
            with self.assertRaisesRegex(TimeoutError, "deadline"):
                client.get("/api/tags")

    def test_deadline_is_checked_after_stream_eof(self):
        budget = adapter.Budget()

        class ExpiresAtEof(httpx.SyncByteStream):
            def __iter__(self):
                yield b"ok"
                budget.deadline = adapter.time.monotonic() - 1

            def close(self):
                pass

        transport = httpx.MockTransport(lambda request: httpx.Response(200, stream=ExpiresAtEof()))
        with adapter.local_client(budget, transport) as client:
            with self.assertRaisesRegex(TimeoutError, "deadline"):
                client.get("/api/tags")

    def test_verified_sequence_rejects_bogus_first_or_second_result(self):
        valid = [("17*23+9", "400.0", True), ("400*2", "800.0", True)]
        self.assertTrue(adapter.verified_sequence(valid, "800"))
        for records in (
            [("17*23+9", "999.0", True), valid[1]],
            [valid[0], ("400*2", "999.0", True)],
        ):
            with self.subTest(records=records):
                self.assertFalse(adapter.verified_sequence(records, "800"))

    def test_calculator_rejects_unknown_arguments_and_overbudget(self):
        tool = adapter.calculator_tool()
        self.assertFalse(tool.execute(expression="2+2", extra="ignored").success)
        self.assertTrue(tool.execute(expression="2+2").success)
        tool.calls = 4
        self.assertFalse(tool.execute(expression="2+2").success)

    def test_recording_fixture_uses_real_orchestrator_with_synthetic_ollama(self):
        responses = iter((
            {"models": [{"name": "gemma3:4b"}]},
            {"message": {"content": 'TOOL: calculator\nINPUT: {"expression": "17*23+9"}'}, "model": "gemma3:4b"},
            {"message": {"content": 'TOOL: calculator\nINPUT: {"expression": "400*2"}'}, "model": "gemma3:4b"},
            {"message": {"content": "FINAL_ANSWER: 800"}, "model": "gemma3:4b"},
        ))

        def handler(request):
            return httpx.Response(200, json=next(responses))

        mock_transport = httpx.MockTransport(handler)
        with patch("openjarvis.agents._stubs.load_config", side_effect=AssertionError("config lookup")) as load_config:
            result = adapter.run_recording_fixture("gemma3:4b", mock_transport)

        load_config.assert_not_called()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["answer"], 800)
        self.assertEqual(result["http_requests"], 4)
        self.assertEqual([step["value"] for step in result["verified_steps"]], [400.0, 800.0])
        self.assertEqual(result["tool_call_count"], 2)
        self.assertFalse(result["cloud_used"])


if __name__ == "__main__":
    unittest.main()
