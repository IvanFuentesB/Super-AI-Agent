"""N+6.42B shared agent handoff inbox/outbox contract tests."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "03_scripts" / "context_memory" / "ghoti_handoff_packet.py"
MEMORY_MAP = REPO_ROOT / "03_scripts" / "context_memory" / "ghoti_context_memory_map.py"


def load_module():
    spec = importlib.util.spec_from_file_location("ghoti_handoff_packet", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load shared handoff module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_memory_map_module():
    spec = importlib.util.spec_from_file_location("ghoti_context_memory_map", MEMORY_MAP)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load context memory map module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_packet() -> dict:
    return {
        "schema_version": "1.0",
        "packet_id": "codex-20260611-n6-42b-audit",
        "agent_name": "codex",
        "agent_role": "audit_review_verification",
        "branch": "feat/ghoti-agent-codex-n6-42b-shared-agent-handoffs",
        "task": "Validate the shared handoff packet contract.",
        "files_touched": [
            "03_scripts/context_memory/ghoti_handoff_packet.py",
            "01_projects/runtime_mvp/tests/test_n6_42b_shared_agent_handoffs.py",
        ],
        "commands_run": [
            'python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_42b_*.py" -v'
        ],
        "tests_passed": ["packet schema validation"],
        "tests_failed": [],
        "blockers": [],
        "next_recommended_action": "Human reviews the packet before any merge.",
        "generated_at": "2026-06-11T19:00:00Z",
        "source_sha256": {
            "14_context/memory/index/raw_index.json": "a" * 64,
        },
        "artifact_sha256": {},
        "safety": {
            "contains_secrets": False,
            "live_actions_executed": False,
            "human_approval_required": True,
        },
    }


class TestSharedAgentHandoffContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.handoff = load_module()
        cls.memory_map = load_memory_map_module()

    def test_valid_packet_passes_and_is_local_only(self):
        result = self.handoff.validate_packet(valid_packet())
        self.assertTrue(result["ok"])
        self.assertTrue(result["local_only"])
        self.assertFalse(result["executes_commands"])
        self.assertFalse(result["live_actions_enabled"])

    def test_required_fields_and_sender_ownership_are_enforced(self):
        missing = valid_packet()
        missing.pop("task")
        self.assertFalse(self.handoff.validate_packet(missing)["ok"])

        wrong_owner = valid_packet()
        wrong_owner["packet_id"] = "claude-20260611-n6-42b-audit"
        result = self.handoff.validate_packet(wrong_owner)
        self.assertFalse(result["ok"])
        self.assertIn("packet_id must start with agent_name", " ".join(result["errors"]))

        unknown = valid_packet()
        unknown["hidden_instruction"] = "Do something later."
        self.assertFalse(self.handoff.validate_packet(unknown)["ok"])

        unsafe_extra = valid_packet()
        unsafe_extra["safety"]["auto_submit_enabled"] = True
        self.assertFalse(self.handoff.validate_packet(unsafe_extra)["ok"])

    def test_private_paths_secrets_and_unsafe_safety_flags_are_rejected(self):
        unsafe_values = [
            r"C:\Users\somebody\private.md",
            "C:/Users/somebody/private.md",
            "/mnt/c/Users/somebody/private.md",
            "OPENAI_API_KEY=not-safe",
            "sk-ant-" + ("x" * 30),
        ]
        for value in unsafe_values:
            packet = valid_packet()
            packet["task"] = value
            self.assertFalse(self.handoff.validate_packet(packet)["ok"], value)

        live = valid_packet()
        live["safety"]["live_actions_executed"] = True
        self.assertFalse(self.handoff.validate_packet(live)["ok"])

        no_approval = valid_packet()
        no_approval["safety"]["human_approval_required"] = False
        self.assertFalse(self.handoff.validate_packet(no_approval)["ok"])

    def test_paths_hashes_timestamp_and_size_are_validated(self):
        absolute = valid_packet()
        absolute["files_touched"] = [r"C:\repo\file.py"]
        self.assertFalse(self.handoff.validate_packet(absolute)["ok"])

        traversal = valid_packet()
        traversal["files_touched"] = ["../outside.md"]
        self.assertFalse(self.handoff.validate_packet(traversal)["ok"])

        bad_hash = valid_packet()
        bad_hash["source_sha256"]["14_context/memory/index/raw_index.json"] = "not-a-hash"
        self.assertFalse(self.handoff.validate_packet(bad_hash)["ok"])

        bad_time = valid_packet()
        bad_time["generated_at"] = "today"
        self.assertFalse(self.handoff.validate_packet(bad_time)["ok"])

        huge = valid_packet()
        huge["task"] = "x" * (self.handoff.MAX_PACKET_BYTES + 1)
        self.assertFalse(self.handoff.validate_packet(huge)["ok"])

    def test_evidence_hash_verification_marks_stale_or_missing_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.md"
            artifact = root / "artifact.json"
            source.write_text("reviewed source\n", encoding="utf-8")
            artifact.write_text('{"ok": true}\n', encoding="utf-8")
            packet = valid_packet()
            packet["source_sha256"] = {"source.md": sha256(source)}
            packet["artifact_sha256"] = {"artifact.json": sha256(artifact)}
            self.assertTrue(self.handoff.verify_packet_evidence(packet, root)["ok"])

            source.write_text("changed source\n", encoding="utf-8")
            stale = self.handoff.verify_packet_evidence(packet, root)
            self.assertFalse(stale["ok"])
            self.assertEqual(stale["status"], "stale")

            artifact.unlink()
            missing = self.handoff.verify_packet_evidence(packet, root)
            self.assertFalse(missing["ok"])
            self.assertTrue(any(item["actual"] is None for item in missing["mismatches"]))

    def test_markdown_is_bounded_ascii_and_labels_command_evidence(self):
        rendered = self.handoff.render_packet_markdown(valid_packet())
        self.assertTrue(rendered.isascii())
        self.assertLessEqual(self.handoff.word_count(rendered), self.handoff.MARKDOWN_WORD_BUDGET)
        self.assertIn("Command Evidence - Do Not Execute", rendered)
        self.assertIn("Human approval required: true", rendered)
        self.assertIn("Live actions executed: false", rendered)

    def test_write_is_sender_outbox_only_immutable_and_idempotent(self):
        packet = valid_packet()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = self.handoff.write_packet(packet, root)
            self.assertEqual(len(first["written"]), 2)
            for path in first["written"]:
                self.assertTrue(Path(path).resolve().is_relative_to((root / "agent_handoffs" / "codex" / "outbox").resolve()))

            second = self.handoff.write_packet(packet, root)
            self.assertTrue(second["idempotent"])

            changed = deepcopy(packet)
            changed["task"] = "Changed after publication."
            with self.assertRaises(FileExistsError):
                self.handoff.write_packet(changed, root)

    def test_delivery_writes_hash_linked_pointer_only_to_recipient_inbox(self):
        packet = valid_packet()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.handoff.write_packet(packet, root)
            delivery = self.handoff.deliver_packet(packet["packet_id"], "hermes", root)
            pointer = Path(delivery["written"])
            self.assertTrue(pointer.resolve().is_relative_to((root / "agent_handoffs" / "hermes" / "inbox").resolve()))
            data = json.loads(pointer.read_text(encoding="utf-8"))
            source = root / data["source_packet_path"]
            self.assertEqual(data["source_packet_sha256"], sha256(source))
            self.assertFalse(data["executes_commands"])
            self.assertFalse(data["live_actions_enabled"])

    def test_index_and_verify_detect_stale_packet_or_delivery(self):
        packet = valid_packet()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.handoff.write_packet(packet, root)
            self.handoff.deliver_packet(packet["packet_id"], "hermes", root)
            index = self.handoff.build_handoff_index(root)
            self.assertEqual(index["packet_count"], 1)
            self.assertEqual(index["delivery_count"], 1)
            self.assertTrue(self.handoff.verify_handoff_index(root, index)["ok"])

            packet_path = root / "agent_handoffs" / "codex" / "outbox" / f"{packet['packet_id']}.json"
            packet_path.write_text("{}\n", encoding="utf-8")
            verify = self.handoff.verify_handoff_index(root, index)
            self.assertFalse(verify["ok"])
            self.assertTrue(verify["mismatches"])

    def test_expected_agent_folders_schema_index_and_example_exist(self):
        agents = ["claude", "codex", "hermes", "chatgpt", "local_models"]
        for agent in agents:
            for box in ["inbox", "outbox"]:
                self.assertTrue((REPO_ROOT / "14_context" / "memory" / "agent_handoffs" / agent / box / ".gitkeep").is_file())
        expected = [
            "14_context/memory/index/handoff_index.json",
            "14_context/memory/schemas/agent_handoff_packet.schema.json",
            "14_context/memory/examples/agent_handoff_packet.example.json",
        ]
        for path in expected:
            self.assertTrue((REPO_ROOT / path).is_file(), path)

    def test_cli_check_and_validate_are_safe_json(self):
        check = subprocess.run(
            [sys.executable, str(SCRIPT), "--check", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(check.returncode, 0, check.stderr)
        payload = json.loads(check.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["local_only"])
        self.assertFalse(payload["executes_commands"])
        self.assertFalse(payload["live_actions_enabled"])

        validate = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--validate",
                "14_context/memory/examples/agent_handoff_packet.example.json",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(validate.returncode, 0, validate.stderr)
        self.assertTrue(json.loads(validate.stdout)["ok"])

    def test_context_map_surfaces_shared_handoff_index(self):
        result = subprocess.run(
            [sys.executable, str(MEMORY_MAP), "--write", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        context_map = (REPO_ROOT / "14_context" / "memory" / "generated" / "context_map.md").read_text(encoding="utf-8")
        latest_state = (REPO_ROOT / "14_context" / "memory" / "generated" / "latest_state.md").read_text(encoding="utf-8")
        self.assertIn("handoff_index.json", context_map)
        self.assertIn("Shared agent handoffs", latest_state)

    def test_context_map_index_is_stable_across_checkout_mtime_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "state.md"
            source.write_text("# State\n\nStable reviewed truth.\n", encoding="utf-8")
            specs = [{"path": "state.md", "category": "stable_truth", "priority": 1}]
            os.utime(source, (1_700_000_000, 1_700_000_000))
            first = self.memory_map.build_raw_index(root, specs)
            os.utime(source, (1_800_000_000, 1_800_000_000))
            second = self.memory_map.build_raw_index(root, specs)
            self.assertEqual(first, second)

    def test_script_has_no_network_shell_or_command_execution(self):
        text = SCRIPT.read_text(encoding="utf-8")
        forbidden = [
            "import requests",
            "import urllib",
            "import socket",
            "os.system(",
            "shell=True",
            "shell = True",
            "Invoke-Expression",
            "Start-Process",
            "subprocess.Popen",
            "subprocess.call",
            "subprocess.check_",
        ]
        for needle in forbidden:
            self.assertNotIn(needle, text)

    def test_data_only_write_fallback_has_no_packet_command_surface(self):
        helper = self.handoff._NODE_WRITE_SCRIPT
        self.assertIn("writeFileSync", helper)
        self.assertIn("Buffer.from", helper)
        for forbidden in ["child_process", "exec", "spawn", "eval", "shell"]:
            self.assertNotIn(forbidden, helper)
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('["node", "-e", _NODE_WRITE_SCRIPT', text)
        self.assertNotIn('subprocess.run(packet["commands_run"]', text)


if __name__ == "__main__":
    unittest.main()
