"""Fixed, owner-invoked Paperclip session; no ACP, permit, daemon or renewal.

Reuses the reviewed Windows Job owner. This is lifetime containment, not a
filesystem/network sandbox. Authenticated mode intentionally requires the human
operator's initial account/board claim; this launcher cannot grant that claim.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import http.client
import json
import os
import re
from pathlib import Path
import subprocess
import stat
import sys
from types import SimpleNamespace
import threading
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT.parent / 'ghoti_operator_integration/.worktrees/t_4d9627ef'
SOURCE = Path.home() / 'Documents/AI_Managed_Only/21_repos/third_party/evals/paperclip'
NODE = Path.home() / 'AppData/Local/hermes/node/node.exe'
STATE = NATIVE / 'tmp/paperclip-full-app-state'
SOURCE_REVISION = "e04e2ae1a0d47cdedf5380b5a0d94f280a82d5d1"
# Reviewed deployment bytes are not necessarily Git's LF blob representation.
# Bind BOTH identities; never normalize installed bytes to make them pass.
DEPLOYED_SOURCE_FILES = {
    'server/src/adapters/utils.ts': (
        '44e3614b027e8d4844f6036a5254ab1a73651b17',
        '46e22ffde9f24ab90d094a0ffdba2c352b547dba1f40ef45cc68d9b9f279bf1c', 3801),
    'packages/adapter-utils/src/service-declarations.test.ts': (
        '1304a570ff8ae5f3921551a998ac191b483cfad2',
        '844395e3bc274c725c0d9eb5f32f20f9fae31dbcf2b84e0f8ec2a9064cbcc0e1', 4757),
}
HELPER_HASHES = {
    'ghoti_external_tasks/process.py': '692ccc766a9f32e71a9c3f86ec6d650e17d789de94c2bada7fb2f17954b45d23',
    'ghoti_external_tasks/common.py': 'c0814fbdb93f7b581d4cf5854a138c569832a033fe0d82d82c7951b0d37184ec',
    'ghoti_runtime/process_control.py': 'a9e1e01e75e44b9cf56b44b65c04ebf3728dbaefb56fbe72716a38cb61406955',
}
PORTS = {41401, 41402}
URL = 'http://127.0.0.1:41402'


# Only protocol literals and narrowly typed public metadata may cross this boundary.
# A field-name allowlist alone permits secrets in error/stage/ID string values.
RECEIVER_STAGES = frozenset({
    'cli_approved', 'cli_browser_open_failed', 'cli_browser_open_requested', 'cli_cancelled',
    'cli_challenge_created', 'cli_credential_revocation_failed', 'cli_credential_revoked',
    'cli_credential_stored', 'cli_expired', 'cli_failed_grant_revocation_unverified',
    'cli_failed_grant_revocation_verified', 'cli_http_failure', 'cli_http_request', 'cli_http_response',
    'cli_identity_verified', 'cli_poll_interrupted', 'company_ready', 'human_cli_approval_received',
    'human_cli_approval_required', 'human_hire_approval_received', 'human_hire_approval_required',
    'paperclip_run_created', 'real_worker_started', 'receiver_uncaught_error',
    'receiver_unhandled_rejection', 'requesting_cli_started', 'result_recorded_opened_on_board',
    'task_assigned_waiting_for_paperclip_worker', 'workflow_stopped',
})
RECEIVER_ERRORS = frozenset({
    'AbortError', 'Error', 'SyntaxError', 'TimeoutError', 'TypeError', 'adapter_invocation_not_unique',
    'agent_configuration_readback_failed', 'agent_not_idle', 'agent_policy_readback_failed',
    'ambiguous_matching_agents', 'ambiguous_matching_companies', 'ambiguous_matching_tasks',
    'api_scope_invalid', 'application_request_failed', 'assignment_readback_failed', 'blocked',
    'board_result_readback_failed', 'cli_cancelled', 'cli_expired', 'cli_identity_unverified',
    'cli_revocation_readback_failed', 'company_readback_failed', 'credential_in_output',
    'credential_scope_decision_required', 'existing_agent_needs_reconciliation',
    'existing_agent_running', 'existing_credential_needs_reconciliation',
    'existing_hire_needs_reconciliation', 'existing_runs_need_reconciliation',
    'existing_task_needs_reconciliation', 'hire_approval_budget_exhausted', 'hire_not_approved',
    'insufficient_full_pairing_window', 'insufficient_setup_budget', 'insufficient_worker_budget',
    'invalid_host_deadline', 'invalid_review_output', 'invalid_run_events', 'lease_work_deadline',
    'model_changed', 'native_codex_missing', 'paperclip_did_not_start_run', 'public_page_scope_invalid',
    'readonly_sandbox_required', 'real_worker_failed', 'reasoning_changed', 'receiver_error',
    'scope_changed', 'service_not_ready', 'unexpected_additional_run', 'unexpected_agent_list',
    'unexpected_company_list', 'unexpected_issue_list', 'unexpected_run_count', 'unexpected_run_list',
    'unsafe_argv', 'worker_deadline', 'worker_output_missing', 'worker_used_out_of_scope_tools',
})
RECEIVER_UUID_FIELDS = frozenset({'requestId', 'challengeId', 'run_id', 'task_id', 'company_id', 'approval_id'})
RECEIVER_FIXED_TEXT = {'agent_name': 'Ghoti Reviewer', 'button': 'Approve CLI access', 'client': 'Ghoti attended first task'}


def safe_receiver_event(event):
    if not isinstance(event, dict) or not isinstance(event.get('stage'), str) or event['stage'] not in RECEIVER_STAGES:
        return None
    safe = {'stage': event['stage']}
    for key, value in event.items():
        if key in {'at', 'expiresAt', 'started_at'} and isinstance(value, str):
            if re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})', value):
                safe[key] = value
        elif key in RECEIVER_UUID_FIELDS and isinstance(value, str):
            if re.fullmatch(r'[a-fA-F0-9]{8}(?:-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}', value):
                safe[key] = value
        elif key == 'remaining_seconds' and type(value) in (int, float) and 0 <= value <= 1200:
            safe[key] = value
        elif key == 'status' and (value is None or type(value) is int and 0 <= value <= 599
                or isinstance(value, str) and value in {'queued', 'running', 'succeeded', 'failed', 'cancelled', 'timed_out', 'done', 'blocked', 'pending', 'approved', 'denied', 'expired'}):
            safe[key] = value
        elif key in {'error', 'code'}:
            safe[key] = value if isinstance(value, str) and value in RECEIVER_ERRORS else 'receiver_error'
        elif key == 'identifier' and isinstance(value, str) and re.fullmatch(r'[A-Z][A-Z0-9]{0,9}-[0-9]{1,8}', value):
            safe[key] = value
        elif key in RECEIVER_FIXED_TEXT and value == RECEIVER_FIXED_TEXT[key]:
            safe[key] = value
    return safe


def path_entry(path):
    try:
        entry = path.lstat()
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(entry.st_mode) or getattr(entry, 'st_file_attributes', 0) & 0x400:
        raise PermissionError('link/reparse directory entry refused, including dangling links')
    return entry


def reject_links(path):
    for component in (*reversed(path.parents), path):
        path_entry(component)


def reject_git_overrides(inherited):
    # Preserve the terminal's display-only pager setting. The reviewed Git helper
    # supplies its own subprocess environment and never inherits that pager.
    if any(key.upper().startswith('GIT_') and key.upper() != 'GIT_PAGER' for key in inherited):
        raise PermissionError('inherited Git override refused before inspection; do not clear or retry')


def load_helpers():
    for relative, expected in HELPER_HASHES.items():
        path = NATIVE / '03_scripts' / relative
        reject_links(path)
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise PermissionError('reviewed process helper changed')
    module_root = str(NATIVE / '03_scripts')
    if module_root not in sys.path:
        sys.path.insert(0, module_root)
    from ghoti_external_tasks.process import OwnedProcess
    from ghoti_external_tasks.common import run_process, inspect_git
    from ghoti_runtime.process_control import InstanceLock
    return SimpleNamespace(OwnedProcess=OwnedProcess, run_process=run_process,
                           inspect_git=inspect_git, InstanceLock=InstanceLock)


def validate_lease(seconds):
    if type(seconds) is not int or not 1 <= seconds <= 1200:
        raise ValueError('one explicit session must be between 1 and 1200 seconds; no renewal')
    return seconds


def configuration(state):
    state = state.resolve()
    return {
        '$meta': {'version': 1, 'updatedAt': datetime.now(timezone.utc).isoformat(), 'source': 'configure'},
        'database': {'mode': 'embedded-postgres', 'embeddedPostgresDataDir': str(state / 'db'),
                     'embeddedPostgresPort': 41401, 'backup': {'enabled': False, 'intervalMinutes': 60,
                     'retentionDays': 7, 'dir': str(state / 'backups')}},
        'logging': {'mode': 'file', 'logDir': str(state / 'logs')},
        'server': {'deploymentMode': 'authenticated', 'exposure': 'private', 'bind': 'loopback',
                   'host': '127.0.0.1', 'port': 41402, 'allowedHostnames': ['127.0.0.1', 'localhost'],
                   'serveUi': True},
        'telemetry': {'enabled': False},
        'auth': {'baseUrlMode': 'explicit', 'publicBaseUrl': URL, 'disableSignUp': False},
        'storage': {'provider': 'local_disk', 'localDisk': {'baseDir': str(state / 'storage')}},
        'secrets': {'provider': 'local_encrypted', 'strictMode': True,
                    'localEncrypted': {'keyFilePath': str(state / 'secrets/master.key')}}}


def ensure_configuration(state):
    reject_links(state / 'config.json')
    expected = configuration(state)
    state.mkdir(parents=True, exist_ok=True)
    target = state / 'config.json'
    if target.exists():
        prior = json.loads(target.read_text(encoding='utf-8'))
        timestamp = prior.get('$meta', {}).get('updatedAt')
        if not isinstance(timestamp, str):
            raise ValueError('existing task configuration lacks creation metadata')
        expected['$meta']['updatedAt'] = timestamp
        if prior != expected:
            raise ValueError('existing task configuration changed; refusing to overwrite it')
    else:
        with target.open('x', encoding='utf-8') as handle:
            json.dump(expected, handle, indent=2)
            handle.write('\n')
    return target


def environment(state, inherited):
    reject_git_overrides(inherited)
    forbidden = {'NODE_OPTIONS', 'NODE_PATH', 'DATABASE_URL', 'DATABASE_MIGRATION_URL',
                 'OPENAI_API_KEY', 'CODEX_API_KEY', 'ANTHROPIC_API_KEY', 'OPENAI_BASE_URL',
                 'CODEX_HOME', 'CODEX_CONFIG_FILE', 'CODEX_MANAGED_CONFIG', 'HOST', 'PORT',
                 'BETTER_AUTH_SECRET', 'BETTER_AUTH_URL', 'BETTER_AUTH_BASE_URL',
                 'HEARTBEAT_SCHEDULER_ENABLED'}
    if any(k.upper() in forbidden or k.upper().startswith('PAPERCLIP_') for k in inherited):
        raise PermissionError('inherited startup/auth override present; do not clear it or fall back')
    result = dict(inherited)
    result.update(PAPERCLIP_HOME=str(state), PAPERCLIP_CONFIG=str(state / 'config.json'),
                  PAPERCLIP_WINDOWS_PYTHON=str(Path.home() / 'AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe'),
                  PAPERCLIP_INSTANCE_ID='ghoti-t_4d9627ef', PAPERCLIP_BIND='loopback',
                  PAPERCLIP_DEPLOYMENT_MODE='authenticated', PAPERCLIP_DEPLOYMENT_EXPOSURE='private',
                  HOST='127.0.0.1', PORT='41402', HEARTBEAT_SCHEDULER_ENABLED='false',
                  PAPERCLIP_TELEMETRY_ENABLED='false', PAPERCLIP_TELEMETRY_DISABLED='1',
                  PAPERCLIP_DB_BACKUP_ENABLED='false', PAPERCLIP_UI_DEV_MIDDLEWARE='false',
                  PAPERCLIP_MIGRATION_PROMPT='never', PAPERCLIP_MIGRATION_AUTO_APPLY='false')
    result['PATH'] = str(NODE.parent) + os.pathsep + result.get('PATH', '')
    return result


def validate_listeners(rows, owned):
    for row in rows:
        if row['pid'] not in owned or row['host'] not in {'127.0.0.1', '::1'} or row['port'] not in PORTS:
            raise PermissionError('listener outside owned loopback port scope')


def validate_dotenv(path):
    reject_links(path)
    entry = path_entry(path)
    if entry is None:
        return
    if not stat.S_ISREG(entry.st_mode) or entry.st_size > 2048:
        raise PermissionError('unsafe task dotenv file')
    entries = [line.strip() for line in path.read_text(encoding='utf-8').splitlines()
               if line.strip() and not line.lstrip().startswith('#')]
    if len(entries) != 1 or re.fullmatch(r'PAPERCLIP_AGENT_JWT_SECRET=[0-9a-f]{64}', entries[0]) is None:
        raise PermissionError('task dotenv must contain only the upstream-generated JWT secret')


def validate_readiness(record):
    if (record['health'].get('status') != 'ok' or record['health'].get('deploymentMode') != 'authenticated'
            or record['ui_status'] != 200 or record['unauthenticated_companies_status'] not in {401, 403}
            or record['invalid_bearer_status'] not in {401, 403} or record['untrusted_host_status'] != 403):
        raise PermissionError('effective service authentication/readiness contract failed')


def request(path, headers=None):
    connection = http.client.HTTPConnection('127.0.0.1', 41402, timeout=2)
    try:
        connection.request('GET', path, headers=headers or {})
        response = connection.getresponse()
        body = response.read(131072)
        return response.status, body
    finally:
        connection.close()


def installation_check():
    reject_git_overrides(os.environ)
    for root in (SOURCE, STATE, *(STATE / name for name in (
            'config.json', '.env', 'host.lock', 'db', 'logs', 'storage', 'secrets', 'sessions'))):
        reject_links(root)
    if path_entry(SOURCE / '.env') is not None:
        raise PermissionError('unreviewed upstream-root dotenv exists; no startup or automatic deletion')
    needed = [NODE, SOURCE / 'cli/node_modules/tsx/dist/cli.mjs',
              SOURCE / 'packages/shared/dist/index.js', SOURCE / 'packages/plugins/sdk/dist/index.js',
              SOURCE / 'server/dist/index.js', SOURCE / 'ui/dist/index.html', SOURCE / 'cli/dist/index.js']
    if not all(p.is_file() for p in needed):
        raise FileNotFoundError('full Paperclip build is incomplete: ' + ', '.join(str(p) for p in needed if not p.is_file()))
    helpers = load_helpers()
    def git(*args):
        result = helpers.inspect_git(SOURCE, *args)
        if result['exit_code'] != 0 or result['timed_out'] or result['output_overflow']:
            raise PermissionError('bounded source inspection failed; no start')
        return result['stdout'].strip()
    revision = git('rev-parse', 'HEAD')
    if revision != SOURCE_REVISION:
        raise ValueError('official source revision changed; review the new pin before starting')
    if Path(git('rev-parse', '--show-toplevel')).resolve() != SOURCE.resolve():
        raise PermissionError('Git resolved a different repository')
    for relative, (blob_oid, raw_sha256, raw_size) in DEPLOYED_SOURCE_FILES.items():
        path = SOURCE / relative
        reject_links(path)
        entry = path_entry(path)
        if entry is None or not stat.S_ISREG(entry.st_mode) or entry.st_size != raw_size:
            raise PermissionError('reviewed deployment artifact size/type changed; no start')
        if git('rev-parse', 'HEAD:' + relative) != blob_oid:
            raise PermissionError('reviewed deployment artifact source binding changed; no start')
        if hashlib.sha256(path.read_bytes()).hexdigest() != raw_sha256:
            raise PermissionError('reviewed deployment artifact bytes changed; no start')
    # Only the two explicitly source-bound, exact-byte artifacts are excluded.
    git('diff', '--no-ext-diff', '--no-textconv', '--quiet', 'HEAD', '--', '.',
        *(':(exclude)' + relative for relative in DEPLOYED_SOURCE_FILES))
    return revision


def run(seconds, *, receiver_factory=None):
    import psutil
    validate_lease(seconds)
    env = environment(STATE, os.environ)
    revision = installation_check()
    helpers = load_helpers()

    with helpers.InstanceLock(STATE / 'host.lock'):
        if any(c.status == 'LISTEN' and c.laddr.port in PORTS for c in psutil.net_connections(kind='tcp')):
            raise RuntimeError('configured ports are occupied; no reuse or fallback allowed')
        config = ensure_configuration(STATE)
        validate_dotenv(STATE / '.env')
        loader = SOURCE / 'cli/node_modules/tsx/dist/cli.mjs'
        # The project's own generator handles its own runtime JWT; never expose it.
        module_url = (SOURCE / 'cli/src/config/env.ts').as_uri()
        setup = helpers.run_process([str(NODE), str(loader), '--eval',
                             f'import {{ ensureAgentJwtSecret }} from {json.dumps(module_url)}; '
                             'ensureAgentJwtSecret(process.argv[1]);', str(config)],
                            cwd=SOURCE, env=env, timeout=25, output_limit=4096)
        if setup['exit_code'] != 0:
            raise RuntimeError('upstream JWT setup failed; no service started: ' + setup['stderr'][:1500])
        validate_dotenv(STATE / '.env')
        run_dir = STATE / 'sessions' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex[:8])
        run_dir.mkdir(parents=True, exist_ok=False)
        record = {'schema': 'ghoti_paperclip_host/1', 'task_id': 't_4d9627ef', 'source_revision': revision,
                  'lease_seconds': seconds, 'health': None, 'ready': False, 'reason': 'starting',
                  'auth_mode': 'authenticated', 'url': URL, 'acp_requested': False,
                  'auto_renewal': False, 'scheduler_enabled': False, 'processes': [], 'listeners': []}
        def save():
            (run_dir / 'receipt.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
        save()
        argv = [str(NODE), str(loader), str(SOURCE / 'cli/src/index.ts'), 'run',
                '--config', str(config), '--data-dir', str(STATE), '--no-repair']
        started = time.monotonic()
        started_utc = datetime.now(timezone.utc)
        deadline = started + seconds
        record.update(started_utc=started_utc.isoformat(),
                      deadline_utc=(started_utc + timedelta(seconds=seconds)).isoformat())
        child = helpers.OwnedProcess(argv, cwd=SOURCE, env=env)
        receiver = None
        receiver_finished = False
        record['pid'] = child.p.pid
        known = {}
        guard = threading.Lock()
        stopped = False
        def stop():
            nonlocal stopped
            with guard:
                if not stopped:
                    stopped = True
                    try:
                        if receiver is not None:
                            receiver.stop()
                    finally:
                        child.stop()
        expired = threading.Event()
        def expire():
            expired.set()
            stop()
        timer = threading.Timer(max(0, deadline - time.monotonic()), expire)
        timer.daemon = True
        log_failed = threading.Event()
        def drain(stream, filename):
            try:
                with (run_dir / filename).open('wb') as handle:
                    size = 0
                    while chunk := stream.read(4096):
                        size += len(chunk)
                        if size > 2 * 1024 * 1024:
                            raise OSError('log limit exceeded')
                        handle.write(chunk)
                        handle.flush()
            except Exception:
                log_failed.set()
                stop()
        def drain_receiver(stream, filename):
            try:
                with (run_dir / filename).open('w', encoding='utf-8') as handle:
                    size = 0
                    while line := stream.readline(16384):
                        size += len(line)
                        if size > 2 * 1024 * 1024:
                            raise OSError('receiver log limit exceeded')
                        try:
                            event = json.loads(line)
                        except (ValueError, UnicodeError):
                            continue
                        safe = safe_receiver_event(event)
                        if safe is not None:
                            handle.write(json.dumps(safe) + '\n')
                            handle.flush()
                            print(json.dumps(safe), flush=True)
            except Exception:
                log_failed.set()
                stop()
        pumps = [threading.Thread(target=drain, args=(stream, name), daemon=True)
                 for stream, name in [(child.p.stdout, 'stdout.log'), (child.p.stderr, 'stderr.log')]]
        try:
            timer.start()
            for pump in pumps:
                pump.start()
            save()
            print(json.dumps({'pid': child.p.pid, 'session': str(run_dir), 'lease_seconds': seconds,
                              'deadline_utc': record['deadline_utc'], 'remaining_seconds': max(0, deadline-time.monotonic())}), flush=True)
            while child.p.poll() is None and not expired.is_set() and not log_failed.is_set():
                try:
                    processes = [psutil.Process(child.p.pid), *psutil.Process(child.p.pid).children(recursive=True)]
                except psutil.NoSuchProcess:
                    break
                if receiver is not None and receiver.p.poll() is None:
                    try:
                        processes.extend([psutil.Process(receiver.p.pid), *psutil.Process(receiver.p.pid).children(recursive=True)])
                    except psutil.NoSuchProcess:
                        pass
                for process in processes:
                    try:
                        known[(process.pid, process.create_time())] = process.name()
                    except psutil.NoSuchProcess:
                        continue
                owned = {p.pid for p in processes}
                rows = [{'pid': c.pid, 'host': c.laddr.ip, 'port': c.laddr.port}
                        for c in psutil.net_connections(kind='tcp') if c.status == 'LISTEN'
                        and (c.pid in owned or c.laddr.port in PORTS)]
                validate_listeners(rows, owned)
                if not record['ready'] and {r['port'] for r in rows} == PORTS:
                    try:
                        status, body = request('/api/health')
                        health = json.loads(body)
                        if status == 200 and health.get('status') == 'ok':
                            record.update(health=health, ready_seconds=round(time.monotonic()-started,3), listeners=rows)
                            record['ui_status'] = request('/')[0]
                            record['unauthenticated_companies_status'] = request('/api/companies')[0]
                            record['invalid_bearer_status'] = request('/api/companies', {'Authorization': 'Bearer invalid-test-token'})[0]
                            record['untrusted_host_status'] = request('/api/companies', {'Host': 'untrusted.invalid'})[0]
                            validate_readiness(record)
                            record['ready'] = True
                            save()
                            print(json.dumps({'ready': True, 'url': URL, 'health': health, 'session': str(run_dir)}), flush=True)
                    except PermissionError:
                        raise
                    except (OSError, ValueError):
                        pass
                if record['ready'] and receiver_factory is not None and receiver is None:
                    # The same owner and deadline cover both subprocess trees. No tool-call lease.
                    with guard:
                        if not stopped and time.monotonic() < deadline:
                            receiver = receiver_factory(helpers, env, run_dir, record['deadline_utc'])
                            record['receiver_pid'] = receiver.p.pid
                            record['receiver_started_utc'] = datetime.now(timezone.utc).isoformat()
                            save()
                    if receiver is not None:
                        for stream, name in ((receiver.p.stdout, 'receiver.stdout.jsonl'), (receiver.p.stderr, 'receiver.stderr.jsonl')):
                            pump = threading.Thread(target=drain_receiver, args=(stream, name), daemon=True)
                            pumps.append(pump)
                            pump.start()
                        print(json.dumps({'receiver_alive': receiver.p.poll() is None, 'pid': receiver.p.pid,
                                          'deadline_utc': record['deadline_utc']}), flush=True)
                if receiver is not None and not receiver_finished and receiver.p.poll() is not None:
                    receiver_finished = True
                    record['receiver_exit_code'] = receiver.p.returncode
                    print(json.dumps({'receiver_exited': True, 'exit_code': receiver.p.returncode,
                                      'do_not_approve_stale_page': receiver.p.returncode != 0}), flush=True)
                    if receiver.p.returncode != 0:
                        record['reason'] = 'receiver_failed'
                        break
                if not record['ready'] and time.monotonic() - started > min(180, seconds):
                    record['reason'] = 'readiness_timeout'
                    break
                time.sleep(0.5)
            if expired.is_set():
                record['reason'] = 'lease_expired'
            elif record['reason'] == 'starting':
                record['reason'] = 'application_exited'
        except BaseException as exc:
            record['reason'] = 'host_exception:' + type(exc).__name__
            raise
        finally:
            stop()
            timer.cancel()
            for pump in pumps:
                if pump.ident is not None:
                    pump.join(timeout=3)
            if log_failed.is_set() or any(pump.is_alive() for pump in pumps):
                record['reason'] = 'log_failure'
            record['elapsed_seconds'] = round(time.monotonic() - started, 3)
            record['exit_code'] = child.p.returncode
            if receiver is not None:
                record['receiver_exit_code'] = receiver.p.returncode
            record['processes'] = [{'pid': pid, 'created': created, 'name': name} for (pid, created), name in known.items()]
            live = []
            for (pid, created), name in known.items():
                try:
                    if psutil.Process(pid).create_time() == created:
                        live.append(pid)
                except psutil.NoSuchProcess:
                    pass
            record['remaining_owned_pids'] = live
            record['remaining_listeners'] = [{'pid': c.pid, 'port': c.laddr.port} for c in psutil.net_connections(kind='tcp')
                                             if c.status == 'LISTEN' and c.laddr.port in PORTS]
            record['cleanup_verified'] = not live and not record['remaining_listeners']
            save()
            print(json.dumps({'ready': record['ready'], 'reason': record['reason'], 'cleanup_verified': record['cleanup_verified'],
                              'receipt': str(run_dir / 'receipt.json')}), flush=True)
        return 0 if record['ready'] and record['reason'] == 'lease_expired' and record['cleanup_verified'] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=int, default=300)
    parser.add_argument('--check', action='store_true', help='check installed build only; do not start')
    args = parser.parse_args()
    validate_lease(args.seconds)
    if args.check:
        print(json.dumps({'source_revision': installation_check(), 'build_present': True, 'service_started': False}))
        return 0
    return run(args.seconds)


if __name__ == '__main__':
    raise SystemExit(main())
