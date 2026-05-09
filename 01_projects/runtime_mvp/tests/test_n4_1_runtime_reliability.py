import subprocess
import tempfile
import unittest
from pathlib import Path

from super_ai_agent import queue
from super_ai_agent.models import SupervisorState, Task
from super_ai_agent import storage


class N41RuntimeReliabilityTests(unittest.TestCase):
    def test_supervisor_state_from_old_json_defaults_ready_to_resume_count(self):
        state = SupervisorState.from_dict({})
        self.assertEqual(state.ready_to_resume_count, 0)

    def test_desktop_bridge_timeout_becomes_runtime_error(self):
        original_run = queue.subprocess.run

        def raise_timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs.get('timeout'))

        queue.subprocess.run = raise_timeout
        try:
            with self.assertRaisesRegex(RuntimeError, 'timed out'):
                queue._invoke_desktop_bridge_action(action_type='wait_seconds', target='0')
        finally:
            queue.subprocess.run = original_run

    def test_desktop_bridge_invocation_uses_timeout(self):
        original_run = queue.subprocess.run
        captured = {}

        class Result:
            returncode = 0
            stdout = 'status: ok\nwaited_seconds: 0\nheadline: Waited without hanging.\n'
            stderr = ''

        def fake_run(*args, **kwargs):
            captured.update(kwargs)
            return Result()

        queue.subprocess.run = fake_run
        try:
            result = queue._invoke_desktop_bridge_action(action_type='wait_seconds', target='0')
        finally:
            queue.subprocess.run = original_run

        self.assertEqual(result['summary'], 'Waited without hanging.')
        self.assertIn('timeout', captured)
        self.assertGreater(captured['timeout'], 0)

    def test_task_from_dict_null_executor_action_type_becomes_empty_string(self):
        minimal = {
            "task_id": "t1", "title": "T", "description": "", "risk_level": "low",
            "status": "queued", "requires_approval": False, "approval_state": "not_required",
            "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-01-01T00:00:00Z",
            "executor_action_type": None,
            "executor_target": None,
            "executor_payload": None,
        }
        task = Task.from_dict(minimal)
        self.assertEqual(task.executor_action_type, "")
        self.assertEqual(task.executor_target, "")
        self.assertIsInstance(task.executor_payload, dict)

    def test_runtime_data_lock_recovers_dead_owner_lock(self):
        original_lock_path = storage.RUNTIME_LOCK_PATH
        with tempfile.TemporaryDirectory() as tmp:
            stale_lock = Path(tmp) / '.runtime_data.lock'
            stale_lock.write_text(
                'pid=999999 created_at=2000-01-01T00:00:00Z',
                encoding='utf-8',
            )
            storage.RUNTIME_LOCK_PATH = stale_lock
            try:
                with storage.runtime_data_lock(timeout_seconds=0.1, poll_seconds=0.01):
                    self.assertTrue(stale_lock.exists())
            finally:
                storage.RUNTIME_LOCK_PATH = original_lock_path


if __name__ == '__main__':
    unittest.main()
