"""Exercise the real installation gate with real Git and reviewed process helpers.

Only SOURCE/STATE/NATIVE locations are rebound to the disposable installation;
the gate, Git isolation, source revision, artifact pins and helper code are real.
No worker, server, DB, dotenv or account is opened.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location('artifact_host', Path(__file__).parents[1] / 'paperclip_host.py')
host = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(host)
NATIVE = Path.home() / 'AppData/Local/Ghoti/engineering/ghoti_operator_integration/.worktrees/t_4d9627ef'
GIT = r'C:/Program Files/Git/cmd/git.exe'
EXPECTED = {
    'server/src/adapters/utils.ts': '46e22ffde9f24ab90d094a0ffdba2c352b547dba1f40ef45cc68d9b9f279bf1c',
    'packages/adapter-utils/src/service-declarations.test.ts': '844395e3bc274c725c0d9eb5f32f20f9fae31dbcf2b84e0f8ec2a9064cbcc0e1',
}


class ActualInstallationPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='paperclip-artifact-preflight-')
        cls.root = Path(cls.temp.name)
        cls.source = cls.root / 'installation'
        cls.original = host.SOURCE
        cls.env = {k: v for k, v in os.environ.items() if not k.upper().startswith('GIT_')}
        cls.env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_OPTIONAL_LOCKS='0')
        cls.git('clone', '--local', '--no-hardlinks', '--no-checkout', str(cls.original), str(cls.source), cwd=cls.root)
        cls.git('-c', 'core.autocrlf=false', '-c', 'core.hooksPath=' + str(cls.root / 'no-hooks'),
                'checkout', '--detach', host.SOURCE_REVISION)
        cls.approved = {}
        for rel, expected in EXPECTED.items():
            raw = cls.git('cat-file', 'blob', host.SOURCE_REVISION + ':' + rel).stdout
            if rel.startswith('server/'):
                # Fixture construction only; installed bytes are never normalized by the gate.
                raw = raw.replace(b'\n', b'\r\n')
            assert hashlib.sha256(raw).hexdigest() == expected
            cls.approved[rel] = raw
        for rel in ('cli/node_modules/tsx/dist/cli.mjs', 'packages/shared/dist/index.js',
                    'packages/plugins/sdk/dist/index.js', 'server/dist/index.js',
                    'ui/dist/index.html', 'cli/dist/index.js'):
            target = cls.source / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(cls.original / rel, target)
        cls.bindings = mock.patch.multiple(host, SOURCE=cls.source, STATE=cls.root / 'state', NATIVE=NATIVE)
        cls.bindings.start()

    @classmethod
    def tearDownClass(cls):
        cls.bindings.stop()
        assert cls.source.is_relative_to(cls.root) and cls.root.name.startswith('paperclip-artifact-preflight-')
        cls.temp.cleanup()

    @classmethod
    def git(cls, *args, cwd=None):
        return subprocess.run([GIT, '-c', 'core.fsmonitor=false', '-c', 'core.untrackedCache=false',
                               '-C', str(cwd or cls.source), *args], env=cls.env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45, check=True)

    def setUp(self):
        for rel, raw in self.approved.items():
            (self.source / rel).write_bytes(raw)

    def test_actual_reported_failure_still_rejects_bad_installed_test(self):
        rel = 'packages/adapter-utils/src/service-declarations.test.ts'
        bad = self.approved[rel].replace(b'\n', b'\r\n')
        self.assertEqual(hashlib.sha256(bad).hexdigest(), '272491d47384e9722dd3ba27addcd9fdc8fbb0ffba018bcfcd35a271dc617a56')
        (self.source / rel).write_bytes(bad)
        with self.assertRaises(PermissionError):
            host.installation_check()

    def test_approved_mixed_representation_passes_actual_gate(self):
        self.assertEqual(host.installation_check(), host.SOURCE_REVISION)

    def test_old_representation_only_gate_false_rejects_approved_bytes(self):
        result = host.load_helpers().inspect_git(self.source, 'diff', '--no-ext-diff', '--no-textconv', '--quiet', 'HEAD', '--')
        self.assertEqual(result['exit_code'], 1)
        self.assertFalse(result['timed_out'] or result['output_overflow'])

    def test_each_newline_only_mutation_is_refused(self):
        for rel, raw in self.approved.items():
            mutated = raw.replace(b'\r\n', b'\n') if b'\r\n' in raw else raw.replace(b'\n', b'\r\n')
            with self.subTest(path=rel):
                (self.source / rel).write_bytes(mutated)
                with self.assertRaises(PermissionError):
                    host.installation_check()
                (self.source / rel).write_bytes(raw)

    def test_same_size_content_mutation_is_refused(self):
        for rel, raw in self.approved.items():
            with self.subTest(path=rel):
                (self.source / rel).write_bytes(b'!' + raw[1:])
                with self.assertRaises(PermissionError):
                    host.installation_check()
                (self.source / rel).write_bytes(raw)

    def test_wrong_source_revision_is_refused(self):
        with mock.patch.object(host, 'SOURCE_REVISION', '0' * 40), self.assertRaises(ValueError):
            host.installation_check()

    def test_wrong_git_artifact_binding_is_refused(self):
        altered = dict(host.DEPLOYED_SOURCE_FILES)
        rel = next(iter(altered))
        _, raw, size = altered[rel]
        altered[rel] = ('0' * 40, raw, size)
        with mock.patch.object(host, 'DEPLOYED_SOURCE_FILES', altered), self.assertRaises(PermissionError):
            host.installation_check()

    def test_unrelated_tracked_modification_still_refused(self):
        target = self.source / 'package.json'
        before = target.read_bytes()
        try:
            target.write_bytes(before + b'\n')
            with self.assertRaises(PermissionError):
                host.installation_check()
        finally:
            target.write_bytes(before)

    def test_inherited_override_fails_before_git_or_source_reads(self):
        with mock.patch.dict(host.os.environ, {'GIT_CONFIG_COUNT': '0'}), mock.patch.object(host, 'load_helpers') as helpers:
            with self.assertRaises(PermissionError):
                host.installation_check()
            helpers.assert_not_called()

    def test_gate_is_read_only_and_idempotent(self):
        paths = [self.source / rel for rel in self.approved]
        before = [(p.read_bytes(), p.stat().st_mtime_ns) for p in paths]
        self.assertEqual(host.installation_check(), host.SOURCE_REVISION)
        self.assertEqual(host.installation_check(), host.SOURCE_REVISION)
        self.assertEqual(before, [(p.read_bytes(), p.stat().st_mtime_ns) for p in paths])
        self.assertFalse((self.root / 'state').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
