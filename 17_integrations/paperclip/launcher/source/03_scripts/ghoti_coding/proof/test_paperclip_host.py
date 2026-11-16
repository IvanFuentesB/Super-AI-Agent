"""Focused contract tests for the explicitly authorized local Paperclip host."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import sys
import tempfile
import types
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location('paperclip_host', Path(__file__).parents[1] / 'paperclip_host.py')
host = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(host)


class PaperclipHostTests(unittest.TestCase):
    def test_service_lease_requires_integer_within_authorized_maximum(self):
        for invalid in (0, -1, 1201, 1.5, True, '1200', None, float('nan'), float('inf'), -float('inf')):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                host.validate_lease(invalid)
        for valid in (1, 300, 1200):
            self.assertEqual(host.validate_lease(valid), valid)

    def test_omitted_duration_remains_300_and_longer_duration_is_explicit(self):
        for argv, expected in (([], 300), (['--seconds', '1200'], 1200)):
            with self.subTest(argv=argv), mock.patch.object(sys, 'argv', ['host', *argv]), \
                    mock.patch.object(host, 'run', return_value=0) as run:
                self.assertEqual(host.main(), 0)
                run.assert_called_once_with(expected)

    def test_invalid_cli_duration_never_reaches_process_start(self):
        for value in ('0', '-1', '1201', 'nan', 'inf', '-inf', '1.5', 'invalid'):
            with self.subTest(value=value), mock.patch.object(sys, 'argv', ['host', '--seconds', value]), \
                    mock.patch.object(host, 'run') as run, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises((ValueError, SystemExit)):
                    host.main()
                run.assert_not_called()

    def test_config_is_authenticated_and_all_writable_paths_are_task_owned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            config = host.configuration(root)
            self.assertEqual(config['server']['deploymentMode'], 'authenticated')
            self.assertEqual(config['server']['host'], '127.0.0.1')
            self.assertEqual(config['server']['port'], 41402)
            self.assertEqual(config['database']['embeddedPostgresPort'], 41401)
            self.assertFalse(config['telemetry']['enabled'])
            self.assertFalse(config['database']['backup']['enabled'])
            for location in (config['database']['embeddedPostgresDataDir'], config['logging']['logDir'],
                             config['storage']['localDisk']['baseDir'], config['secrets']['localEncrypted']['keyFilePath']):
                self.assertTrue(Path(location).is_relative_to(root))

    def test_existing_configuration_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = host.ensure_configuration(root)
            original = target.read_bytes()
            self.assertEqual(host.ensure_configuration(root).read_bytes(), original)
            target.write_text('{}', encoding='utf-8')
            with self.assertRaises(ValueError):
                host.ensure_configuration(root)
            self.assertEqual(target.read_text(), '{}')

    def test_environment_preserves_native_policy_and_disables_scheduling(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            environment = host.environment(root, {'PATH': 'existing', 'POLICY_SENTINEL': 'preserved'})
            self.assertEqual(environment['POLICY_SENTINEL'], 'preserved')
            self.assertEqual(environment['HEARTBEAT_SCHEDULER_ENABLED'], 'false')
            self.assertEqual(environment['PAPERCLIP_UI_DEV_MIDDLEWARE'], 'false')
            for key in ('NODE_OPTIONS', 'NODE_PATH', 'DATABASE_URL', 'OPENAI_API_KEY', 'PAPERCLIP_CONFIG'):
                with self.subTest(key=key), self.assertRaises(PermissionError):
                    host.environment(root, {key: 'do-not-clear'})

    def test_effective_auth_is_required_for_readiness(self):
        good = dict(health={'status': 'ok', 'deploymentMode': 'authenticated'},
                    ui_status=200, unauthenticated_companies_status=403,
                    invalid_bearer_status=403, untrusted_host_status=403)
        host.validate_readiness(good)
        for key, bad in [('health', {'status':'ok','deploymentMode':'local_trusted'}),
                         ('ui_status', 500), ('unauthenticated_companies_status', 200),
                         ('invalid_bearer_status', 200), ('untrusted_host_status', 200)]:
            with self.subTest(key=key), self.assertRaises(PermissionError):
                host.validate_readiness({**good, key:bad})

    def test_dotenv_cannot_redirect_database_or_startup(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.env'
            path.write_text('PAPERCLIP_AGENT_JWT_SECRET=' + 'a'*64 + '\n')
            host.validate_dotenv(path)
            for extra in ['DATABASE_URL=postgres://example.invalid/db', 'NODE_OPTIONS=--inspect',
                          'PAPERCLIP_AGENT_JWT_SECRET=' + 'b'*64]:
                path.write_text('PAPERCLIP_AGENT_JWT_SECRET=' + 'a'*64 + '\n' + extra)
                with self.subTest(extra=extra.split('=')[0]), self.assertRaises(PermissionError):
                    host.validate_dotenv(path)

    def test_listener_scope_rejects_public_foreign_and_fallback_ports(self):
        allowed = {10, 11}
        host.validate_listeners([{'pid': 10, 'host': '127.0.0.1', 'port': 41402},
                                 {'pid': 11, 'host': '::1', 'port': 41401}], allowed)
        for row in ({'pid': 10, 'host': '0.0.0.0', 'port': 41402},
                    {'pid': 99, 'host': '127.0.0.1', 'port': 41402},
                    {'pid': 10, 'host': '127.0.0.1', 'port': 41403}):
            with self.subTest(row=row), self.assertRaises(PermissionError):
                host.validate_listeners([row], allowed)


class ReviewRegressionTests(unittest.TestCase):
    def test_git_overrides_are_rejected_not_cleared(self):
        for name in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_CONFIG_COUNT', 'git_config_global'):
            supplied = {name: 'review-fixture'}
            with self.subTest(name=name), self.assertRaises(PermissionError):
                host.environment(Path('fixture'), supplied)
            self.assertEqual(supplied, {name: 'review-fixture'})
        self.assertEqual(host.environment(Path('fixture'), {'GIT_PAGER':'fixture-pager'})['GIT_PAGER'],
                         'fixture-pager')

    def test_installation_rejects_git_override_before_any_subprocess(self):
        with mock.patch.dict(host.os.environ, {'GIT_DIR': 'fixture'}, clear=True), \
                mock.patch.object(host.subprocess, 'check_output') as old_git, \
                mock.patch.object(host, 'load_helpers', create=True) as helpers:
            with self.assertRaises(PermissionError):
                host.installation_check()
            old_git.assert_not_called()
            helpers.assert_not_called()

    def test_dangling_dotenv_is_rejected_before_exists(self):
        dangling = mock.Mock(spec=Path)
        dangling.exists.return_value = False
        dangling.lstat.return_value = types.SimpleNamespace(st_mode=stat.S_IFLNK, st_file_attributes=0)
        dangling.parents = ()
        with self.assertRaises(PermissionError):
            host.validate_dotenv(dangling)
        dangling.read_text.assert_not_called()

    def test_dangling_installation_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source'
            source.mkdir()
            original_lstat = Path.lstat
            def lstat(path):
                if path == source:
                    return types.SimpleNamespace(st_mode=stat.S_IFLNK, st_file_attributes=0)
                return original_lstat(path)
            with mock.patch.object(host, 'SOURCE', source), mock.patch.object(Path, 'lstat', lstat), \
                    mock.patch.dict(host.os.environ, {}, clear=True), \
                    mock.patch.object(host, 'load_helpers', create=True) as helpers:
                with self.assertRaises(PermissionError):
                    host.installation_check()
                helpers.assert_not_called()

    def test_helper_pin_drift_prevents_import(self):
        with tempfile.TemporaryDirectory() as directory:
            native = Path(directory)
            helper = native / '03_scripts/fixture.py'
            helper.parent.mkdir()
            helper.write_text('not an executable fixture')
            with mock.patch.object(host, 'NATIVE', native), \
                    mock.patch.object(host, 'HELPER_HASHES', {'fixture.py': '0'*64}):
                with self.assertRaises(PermissionError):
                    host.load_helpers()

    def test_git_inspection_uses_bounded_helper_and_safe_diff_flags(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source'
            state = Path(directory) / 'state'
            source.mkdir()
            artifacts = {}
            for name in ('one.ts', 'two.ts'):
                raw = name.encode('ascii')
                (source / name).write_bytes(raw)
                artifacts[name] = ('a' * 40, host.hashlib.sha256(raw).hexdigest(), len(raw))
            bounded = mock.Mock(side_effect=[
                {'exit_code':0, 'timed_out':False, 'output_overflow':False, 'stdout':host.SOURCE_REVISION},
                {'exit_code':0, 'timed_out':False, 'output_overflow':False, 'stdout':str(source)},
                {'exit_code':0, 'timed_out':False, 'output_overflow':False, 'stdout':'a' * 40},
                {'exit_code':0, 'timed_out':False, 'output_overflow':False, 'stdout':'a' * 40},
                {'exit_code':0, 'timed_out':False, 'output_overflow':False, 'stdout':''}])
            helpers = types.SimpleNamespace(inspect_git=bounded)
            with mock.patch.object(host, 'SOURCE', source), mock.patch.object(host, 'STATE', state), \
                    mock.patch.object(host, 'DEPLOYED_SOURCE_FILES', artifacts), \
                    mock.patch.dict(host.os.environ, {}, clear=True), mock.patch.object(Path, 'is_file', return_value=True), \
                    mock.patch.object(host, 'load_helpers', return_value=helpers, create=True), \
                    mock.patch.object(host.subprocess, 'check_output') as old_git:
                self.assertEqual(host.installation_check(), host.SOURCE_REVISION)
            old_git.assert_not_called()
            self.assertEqual(bounded.call_count, 5)
            self.assertEqual(bounded.call_args_list[2].args[1:], ('rev-parse', 'HEAD:one.ts'))
            self.assertEqual(bounded.call_args_list[3].args[1:], ('rev-parse', 'HEAD:two.ts'))
            args = bounded.call_args_list[-1].args
            self.assertIn('--no-ext-diff', args)
            self.assertIn('--no-textconv', args)
            self.assertIn(':(exclude)one.ts', args)
            self.assertIn(':(exclude)two.ts', args)

    def lifecycle(self, scenario, seconds=300, with_receiver=False):
        """No subprocess, socket, credential or real timing is used."""
        alive = [True]
        process = types.SimpleNamespace(pid=900001, returncode=None, stdout=io.BytesIO(b'fixture log'), stderr=io.BytesIO())
        process.poll = lambda: None if alive[0] else process.returncode
        owner = types.SimpleNamespace(p=process)
        def stop():
            alive[0] = False
            process.returncode = 0
        owner.stop = mock.Mock(side_effect=stop)
        receiver_alive = [scenario != 'receiver_failed']
        rp = types.SimpleNamespace(pid=900002, returncode=None if receiver_alive[0] else 3,
            stdout=io.BytesIO(b'{"stage":"cli_challenge_created","token":"fixture-secret"}\n'),
            stderr=io.BytesIO(b'fixture-secret-bearing-stderr\n'))
        rp.poll = lambda: None if receiver_alive[0] else rp.returncode
        def receiver_stop():
            receiver_alive[0] = False
            if rp.returncode is None:
                rp.returncode = 0
        receiver = types.SimpleNamespace(p=rp, stop=mock.Mock(side_effect=receiver_stop))
        factory = mock.Mock(return_value=receiver)
        class Gone(Exception):
            pass
        def observe(pid):
            if (pid == rp.pid and not receiver_alive[0]) or (pid != rp.pid and not alive[0]):
                raise Gone()
            return types.SimpleNamespace(pid=pid, create_time=lambda: 1.0, name=lambda: 'fixture.exe', children=lambda **k: [])
        calls = [0]
        def connections(**kwargs):
            calls[0] += 1
            if calls[0] == 1 or not alive[0]:
                return []
            address = '0.0.0.0' if scenario == 'public' else '127.0.0.1'
            return [types.SimpleNamespace(status='LISTEN', pid=process.pid,
                    laddr=types.SimpleNamespace(ip=address, port=port)) for port in (41401,41402)]
        fake_psutil = types.SimpleNamespace(Process=observe, net_connections=connections, NoSuchProcess=Gone)
        callbacks = []
        delays = []
        class Timer:
            def __init__(self, delay, callback):
                self.callback = callback
                callbacks.append(callback)
                delays.append(delay)
            def start(self):
                pass
            def cancel(self):
                pass
        class Thread:
            def __init__(self, target, args, **kwargs):
                self.target, self.args, self.ident = target, args, None
            def start(self):
                self.ident = 1
                try:
                    self.target(*self.args)
                except OSError:
                    pass  # Mimics an uncaught background-thread exception.
            def join(self, **kwargs):
                pass
            def is_alive(self):
                return False
        def request(path, headers=None):
            if path == '/api/health':
                if scenario == 'readiness':
                    return 503, b'{}'
                mode = 'local_trusted' if scenario == 'auth' else 'authenticated'
                return 200, json.dumps({'status':'ok','deploymentMode':mode}).encode()
            return (200 if path == '/' else 403), b''
        helpers = types.SimpleNamespace(OwnedProcess=mock.Mock(return_value=owner),
                  run_process=mock.Mock(return_value={'exit_code':0}),
                  InstanceLock=lambda *args: contextlib.nullcontext())
        legacy_modules = {
            'psutil': fake_psutil,
            'ghoti_external_tasks.process': types.SimpleNamespace(OwnedProcess=helpers.OwnedProcess),
            'ghoti_external_tasks.common': types.SimpleNamespace(run_process=helpers.run_process),
            'ghoti_runtime.process_control': types.SimpleNamespace(InstanceLock=helpers.InstanceLock)}
        original_open = Path.open
        def open_path(path, *args, **kwargs):
            if scenario == 'log_io' and path.name in ('stdout.log','stderr.log'):
                raise OSError('fixture log failure')
            return original_open(path, *args, **kwargs)
        ticks = [0]
        def monotonic():
            ticks[0] += 1
            return (0 if ticks[0] <= 2 else 181) if scenario == 'readiness' else ticks[0]*0.01
        with tempfile.TemporaryDirectory() as directory, contextlib.ExitStack() as stack:
            state = Path(directory)
            config_bytes = host.ensure_configuration(state).read_bytes()
            (state / 'db').mkdir()
            marker = state / 'db/PG_VERSION'
            marker.write_bytes(b'inert-database-fixture')
            stack.enter_context(mock.patch.dict(sys.modules, legacy_modules))
            stack.enter_context(mock.patch.dict(host.os.environ, {}, clear=True))
            stack.enter_context(mock.patch.object(host, 'STATE', state))
            stack.enter_context(mock.patch.object(host, 'installation_check', return_value=host.SOURCE_REVISION))
            stack.enter_context(mock.patch.object(host, 'load_helpers', return_value=helpers, create=True))
            stack.enter_context(mock.patch.object(host.threading, 'Timer', Timer))
            stack.enter_context(mock.patch.object(host.threading, 'Thread', Thread))
            stack.enter_context(mock.patch.object(host.time, 'monotonic', monotonic))
            def tick(_):
                if scenario == 'cancel':
                    raise KeyboardInterrupt()
                if scenario == 'service_exit':
                    alive[0] = False
                    process.returncode = 5
                else:
                    callbacks[0]()
            stack.enter_context(mock.patch.object(host.time, 'sleep', side_effect=tick))
            stack.enter_context(mock.patch.object(host, 'request', request))
            stack.enter_context(mock.patch.object(Path, 'open', open_path))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            options = {'receiver_factory': factory} if with_receiver else {}
            if scenario in ('auth','public','cancel'):
                with self.assertRaises(KeyboardInterrupt if scenario == 'cancel' else PermissionError):
                    host.run(seconds, **options)
                result = 1
            else:
                result = host.run(seconds, **options)
            receipts = list((state/'sessions').glob('*/receipt.json'))
            self.assertEqual(len(receipts),1)
            record = json.loads(receipts[0].read_text())
            self.assertEqual((state / 'config.json').read_bytes(), config_bytes)
            self.assertEqual(marker.read_bytes(), b'inert-database-fixture')
            self.assertEqual(len(delays), 1)
            self.assertGreater(delays[0], 0)
            self.assertLessEqual(delays[0], seconds)
            if with_receiver:
                factory.assert_called_once()
                self.assertEqual(factory.call_args.args[-1], record['deadline_utc'])
                receiver.stop.assert_called_once()
                logs = ''.join(file.read_text() for file in receipts[0].parent.glob('receiver.*.jsonl'))
                self.assertNotIn('fixture-secret', logs)
        owner.stop.assert_called_once()
        self.assertTrue(record['cleanup_verified'])
        return result,record

    def test_mocked_lifecycle_expiry_is_not_renewed(self):
        result,record = self.lifecycle('expiry')
        self.assertEqual(result,0)
        self.assertEqual(record['reason'],'lease_expired')
        self.assertFalse(record['auto_renewal'])

    def test_explicit_1200_uses_one_fixed_deadline_and_preserves_state(self):
        from datetime import datetime
        result, record = self.lifecycle('expiry', 1200)
        self.assertEqual(result, 0)
        self.assertEqual(record['lease_seconds'], 1200)
        span = datetime.fromisoformat(record['deadline_utc']) - datetime.fromisoformat(record['started_utc'])
        self.assertEqual(span.total_seconds(), 1200)

    def test_same_timer_stops_pending_receiver_and_server(self):
        result, record = self.lifecycle('expiry', 1200, with_receiver=True)
        self.assertEqual(result, 0)
        self.assertEqual(record['reason'], 'lease_expired')

    def test_receiver_failure_immediately_ends_owned_service(self):
        result, record = self.lifecycle('receiver_failed', 1200, with_receiver=True)
        self.assertEqual(result, 1)
        self.assertEqual(record['receiver_exit_code'], 3)
        self.assertEqual(record['reason'], 'receiver_failed')

    def test_service_exit_ends_pending_receiver(self):
        result, record = self.lifecycle('service_exit', 1200, with_receiver=True)
        self.assertEqual(result, 1)
        self.assertEqual(record['reason'], 'application_exited')

    def test_user_cancellation_stops_both_trees(self):
        result, record = self.lifecycle('cancel', 1200, with_receiver=True)
        self.assertEqual(record['reason'], 'host_exception:KeyboardInterrupt')

    def test_mocked_lifecycle_auth_failure_stops_once(self):
        self.lifecycle('auth')

    def test_mocked_lifecycle_public_binding_stops_once(self):
        self.lifecycle('public')

    def test_mocked_lifecycle_readiness_timeout_stops_once(self):
        result,record = self.lifecycle('readiness')
        self.assertNotEqual(result,0)
        self.assertEqual(record['reason'],'readiness_timeout')

    def test_mocked_lifecycle_log_io_failure_cannot_pass(self):
        result,record = self.lifecycle('log_io')
        self.assertNotEqual(result,0)
        self.assertEqual(record['reason'],'log_failure')


if __name__ == '__main__':
    unittest.main()
