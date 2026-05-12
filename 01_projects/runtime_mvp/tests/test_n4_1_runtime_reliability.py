import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from super_ai_agent import queue
from super_ai_agent.models import SupervisorState, Task
from super_ai_agent import storage
from super_ai_agent.cli import _classify_executor_task


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

    def test_executor_action_type_none_does_not_crash_classify(self):
        """N+4.1F: _classify_executor_task(None) must not raise AttributeError.

        Root cause: _build_ghoti_watchdog calls _classify_executor_task(focus_task)
        where focus_task can be None when the task queue is empty on first clean run.
        The old code used task.executor_action_type directly; the fix uses getattr.
        """
        # None task (empty queue on fresh install / first clean run)
        result = _classify_executor_task(None)
        self.assertEqual(result, "repo")  # falls through to default "repo" branch

        # Task with executor_action_type explicitly set to None
        minimal = {
            "task_id": "t2", "title": "T2", "description": "", "risk_level": "low",
            "status": "queued", "requires_approval": False, "approval_state": "not_required",
            "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-01-01T00:00:00Z",
            "executor_action_type": None,
            "executor_target": None,
            "executor_payload": None,
        }
        task = Task.from_dict(minimal)
        result2 = _classify_executor_task(task)
        self.assertEqual(result2, "repo")

        # Task with valid executor_action_type still classifies correctly
        minimal_desktop = dict(minimal)
        minimal_desktop.update({"task_id": "t3", "executor_action_type": "wait_seconds"})
        task_desktop = Task.from_dict(minimal_desktop)
        result3 = _classify_executor_task(task_desktop)
        self.assertEqual(result3, "desktop")

    def test_list_executor_tasks_skips_none_entries(self):
        """N+4.1D/N+4.1F: list_executor_tasks() must never crash on None entries."""
        original_list_tasks = queue.list_tasks

        def patched_list_tasks():
            # Simulate storage returning None entries mixed with real tasks
            minimal = {
                "task_id": "t4", "title": "T4", "description": "", "risk_level": "low",
                "status": "queued", "requires_approval": False, "approval_state": "not_required",
                "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-01-01T00:00:00Z",
                "executor_action_type": "read_file",
                "executor_target": "somefile.txt",
                "executor_payload": {},
            }
            return [None, Task.from_dict(minimal), None]

        queue.list_tasks = patched_list_tasks
        try:
            result = queue.list_executor_tasks()
            # Only the real task with executor_action_type should be returned
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].executor_action_type, "read_file")
        finally:
            queue.list_tasks = original_list_tasks

    def test_read_tasks_skips_null_entries(self):
        """N+4.1H: read_tasks() must not crash when tasks.json contains null entries.

        Root cause: tasks.json=[null] → _read_json_list returns [None] →
        Task.from_dict(None) → None["task_id"] → TypeError: 'NoneType' object
        is not subscriptable.  The fix adds isinstance(item, dict) guard.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tasks_path = Path(tmp) / "tasks.json"
            tasks_path.write_text("[null]", encoding="utf-8")
            original_tasks_path = storage.TASKS_PATH
            storage.TASKS_PATH = tasks_path
            try:
                result = storage.read_tasks()
                self.assertEqual(result, [])  # null entry silently dropped
            finally:
                storage.TASKS_PATH = original_tasks_path

    def test_read_tasks_skips_null_mixed_with_valid(self):
        """N+4.1H: read_tasks() skips nulls but keeps valid dict entries."""
        minimal = {
            "task_id": "t5", "title": "T5", "description": "", "risk_level": "low",
            "status": "queued", "requires_approval": False, "approval_state": "not_required",
            "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-01-01T00:00:00Z",
        }
        payload = json.dumps([None, minimal, None])
        with tempfile.TemporaryDirectory() as tmp:
            tasks_path = Path(tmp) / "tasks.json"
            tasks_path.write_text(payload, encoding="utf-8")
            original_tasks_path = storage.TASKS_PATH
            storage.TASKS_PATH = tasks_path
            try:
                result = storage.read_tasks()
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].task_id, "t5")
            finally:
                storage.TASKS_PATH = original_tasks_path

    def test_read_tasks_skips_malformed_dict_entries(self):
        """N+4.1H: read_tasks() skips dicts missing required keys without crashing."""
        payload = json.dumps([{"not_a_task": True}, {"task_id": "t6", "title": "T6",
            "description": "", "risk_level": "low", "status": "queued",
            "requires_approval": False, "approval_state": "not_required",
            "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-01-01T00:00:00Z"}])
        with tempfile.TemporaryDirectory() as tmp:
            tasks_path = Path(tmp) / "tasks.json"
            tasks_path.write_text(payload, encoding="utf-8")
            original_tasks_path = storage.TASKS_PATH
            storage.TASKS_PATH = tasks_path
            try:
                result = storage.read_tasks()
                # Malformed dict silently dropped, valid dict kept
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].task_id, "t6")
            finally:
                storage.TASKS_PATH = original_tasks_path

    def test_task_store_diagnostics_degraded_for_null_entries(self):
        """N+4.1I: get_task_store_diagnostics() returns degraded/skipped count after [null]."""
        with tempfile.TemporaryDirectory() as tmp:
            tasks_path = Path(tmp) / "tasks.json"
            tasks_path.write_text("[null]", encoding="utf-8")
            original_tasks_path = storage.TASKS_PATH
            storage.TASKS_PATH = tasks_path
            try:
                result = storage.read_tasks()
                self.assertEqual(result, [])
                diag = storage.get_task_store_diagnostics()
                self.assertEqual(diag["skipped_entries"], 1)
                self.assertEqual(diag["status"], "degraded")
            finally:
                storage.TASKS_PATH = original_tasks_path

    def test_task_store_diagnostics_ok_for_valid_entries(self):
        """N+4.1I: get_task_store_diagnostics() returns ok/0 for a valid task list."""
        minimal = json.dumps([{
            "task_id": "t7", "title": "T7", "description": "", "risk_level": "low",
            "status": "queued", "requires_approval": False, "approval_state": "not_required",
            "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-01-01T00:00:00Z",
        }])
        with tempfile.TemporaryDirectory() as tmp:
            tasks_path = Path(tmp) / "tasks.json"
            tasks_path.write_text(minimal, encoding="utf-8")
            original_tasks_path = storage.TASKS_PATH
            storage.TASKS_PATH = tasks_path
            try:
                result = storage.read_tasks()
                self.assertEqual(len(result), 1)
                diag = storage.get_task_store_diagnostics()
                self.assertEqual(diag["skipped_entries"], 0)
                self.assertEqual(diag["status"], "ok")
            finally:
                storage.TASKS_PATH = original_tasks_path

    def test_task_store_diagnostics_counts_mixed_null_and_valid(self):
        """N+4.1I: mixed null+valid entries — diagnostics show correct skipped count."""
        minimal = {
            "task_id": "t8", "title": "T8", "description": "", "risk_level": "low",
            "status": "queued", "requires_approval": False, "approval_state": "not_required",
            "created_at": "2024-01-01T00:00:00Z", "updated_at": "2024-01-01T00:00:00Z",
        }
        payload = json.dumps([None, None, minimal, None])
        with tempfile.TemporaryDirectory() as tmp:
            tasks_path = Path(tmp) / "tasks.json"
            tasks_path.write_text(payload, encoding="utf-8")
            original_tasks_path = storage.TASKS_PATH
            storage.TASKS_PATH = tasks_path
            try:
                result = storage.read_tasks()
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].task_id, "t8")
                diag = storage.get_task_store_diagnostics()
                self.assertEqual(diag["skipped_entries"], 3)  # 3 nulls skipped
                self.assertEqual(diag["status"], "degraded")
            finally:
                storage.TASKS_PATH = original_tasks_path

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

    # -------------------------------------------------------------------------
    # N+4.1J tests: diagnostics stability + Task.from_dict controlled error
    # -------------------------------------------------------------------------

    def test_task_from_dict_none_raises_controlled_type_error(self):
        """N+4.1J: Task.from_dict(None) must raise a controlled TypeError, not
        the raw 'NoneType object is not subscriptable' crash."""
        with self.assertRaises(TypeError) as ctx:
            Task.from_dict(None)
        # Message must be informative, not the raw NoneType subscript error
        self.assertIn("Task.from_dict expected a mapping", str(ctx.exception))

    def test_task_from_dict_non_dict_raises_controlled_type_error(self):
        """N+4.1J: Task.from_dict('bad') must raise a controlled TypeError."""
        with self.assertRaises(TypeError) as ctx:
            Task.from_dict("bad-entry")
        self.assertIn("Task.from_dict expected a mapping", str(ctx.exception))

    def test_read_tasks_with_diagnostics_mixed_store_is_degraded(self):
        """N+4.1J: read_tasks_with_diagnostics() returns degraded/skipped>0 for
        a store containing a valid task, null, a string, and a malformed dict.

        This is the N+4.1I blocker: the mixed store was reporting ok/0 because
        _backfill_pending_approval_requests() wrote the file after the first
        read, stripping invalid entries so subsequent reads saw 0 skipped.
        read_tasks_with_diagnostics() is atomic — the diag reflects THIS read."""
        minimal = {
            "task_id": "t9", "title": "T9", "description": "", "risk_level": "low",
            "status": "queued", "requires_approval": False,
            "approval_state": "not_required",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        payload = json.dumps([minimal, None, "bad-entry", {"random_key": "value"}])
        with tempfile.TemporaryDirectory() as tmp:
            tasks_path = Path(tmp) / "tasks.json"
            tasks_path.write_text(payload, encoding="utf-8")
            original_tasks_path = storage.TASKS_PATH
            storage.TASKS_PATH = tasks_path
            try:
                tasks, diag = storage.read_tasks_with_diagnostics()
                self.assertEqual(len(tasks), 1)
                self.assertEqual(tasks[0].task_id, "t9")
                self.assertEqual(diag["skipped_entries"], 3)
                self.assertEqual(diag["status"], "degraded")
            finally:
                storage.TASKS_PATH = original_tasks_path

    def test_read_tasks_with_diagnostics_valid_only_is_ok(self):
        """N+4.1J: read_tasks_with_diagnostics() returns ok/0 for a clean store."""
        minimal = json.dumps([{
            "task_id": "t10", "title": "T10", "description": "", "risk_level": "low",
            "status": "queued", "requires_approval": False,
            "approval_state": "not_required",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }])
        with tempfile.TemporaryDirectory() as tmp:
            tasks_path = Path(tmp) / "tasks.json"
            tasks_path.write_text(minimal, encoding="utf-8")
            original_tasks_path = storage.TASKS_PATH
            storage.TASKS_PATH = tasks_path
            try:
                tasks, diag = storage.read_tasks_with_diagnostics()
                self.assertEqual(len(tasks), 1)
                self.assertEqual(diag["skipped_entries"], 0)
                self.assertEqual(diag["status"], "ok")
            finally:
                storage.TASKS_PATH = original_tasks_path

    def test_read_tasks_with_diagnostics_pure_invalid_is_degraded(self):
        """N+4.1J: read_tasks_with_diagnostics() returns degraded for [null, 'bad']."""
        with tempfile.TemporaryDirectory() as tmp:
            tasks_path = Path(tmp) / "tasks.json"
            tasks_path.write_text(json.dumps([None, "bad"]), encoding="utf-8")
            original_tasks_path = storage.TASKS_PATH
            storage.TASKS_PATH = tasks_path
            try:
                tasks, diag = storage.read_tasks_with_diagnostics()
                self.assertEqual(tasks, [])
                self.assertEqual(diag["skipped_entries"], 2)
                self.assertEqual(diag["status"], "degraded")
            finally:
                storage.TASKS_PATH = original_tasks_path

    def test_diagnostics_stable_after_subsequent_clean_read(self):
        """N+4.1J: diag returned by read_tasks_with_diagnostics() is a snapshot
        and does not change when a subsequent read_tasks() call resets the counter.

        This is the core stability guarantee: even if another code path calls
        read_tasks() on a now-clean file (post-backfill write), the captured
        diag dict still reflects the original mixed-store read."""
        minimal = {
            "task_id": "t11", "title": "T11", "description": "", "risk_level": "low",
            "status": "queued", "requires_approval": False,
            "approval_state": "not_required",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        payload = json.dumps([minimal, None])  # 1 valid + 1 null
        with tempfile.TemporaryDirectory() as tmp:
            tasks_path = Path(tmp) / "tasks.json"
            tasks_path.write_text(payload, encoding="utf-8")
            original_tasks_path = storage.TASKS_PATH
            storage.TASKS_PATH = tasks_path
            try:
                # First read: mixed store — captures degraded/1
                _tasks, diag = storage.read_tasks_with_diagnostics()
                self.assertEqual(diag["skipped_entries"], 1)
                self.assertEqual(diag["status"], "degraded")

                # Simulate post-backfill: overwrite file with only valid task
                tasks_path.write_text(json.dumps([minimal]), encoding="utf-8")

                # Second read (clean file) resets module-global to 0
                storage.read_tasks()
                self.assertEqual(storage._last_task_store_skipped, 0)

                # But the captured diag is still correct — it's a snapshot
                self.assertEqual(diag["skipped_entries"], 1,
                    "captured diag must not be mutated by subsequent clean reads")
                self.assertEqual(diag["status"], "degraded")
            finally:
                storage.TASKS_PATH = original_tasks_path


if __name__ == '__main__':
    unittest.main()
