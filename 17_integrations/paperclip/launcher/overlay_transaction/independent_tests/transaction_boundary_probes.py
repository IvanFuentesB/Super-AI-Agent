"""Two independent synthetic transaction probes. Never run against installed targets."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
import datetime

if len(sys.argv) != 3:
    raise SystemExit("usage: transaction_boundary_probes.py <fresh-disposable-root> <owned-evidence-dir>")
ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
if ROOT == OUT or ROOT in OUT.parents or OUT in ROOT.parents:
    raise SystemExit("fixture and evidence directories must be disjoint")
OUT.mkdir(parents=True, exist_ok=True)
FROZEN = Path(__file__).resolve().parent.parent / 'source'
CANDIDATE = '76c8c81d5a896d4955984c44e5b6fbe897fddc28'
EXPECTED = {
    'paperclip_overlay.py': '5199e7c8f9769ee95c57da83bae39b454f23c07327f5bf150e2aeb62562c578b',
    'tests/fixture.py': '511ec42939e1df80c1d09f55bb339924fd00b83dc32055c3e023348d644b1a90',
    'tests/run_with_spec.py': '7627128d432d5309bea66d94e5dbb02e3043387b80dc945b4d492cbf3aae7acf',
}

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree(root):
    root = Path(root)
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(root.rglob('*')) if p.is_file()}


report = {
    'candidate': CANDIDATE, 'scope': 'ONLY independent F1/F2 synthetic real-Git probes',
    'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'fixture_root': str(ROOT), 'source_hashes': EXPECTED, 'cases': [],
    'installed_or_built_output_compatibility_claim': False,
    'product_source_modified': False, 'source_imported_only_from_frozen_copy': True,
}


def save():
    report['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report['counts'] = {
        'executed': len(report['cases']),
        'passed': sum(c['verdict'] == 'PASS' for c in report['cases']),
        'red': sum(c['verdict'] == 'RED' for c in report['cases']),
        'errors': sum(c['verdict'] == 'ERROR' for c in report['cases']),
    }
    (OUT / 'A-probes-76c8c81.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    lines = ['# Independent F1/F2 probes — A/Darwin', '',
             f'Candidate `{CANDIDATE}`. **{report["counts"]["passed"]} PASS / {report["counts"]["red"]} RED / {report["counts"]["errors"]} ERROR**, {report["counts"]["executed"]} probes executed.', '',
             'Only small synthetic real-Git packages using the exact frozen helper/fixture/Spec entry point. No owner product files were executed or edited. No built-output or installed compatibility claim.', '',
             'Root: `' + str(ROOT) + '`. Fresh, distinct from parent itx76-independent-20261117. Sources and all residual evidence are retained; no cleanup/recovery was used to hide a RED.', '']
    for c in report['cases']:
        lines += ['## ' + c['id'] + ' — ' + c['verdict'], '', c['invariant'], '',
                  '```json', json.dumps(c, indent=2), '```', '']
    if report.get('setup_error'):
        lines += ['Setup error (not a product result):', '```text', report['setup_error'], '```']
    lines += ['Source hashes before/after:', '```json', json.dumps(report.get('source_after', EXPECTED), indent=2), '```', '',
              'Both tests require actual pre-write refusal and unchanged state. Controlled staging-only checkpoints preserve the exact unsafe boundary if reached; they do not replace verifiers or relax assertions. No service/account/database/provider or installed process action. Prior static review is preserved.', '']
    (OUT / 'A-probes-76c8c81.md').write_text('\n'.join(lines), encoding='utf-8')


def snap(f):
    return {'target': f.snapshot(), 'index_raw': digest(f.target / '.git/index'),
            'package': tree(f.package)}


def changed(a, b):
    return [k for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]


def run_case(name, fn, invariant):
    case = {'id': name, 'invariant': invariant}
    try:
        passed, details = fn()
        case.update(details)
        case['verdict'] = 'PASS' if passed is True else 'RED'
    except Exception:
        case.update(verdict='ERROR', error=traceback.format_exc())
    report['cases'].append(case)
    save()
    print(json.dumps({'case': name, 'verdict': case['verdict']}), flush=True)


try:
    assert not ROOT.exists(), 'Fresh root already exists; refuse reuse'
    ROOT.mkdir()
    for rel, expected in EXPECTED.items():
        assert digest(FROZEN / rel) == expected, 'Frozen source identity mismatch: ' + rel
    for k in list(os.environ):
        if k.upper().startswith('GIT_'):
            del os.environ[k]
    for name in ('home', 'tmp', 'fixtures'):
        (ROOT / name).mkdir()
    os.environ.update(HOME=str(ROOT / 'home'), USERPROFILE=str(ROOT / 'home'),
                      TEMP=str(ROOT / 'tmp'), TMP=str(ROOT / 'tmp'),
                      OVERLAY_FIXTURE_ROOT=str(ROOT / 'fixtures'),
                      PATH=os.environ.get('PATH', ''))
    sys.path.insert(0, str(FROZEN / 'tests'))
    from fixture import Fixture, clean_env

    def validated(name):
        f = Fixture(name)
        assert f.root.resolve().is_relative_to(ROOT.resolve())
        assert (f.target / '.git').is_dir() and not (f.target / '.git').is_symlink()
        code, result, err = f.run('preflight')
        assert (code, result.get('status')) == (0, 'READY'), (code, result, err)
        return f, {'exit': code, 'result': result, 'stderr': err,
                   'git_dir_is_fixture_directory': True}

    def f1():
        f, setup = validated('F1')
        x = f.txn('F1-transaction')
        code, result, err = f.run('apply', x)
        assert (code, result.get('status')) == (0, 'APPLIED'), (code, result, err)
        stopped, result, err = f.run('rollback', x,
                                    env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT='rollback:begun'))
        assert stopped == 75, (stopped, result, err)
        phase = json.loads((x / 'journal.json').read_text())['phase']
        assert phase == 'rollback-begun'
        assert not (x / 'rb-out/ui/dist').exists()
        # Independently model an unowned deletion after intent, with no helper move evidence.
        moved = f.root / 'owner-moved-ui'
        (f.target / 'ui/dist').rename(moved)
        before = snap(f)
        journal_before = digest(x / 'journal.json')
        moved_before = tree(moved)
        code, result, err = f.run('recover', x)
        after = snap(f)
        details = {
            'fixture': str(f.root), 'preflight': setup,
            'rollback_pause_exit': stopped, 'journal_phase_before': phase,
            'rb_out_ui_present_before': False,
            'recover': {'exit': code, 'result': result, 'stderr': err},
            'snapshot_changed_fields': changed(before, after),
            'journal_unchanged': journal_before == digest(x / 'journal.json'),
            'later_owner_moved_tree_unchanged': moved_before == tree(moved),
            'ui_dist_present_after': (f.target / 'ui/dist').exists(),
            'before': before, 'after': after,
        }
        passed = (code in (2, 3) and result.get('status') in ('REJECTED', 'INCONSISTENT')
                  and after == before and details['journal_unchanged']
                  and details['later_owner_moved_tree_unchanged'])
        return passed, details

    def f2():
        import _winapi
        f, setup = validated('F2')
        external = f.root / 'outside-sentinel'
        external.mkdir()
        (external / 'sentinel.txt').write_text('owned external sentinel; must not change\n')
        refspace = external / 'refspace'
        refspace.mkdir()
        alias = f.target / '.git/refs/paperclip-overlay'
        assert not alias.exists()
        assert alias.parent.resolve().is_relative_to(f.root.resolve())
        assert refspace.resolve().is_relative_to(ROOT.resolve())
        _winapi.CreateJunction(str(refspace), str(alias))
        assert alias.lstat().st_file_attributes & 0x400
        assert os.path.normcase(os.path.realpath(alias)) == os.path.normcase(str(refspace.resolve()))
        before = snap(f)
        external_before = tree(external)
        x = f.txn('F2-transaction')
        # If the operation does not refuse, stop immediately after fetch to expose the real external ref.
        code, result, err = f.run('apply', x,
                                 env=clean_env(PAPERCLIP_OVERLAY_TEST_STOP_AT='apply:fetched'))
        after = snap(f)
        external_after = tree(external)
        details = {
            'fixture': str(f.root), 'preflight': setup,
            'owned_junction': str(alias), 'owned_external': str(external),
            'operation': {'exit': code, 'result': result, 'stderr': err},
            'txn_created': x.exists(),
            'snapshot_changed_fields': changed(before, after),
            'external_before': external_before, 'external_after': external_after,
            'external_changed_paths': changed(external_before, external_after),
            'journal_phase_after': json.loads((x / 'journal.json').read_text())['phase'] if (x / 'journal.json').is_file() else None,
            'refspace_files_after': [p.name for p in refspace.iterdir()],
            'before': before, 'after': after,
        }
        passed = (code in (2, 3) and result.get('status') in ('REJECTED', 'INCONSISTENT')
                  and after == before and external_after == external_before and not x.exists())
        return passed, details

    run_case('F1-unowned-missing-output-after-rollback-intent', f1,
             'Recover must refuse an unowned missing ui/dist before changing target, Git identity, journal or later owner work.')
    run_case('F2-internal-ref-junction-ownership', f2,
             'Apply must refuse an internal ref-namespace junction before writes, with no target/transaction or external mutation.')
except Exception:
    report['setup_error'] = traceback.format_exc()
finally:
    report['source_after'] = {p: digest(FROZEN / p) for p in EXPECTED}
    report['frozen_sources_unchanged'] = report['source_after'] == EXPECTED
    save()

print(json.dumps(report['counts']), flush=True)
sys.exit(1 if report.get('setup_error') or any(c['verdict'] != 'PASS' for c in report['cases']) else 0)
