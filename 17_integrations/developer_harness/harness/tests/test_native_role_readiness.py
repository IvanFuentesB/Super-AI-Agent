import contextlib
import copy
import io
import json
import pathlib
import queue
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from scripts import native_config_probe as probe
from scripts import native_role_readiness as readiness


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        shutil.copytree(ROOT / '.codex', self.root / '.codex')
        self.receipt = {
            'initialize_ok': True, 'config_error': None, 'models_error': None,
            'agents': {'enabled': True, 'default_subagent_model': 'gpt-6-luna',
                       'default_subagent_reasoning_effort': 'medium'},
            'layers': [{'name': {'type': 'project',
                                'dotCodexFolder': str(self.root / '.codex')},
                        'disabledReason': None}],
            'models': [{'id': model, 'model': model,
                        'efforts': [{'reasoningEffort': effort} for effort in efforts]}
                       for model, efforts in [('gpt-6-luna', ['medium']),
                                             ('gpt-6.1-sol', ['high', 'ultra'])]],
            'model': 'gpt-6.1-sol', 'model_reasoning_effort': 'ultra',
        }

    def check(self):
        return readiness.check_readiness(self.root, self.receipt)

    def edit_role(self, text):
        (self.root / '.codex/agents/explorer.toml').write_text(text, encoding='utf-8')

    def test_valid_configuration_is_not_selection_proof(self):
        result = self.check()
        self.assertEqual(result['status'], 'configured')
        self.assertFalse(result['native_role_selection_proven'])
        self.assertEqual(set(result['roles']),
                         {'explorer', 'implementer', 'tester', 'reviewer', 'integrator'})

    def test_missing_receipt_is_pending(self):
        self.receipt = None
        self.assertEqual(self.check()['status'], 'pending')

    def test_absent_project_layer_is_pending(self):
        self.receipt['layers'] = []
        self.assertEqual(self.check()['status'], 'pending')

    def test_disabled_project_layer_is_pending(self):
        self.receipt['layers'][0]['disabledReason'] = 'untrusted'
        self.assertEqual(self.check()['status'], 'pending')

    def test_another_projects_layer_is_pending(self):
        self.receipt['layers'][0]['name']['dotCodexFolder'] = str(self.root / 'other')
        self.assertEqual(self.check()['status'], 'pending')

    def test_agents_must_be_explicitly_enabled(self):
        for agents in (None, {}, {'enabled': False}, {'enabled': 'true'}):
            with self.subTest(agents=agents):
                self.receipt['agents'] = agents
                self.assertEqual(self.check()['status'], 'pending')

    def test_malformed_role_is_invalid(self):
        self.edit_role('name = [')
        self.assertEqual(self.check()['status'], 'invalid')

    def test_malformed_project_config_is_invalid(self):
        (self.root / '.codex/config.toml').write_text('[agents', encoding='utf-8')
        self.assertEqual(self.check()['status'], 'invalid')

    def test_disabled_source_agents_are_pending(self):
        (self.root / '.codex/config.toml').write_text('[agents]\nenabled = false', encoding='utf-8')
        self.assertEqual(self.check()['status'], 'pending')

    def test_required_fields_must_be_nonempty_strings(self):
        path = self.root / '.codex/agents/explorer.toml'
        original = path.read_text(encoding='utf-8')
        for field in ('name', 'description', 'model', 'model_reasoning_effort',
                      'developer_instructions'):
            with self.subTest(field=field):
                self.edit_role('\n'.join(line for line in original.splitlines()
                                         if not line.startswith(field + ' =')))
                self.assertEqual(self.check()['status'], 'invalid')
        self.edit_role(original.replace('name = "explorer"', 'name = 5'))
        self.assertEqual(self.check()['status'], 'invalid')
        self.edit_role(original.replace('name = "explorer"', 'name = " "'))
        self.assertEqual(self.check()['status'], 'invalid')

    def test_all_five_role_names_are_required(self):
        self.edit_role('name = "other"')
        self.assertEqual(self.check()['status'], 'invalid')
        (self.root / '.codex/agents/tester.toml').unlink()
        self.assertEqual(self.check()['status'], 'invalid')

    def test_extra_role_is_invalid(self):
        shutil.copyfile(self.root / '.codex/agents/tester.toml',
                        self.root / '.codex/agents/extra.toml')
        self.assertEqual(self.check()['status'], 'invalid')

    def test_unsupported_role_model_or_effort_is_invalid(self):
        path = self.root / '.codex/agents/explorer.toml'
        original = path.read_text(encoding='utf-8')
        for old, new in [('gpt-6-luna', 'unknown'), ('medium', 'ultra')]:
            with self.subTest(new=new):
                self.edit_role(original.replace(old, new))
                self.assertEqual(self.check()['status'], 'invalid')

    def test_unsupported_default_model_or_effort_is_invalid(self):
        for key in ('default_subagent_model', 'default_subagent_reasoning_effort'):
            receipt = copy.deepcopy(self.receipt)
            receipt['agents'][key] = 'unsupported'
            self.assertEqual(readiness.check_readiness(self.root, receipt)['status'], 'invalid')

    def test_explicit_source_defaults_override_valid_receipt_for_validation(self):
        path = self.root / '.codex/config.toml'
        for prefix, fields in [('[agents]\nenabled = true\n',
                                ('default_subagent_model', 'default_subagent_reasoning_effort')),
                               ('', ('model', 'model_reasoning_effort'))]:
            for field in fields:
                for value in ('"unsupported"', '2026-11-13'):
                    with self.subTest(field=field, value=value):
                        suffix = '' if prefix else '\n[agents]\nenabled = true\n'
                        path.write_text(prefix + f'{field} = {value}\n' + suffix, encoding='utf-8')
                        result = self.check()
                        self.assertEqual(result['status'], 'invalid')
                        self.assertTrue(result['errors'])
                        json.dumps(result)

    def test_omitted_source_default_counterpart_uses_effective_receipt(self):
        path = self.root / '.codex/config.toml'
        for text, status in [
                ('[agents]\nenabled = true\ndefault_subagent_model = "gpt-6.1-sol"', 'invalid'),
                ('[agents]\nenabled = true\ndefault_subagent_reasoning_effort = "high"', 'invalid'),
                ('[agents]\nenabled = true\ndefault_subagent_model = "gpt-6-luna"', 'configured'),
                ('[agents]\nenabled = true\ndefault_subagent_reasoning_effort = "medium"', 'configured'),
                ('model = "gpt-6-luna"\n[agents]\nenabled = true', 'invalid'),
                ('model_reasoning_effort = "medium"\n[agents]\nenabled = true', 'invalid'),
                ('model = "gpt-6.1-sol"\n[agents]\nenabled = true', 'configured'),
                ('model_reasoning_effort = "ultra"\n[agents]\nenabled = true', 'configured')]:
            with self.subTest(text=text):
                path.write_text(text, encoding='utf-8')
                self.assertEqual(self.check()['status'], status)

    def test_malformed_native_project_folders_are_invalid(self):
        for folder in (None, 42, '', '.codex', 'C:relative/.codex', '\x00',
                       str(self.root / 'bad\x00path')):
            with self.subTest(folder=folder):
                self.receipt['layers'][0]['name']['dotCodexFolder'] = folder
                result = self.check()
                self.assertEqual(result['status'], 'invalid')
                self.assertTrue(result['errors'])
                self.assertFalse(result['native_role_selection_proven'])
                json.dumps(result)

    def test_partial_source_defaults_without_native_agents_remain_pending(self):
        path = self.root / '.codex/config.toml'
        self.receipt['layers'] = []
        for agents in ({}, None):
            self.receipt['agents'] = agents
            for field, value in [('default_subagent_model', 'gpt-6-luna'),
                                 ('default_subagent_reasoning_effort', 'medium')]:
                with self.subTest(agents=agents, field=field):
                    path.write_text(f'[agents]\nenabled = true\n{field} = "{value}"',
                                    encoding='utf-8')
                    result = self.check()
                    self.assertEqual(result['status'], 'pending')
                    self.assertEqual(result['errors'], [])
                    self.assertFalse(result['native_role_selection_proven'])

    def test_unsupported_partial_or_paired_defaults_without_native_agents_are_invalid(self):
        self.receipt['layers'] = []
        self.receipt['agents'] = {}
        for text in ('default_subagent_model = "unknown"',
                     'default_subagent_reasoning_effort = "unknown"',
                     'default_subagent_model = 2026-11-13',
                     'default_subagent_reasoning_effort = 2026-11-13',
                     'default_subagent_model = "gpt-6-luna"\ndefault_subagent_reasoning_effort = "high"'):
            with self.subTest(text=text):
                (self.root / '.codex/config.toml').write_text(
                    '[agents]\nenabled = true\n' + text, encoding='utf-8')
                self.assertEqual(self.check()['status'], 'invalid')

    def test_enabled_effective_partial_defaults_remain_pending(self):
        path = self.root / '.codex/config.toml'
        for field, value in [('default_subagent_model', 'gpt-6-luna'),
                             ('default_subagent_reasoning_effort', 'medium')]:
            for source in ('', f'{field} = "{value}"'):
                with self.subTest(field=field, source=source):
                    path.write_text('[agents]\nenabled = true\n' + source, encoding='utf-8')
                    self.receipt['agents'] = {'enabled': True, field: value}
                    result = self.check()
                    self.assertEqual(result['status'], 'pending', result['errors'])
                    self.assertEqual(result['errors'], [])
                    self.assertTrue(result['pending'])
                    self.assertFalse(result['native_role_selection_proven'])

    def test_enabled_effective_unsupported_defaults_remain_invalid(self):
        (self.root / '.codex/config.toml').write_text('[agents]\nenabled = true', encoding='utf-8')
        for fields in ({'default_subagent_model': 'unknown'},
                       {'default_subagent_reasoning_effort': 'unknown'},
                       {'default_subagent_model': 42},
                       {'default_subagent_reasoning_effort': False},
                       {'default_subagent_model': 'gpt-6-luna',
                        'default_subagent_reasoning_effort': 'high'}):
            with self.subTest(fields=fields):
                self.receipt['agents'] = {'enabled': True, **fields}
                self.assertEqual(self.check()['status'], 'invalid')

    def test_cli_relative_project_folder_is_invalid_from_target_cwd(self):
        self.receipt['layers'][0]['name']['dotCodexFolder'] = '.codex'
        receipt = self.root / 'receipt.json'
        receipt.write_text(json.dumps(self.receipt), encoding='utf-8')
        result = subprocess.run([
            sys.executable, '-B', str(ROOT / 'scripts/native_role_readiness.py'),
            '--project-root', str(self.root), '--receipt', str(receipt), '--json'],
            cwd=self.root, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'invalid')
        self.assertEqual(result.stderr, '')

    def test_policy_overrides_are_invalid(self):
        path = self.root / '.codex/agents/explorer.toml'
        original = path.read_text(encoding='utf-8')
        for override in ('sandbox_mode = "read-only"', 'approval_policy = "never"',
                         '[mcp_servers.local]\ncommand = "unused"',
                         '[sandbox_workspace_write]\nnetwork_access = true',
                         'permissions = "custom"'):
            with self.subTest(override=override):
                self.edit_role(original + '\n' + override)
                self.assertEqual(self.check()['status'], 'invalid')

    def test_failed_protocol_receipt_is_invalid(self):
        for key, value in [('initialize_ok', False), ('config_error', 'failed'),
                           ('models_error', 'failed')]:
            receipt = copy.deepcopy(self.receipt)
            receipt[key] = value
            self.assertEqual(readiness.check_readiness(self.root, receipt)['status'], 'invalid')

    def test_malformed_receipt_shapes_are_invalid(self):
        for receipt in ([], {'layers': 'bad'}, {**self.receipt, 'models': None},
                        {**self.receipt, 'layers': {}}, {**self.receipt, 'models': [{}]}):
            with self.subTest(receipt=receipt):
                self.assertEqual(readiness.check_readiness(self.root, receipt)['status'], 'invalid')

    def test_metadata_identifies_only_source_and_retained_defaults(self):
        result = self.check()
        self.assertEqual(result['source']['config_path'], str((self.root / '.codex/config.toml').resolve()))
        self.assertEqual(len(result['source']['config_sha256']), 64)
        self.assertEqual(result['source']['parent_default'],
                         {'model': 'gpt-6.1-sol', 'effort': 'ultra'})
        self.assertEqual(len(result['roles']['explorer']['sha256']), 64)

    def test_no_ad_hoc_selection_flag_is_accepted(self):
        self.receipt['native_role_selection_proven'] = True
        self.assertFalse(self.check()['native_role_selection_proven'])

    def test_function_is_read_only_and_preserves_receipt(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        receipt = copy.deepcopy(self.receipt)
        with patch('subprocess.Popen', side_effect=AssertionError('process')), \
                patch('socket.socket', side_effect=AssertionError('network')):
            result = self.check()
        self.assertEqual(result['status'], 'configured')
        self.assertEqual(self.receipt, receipt)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_cli_reads_only_retained_receipt_by_default(self):
        with patch.object(readiness, 'check_readiness', return_value={
                'status': 'configured', 'native_role_selection_proven': False}) as check, \
                patch.object(pathlib.Path, 'read_text', return_value=json.dumps(self.receipt)), \
                patch('subprocess.Popen', side_effect=AssertionError('process')), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(readiness.main(['--json']), 0)
        self.assertEqual(json.loads(output.getvalue())['status'], 'configured')
        self.assertEqual(check.call_args.args[0], ROOT)

    def test_cli_status_and_missing_receipt(self):
        receipt = self.root / 'receipt.json'
        args = ['--project-root', str(self.root), '--receipt', str(receipt), '--json']
        for content, status, code in [(None, 'pending', 1), ('{', 'invalid', 2),
                                      ('null', 'invalid', 2),
                                      (json.dumps(self.receipt), 'configured', 0)]:
            with self.subTest(status=status):
                if content is not None:
                    receipt.write_text(content, encoding='utf-8')
                result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/native_role_readiness.py'),
                                         *args], capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(json.loads(result.stdout)['status'], status)

    def test_cli_toml_temporal_model_and_effort_return_invalid_json(self):
        path = self.root / '.codex/agents/explorer.toml'
        original = path.read_text(encoding='utf-8')
        receipt = self.root / 'receipt.json'
        receipt.write_text(json.dumps(self.receipt), encoding='utf-8')
        for field, valid in [('model', 'gpt-6-luna'), ('model_reasoning_effort', 'medium')]:
            for value in ('2026-11-13', '12:34:56', '2026-11-13T12:34:56',
                          '2026-11-13T12:34:56Z'):
                with self.subTest(field=field, value=value):
                    self.edit_role(original.replace(f'{field} = "{valid}"', f'{field} = {value}'))
                    result = subprocess.run([
                        sys.executable, '-B', str(ROOT / 'scripts/native_role_readiness.py'),
                        '--project-root', str(self.root), '--receipt', str(receipt), '--json'],
                        capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    output = json.loads(result.stdout)
                    self.assertEqual(output['status'], 'invalid')
                    self.assertIn('explorer: required fields must be nonempty strings', output['errors'])
                    self.assertIsNone(output['roles']['explorer'][field])
                    self.assertFalse(output['native_role_selection_proven'])
                    self.assertEqual(result.stderr, '')


class ProbeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = pathlib.Path(temp.name).resolve()
        self.harness = self.base / 'harness'
        self.script = self.harness / 'scripts/native_config_probe.py'
        self.script.parent.mkdir(parents=True)
        self.receipt = self.base / 'evidence/native-config.json'

    def test_other_root_requires_output_before_success_or_failure_rpc(self):
        with tempfile.TemporaryDirectory() as directory:
            base = pathlib.Path(directory).resolve()
            harness = base / 'harness'
            target = base / 'target'
            target.mkdir()
            (base / 'evidence').mkdir()
            receipt = base / 'evidence/native-config.json'
            receipt.write_bytes(b'preserved receipt')
            for failed in (False, True):
                with self.subTest(failed=failed):
                    self.assert_destination_rejected(harness, target, [], failed)
                    self.assertEqual(receipt.read_bytes(), b'preserved receipt')

    def assert_destination_rejected(self, harness, target, options, failed):
        process = Mock()
        responses = ([{'id': 1, 'error': {'message': 'failed'}}] if failed else [
            {'id': 1, 'result': {}},
            {'id': 2, 'result': {'config': {}, 'layers': []}},
            {'id': 3, 'result': {'data': []}}])
        process.stdout = io.StringIO('\n'.join(json.dumps(r) for r in responses))
        with patch.object(probe, '__file__', str(harness / 'scripts/native_config_probe.py')), \
                patch.object(probe.subprocess, 'Popen', return_value=process) as launch, \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            try:
                code = probe.main(['approved-local-executable', '--project-root', str(target), *options])
            except SystemExit as error:
                code = error.code
        self.assertEqual(code, 2)
        launch.assert_not_called()

    def test_protected_outputs_and_aliases_rejected_before_success_or_failure_rpc(self):
        with tempfile.TemporaryDirectory() as directory:
            base = pathlib.Path(directory).resolve()
            harness, target = base / 'harness', base / 'target'
            protected = []
            for root in (harness, target):
                for name in ('.codex/config.toml', '.codex/agents/explorer.toml',
                             'scripts/probe.py', 'tests/test_probe.py', 'README.md'):
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(b'preserved source/config')
                    protected.append(path)
            (base / 'evidence').mkdir()
            receipt = base / 'evidence/native-config.json'
            receipt.write_bytes(b'preserved harness receipt')
            protected.append(receipt)
            config_alias = target / 'config-alias.json'
            config_alias.hardlink_to(target / '.codex/config.toml')
            receipt_alias = target / 'receipt-alias.json'
            receipt_alias.hardlink_to(receipt)
            before = {p: p.read_bytes() for p in protected}
            outputs = [*protected, config_alias, receipt_alias,
                       target / 'scripts/../.codex/config.toml',
                       target / '.codex/new-config.json']
            for output in outputs:
                for failed in (False, True):
                    with self.subTest(output=output, failed=failed):
                        self.assert_destination_rejected(
                            harness, target, ['--output', str(output)], failed)
                        self.assertEqual(before, {p: p.read_bytes() for p in protected})

    def test_failed_rpc_does_not_replace_legacy_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            base = pathlib.Path(directory).resolve()
            (base / 'evidence').mkdir()
            receipt = base / 'evidence/native-config.json'
            receipt.write_bytes(b'preserved legacy receipt')
            process = Mock()
            process.stdout = io.StringIO(json.dumps({'id': 1, 'error': {'message': 'failed'}}))
            with patch.object(probe, '__file__', str(base / 'harness/scripts/native_config_probe.py')), \
                    patch.object(probe.subprocess, 'Popen', return_value=process), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(probe.main(['approved-local-executable']), 2)
            self.assertEqual(receipt.read_bytes(), b'preserved legacy receipt')

    def test_legacy_receipt_hardlink_is_rejected_before_rpc(self):
        with tempfile.TemporaryDirectory() as directory:
            base = pathlib.Path(directory).resolve()
            harness = base / 'harness'
            config = harness / '.codex/config.toml'
            config.parent.mkdir(parents=True)
            config.write_bytes(b'preserved config')
            (base / 'evidence').mkdir()
            receipt = base / 'evidence/native-config.json'
            receipt.hardlink_to(config)
            for failed in (False, True):
                with self.subTest(failed=failed):
                    self.assert_destination_rejected(harness, harness, [], failed)
                    self.assertEqual(config.read_bytes(), b'preserved config')

    def test_failed_rpc_does_not_create_target_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            base = pathlib.Path(directory).resolve()
            destination = base / 'target-receipt.json'
            process = Mock()
            process.stdout = io.StringIO(json.dumps({'id': 1, 'error': {'message': 'failed'}}))
            with patch.object(probe, '__file__', str(base / 'harness/scripts/native_config_probe.py')), \
                    patch.object(probe.subprocess, 'Popen', return_value=process), \
                    contextlib.redirect_stdout(io.StringIO()) as output:
                code = probe.main(['approved-local-executable', '--project-root', str(base),
                                   '--output', str(destination)])
            self.assertEqual(code, 2)
            self.assertIn('protocol_error', json.loads(output.getvalue()))
            self.assertFalse(destination.exists())

    def test_legacy_directory_alias_rejected_before_rpc(self):
        unrelated = self.base / 'unrelated'
        unrelated.mkdir()
        original = unrelated / self.receipt.name
        original.write_bytes(b'unrelated regular file')
        if sys.platform == 'win32':
            import _winapi
            _winapi.CreateJunction(str(unrelated), str(self.receipt.parent))
        else:
            self.receipt.parent.symlink_to(unrelated, target_is_directory=True)
        self.assert_destination_rejected(self.harness, self.harness, [], False)
        self.assertEqual(original.read_bytes(), b'unrelated regular file')

    def test_legacy_leaf_swap_after_check_preserves_protected_file(self):
        self.receipt.parent.mkdir()
        self.receipt.write_bytes(b'previous receipt')
        protected = self.harness / 'fixture.toml'
        protected.write_bytes(b'protected fixture')
        dumps = json.dumps
        swapped = False

        def swap_on_serialization(value, **kwargs):
            nonlocal swapped
            if not swapped and isinstance(value, dict) and value.get('initialize_ok'):
                self.receipt.unlink()
                self.receipt.hardlink_to(protected)
                swapped = True
            return dumps(value, **kwargs)

        with patch.object(probe.json, 'dumps', side_effect=swap_on_serialization):
            code, output, _, _ = self.run_probe([
                {'id': 1, 'result': {}},
                {'id': 2, 'result': {'config': {}, 'layers': []}},
                {'id': 3, 'result': {'data': []}}])
        self.assertTrue(swapped)
        self.assertEqual(protected.read_bytes(), b'protected fixture')
        self.assertEqual(code, 0)
        self.assertFalse(self.receipt.samefile(protected))
        self.assertEqual(json.loads(self.receipt.read_text(encoding='utf-8')), json.loads(output))

    def test_output_created_during_rpc_is_preserved_with_nonzero_status(self):
        for legacy in (False, True):
            with self.subTest(legacy=legacy), tempfile.TemporaryDirectory() as directory:
                self.check_output_alias_created_during_rpc(pathlib.Path(directory).resolve(), legacy)

    def check_output_alias_created_during_rpc(self, base, legacy):
        destination = base / ('evidence/native-config.json' if legacy else 'receipt.json')
        destination.parent.mkdir(parents=True, exist_ok=True)
        config = base / 'fixture-config.toml'
        config.write_bytes(b'concurrent protected file')
        process = Mock()
        process.stdout = io.StringIO('\n'.join(json.dumps(r) for r in [
            {'id': 1, 'result': {}},
            {'id': 2, 'result': {'config': {}, 'layers': []}},
            {'id': 3, 'result': {'data': []}}]))

        def launch(*args, **kwargs):
            destination.hardlink_to(config)
            return process

        options = [] if legacy else ['--output', str(destination)]
        with patch.object(probe, '__file__', str(base / 'harness/scripts/native_config_probe.py')), \
                patch.object(probe.subprocess, 'Popen', side_effect=launch), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            code = probe.main(['approved-local-executable', *options])
        self.assertEqual(code, 2)
        self.assertIn('output_error', json.loads(output.getvalue()))
        self.assertEqual(config.read_bytes(), b'concurrent protected file')

    def test_target_workflow_binds_root_and_preserves_harness_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            base = pathlib.Path(directory).resolve()
            harness = base / 'harness'
            target = base / 'ordinary-project'
            target.mkdir()
            (base / 'evidence').mkdir()
            harness_receipt = base / 'evidence/native-config.json'
            harness_receipt.write_bytes(b'original harness receipt')
            output_path = target / 'target-receipt.json'
            process = Mock()
            process.stdout = io.StringIO('\n'.join(json.dumps(r) for r in [
                {'id': 1, 'result': {}},
                {'id': 2, 'result': {'config': {'agents': {'enabled': True}}, 'layers': [
                    {'name': {'type': 'project', 'dotCodexFolder': str(target / '.codex')},
                     'disabledReason': None}]}},
                {'id': 3, 'result': {'data': []}}]))
            with patch.object(probe, '__file__', str(harness / 'scripts/native_config_probe.py')), \
                    patch.object(sys, 'argv', ['native_config_probe.py', 'approved-local-executable',
                                              '--project-root', str(target), '--output', str(output_path)]), \
                    patch.object(probe.subprocess, 'Popen', return_value=process) as launch, \
                    contextlib.redirect_stdout(io.StringIO()) as stdout:
                code = probe.main()
            self.assertEqual(code, 0)
            self.assertEqual(launch.call_args.kwargs['cwd'], str(target))
            requests = [json.loads(call.args[0]) for call in process.stdin.write.call_args_list]
            self.assertEqual([r['method'] for r in requests],
                             ['initialize', 'initialized', 'config/read', 'model/list'])
            self.assertEqual(requests[2]['params'], {'cwd': str(target), 'includeLayers': True})
            self.assertEqual(json.loads(output_path.read_text(encoding='utf-8')),
                             json.loads(stdout.getvalue()))
            self.assertEqual(harness_receipt.read_bytes(), b'original harness receipt')

    def run_probe(self, responses, empty=False, cli=False, options=()):
        self.receipt.parent.mkdir(exist_ok=True)
        process = Mock()
        process.stdin = io.StringIO()
        process.stdout = io.StringIO('\n'.join(json.dumps(r) for r in responses))
        with patch.object(sys, 'argv', ['native_config_probe.py', 'approved-local-executable', *options]), \
                patch.object(probe.subprocess, 'Popen', return_value=process) as launch, \
                patch.object(probe, '__file__', str(self.script)), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            if cli:
                shutil.copyfile(ROOT / 'scripts/native_config_probe.py', self.script)
                with self.assertRaises(SystemExit) as exit_status:
                    runpy.run_path(str(self.script), run_name='__main__')
                code = exit_status.exception.code
            elif empty:
                with patch.object(probe.queue.Queue, 'get', side_effect=queue.Empty):
                    code = probe.main()
            else:
                try:
                    code = probe.main()
                except SystemExit as error:
                    code = error.code
        if launch.called:
            process.wait.assert_called_once_with(timeout=5)
        else:
            process.wait.assert_not_called()
        return code, output.getvalue(), self.receipt, launch

    def test_success_retains_filtered_format(self):
        code, output, receipt, launch = self.run_probe([
            {'id': 1, 'result': {}},
            {'id': 2, 'result': {'config': {'agents': {'enabled': True},
                                           'sensitive_unknown_value': 'not-output'}, 'layers': []}},
            {'id': 3, 'result': {'data': []}}])
        self.assertEqual(code, 0)
        result = json.loads(output)
        self.assertTrue(result['initialize_ok'])
        self.assertEqual(result['agents'], {'enabled': True})
        self.assertNotIn('not-output', output)
        self.assertIn('models_error', result)
        self.assertEqual(json.loads(receipt.read_text(encoding='utf-8')), result)
        self.assertEqual(launch.call_args.args[0][1:], ['app-server', '--strict-config', '--stdio'])
        self.assertEqual(launch.call_args.kwargs['cwd'], str(self.harness))

    def test_project_root_option_requires_dedicated_receipt(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stderr(io.StringIO()):
            code, _, receipt, launch = self.run_probe([], options=['--project-root', directory])
        self.assertEqual(code, 2)
        launch.assert_not_called()
        self.assertFalse(receipt.exists())

    def test_output_option_preserves_legacy_project_root_on_cli_failure(self):
        destination = self.harness / 'offline-receipt.json'
        code, _, receipt, launch = self.run_probe(
            [{'id': 1, 'error': {'message': 'failed'}}], cli=True,
            options=['--output', str(destination)])
        self.assertEqual(code, 2)
        self.assertEqual(launch.call_args.kwargs['cwd'], str(self.harness))
        self.assertFalse(destination.exists())
        self.assertFalse(receipt.exists())

    def test_each_protocol_error_returns_nonzero(self):
        baseline = [{'id': 1, 'result': {}},
                    {'id': 2, 'result': {'config': {}, 'layers': []}},
                    {'id': 3, 'result': {'data': []}}]
        for index in range(3):
            with self.subTest(index=index):
                responses = copy.deepcopy(baseline)
                responses[index] = {'id': index + 1, 'error': {'message': 'failed'}}
                code, output, _, _ = self.run_probe(responses)
                self.assertIsInstance(code, int)
                self.assertGreater(code, 0, output)

    def test_missing_result_is_not_success(self):
        code, _, _, _ = self.run_probe([{'id': 1}, {'id': 2}, {'id': 3}])
        self.assertIsInstance(code, int)
        self.assertGreater(code, 0)

    def test_malformed_protocol_result_returns_nonzero(self):
        for config, models in [({'config': []}, {'data': []}),
                               ({'config': {}, 'layers': []}, {'data': None}),
                               ({'config': {}, 'layers': [None]}, {'data': []}),
                               ({'config': {}, 'layers': []}, {'data': [None]})]:
            with self.subTest(config=config, models=models):
                code, _, _, _ = self.run_probe([
                    {'id': 1, 'result': {}}, {'id': 2, 'result': config},
                    {'id': 3, 'result': models}])
                self.assertGreater(code, 0)

    def test_cli_exits_nonzero_on_protocol_error(self):
        code, _, _, _ = self.run_probe([{'id': 1, 'error': {'message': 'failed'}}], cli=True)
        self.assertGreater(code, 0)

    def test_timeout_returns_nonzero_and_closes_child(self):
        code, output, _, _ = self.run_probe([], empty=True)
        self.assertNotEqual(code, 0)
        self.assertTrue(json.loads(output)['protocol_error'])


if __name__ == '__main__':
    unittest.main()
