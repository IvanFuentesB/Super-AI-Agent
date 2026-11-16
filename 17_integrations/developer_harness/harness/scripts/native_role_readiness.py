"""Read retained native metadata and role files without starting a native turn."""
import argparse
import hashlib
import json
from pathlib import Path
import tomllib


ROLES = ('explorer', 'implementer', 'tester', 'reviewer', 'integrator')
FIELDS = {'name', 'description', 'model', 'model_reasoning_effort',
          'developer_instructions'}
ROOT = Path(__file__).resolve().parents[1]


def check_readiness(project_root, receipt):
    """Return snapshot readiness; only read project files, never mutate inputs."""
    root = Path(project_root).resolve()
    errors, pending, roles = [], [], {}
    config_path = root / '.codex/config.toml'
    metadata = {'project_root': str(root), 'config_path': str(config_path),
                'config_sha256': None, 'evidence': 'retained config/model snapshot'}
    try:
        raw = config_path.read_bytes()
        metadata['config_sha256'] = hashlib.sha256(raw).hexdigest()
        config = tomllib.loads(raw.decode('utf-8'))
    except FileNotFoundError:
        config = {}
        pending.append('Project config is absent')
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        config = {}
        errors.append('Project config is unreadable or malformed')

    paths = sorted((root / '.codex/agents').glob('*.toml'))
    if {p.stem for p in paths} != set(ROLES):
        errors.append('Exactly the five assigned role files are required')
    for path in paths:
        try:
            raw = path.read_bytes()
            role = tomllib.loads(raw.decode('utf-8'))
        except (OSError, UnicodeError, tomllib.TOMLDecodeError):
            errors.append(f'{path.stem}: unreadable or malformed role')
            continue
        if any(not isinstance(role.get(key), str) or not role[key].strip() for key in FIELDS):
            errors.append(f'{path.stem}: required fields must be nonempty strings')
        if role.get('name') != path.stem or path.stem not in ROLES:
            errors.append(f'{path.stem}: role name does not match an assigned role')
        # The retained role format has only these five fields; policy stays inherited.
        if set(role) - FIELDS:
            errors.append(f'{path.stem}: unsupported fields or per-role policy overrides')
        roles[path.stem] = {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest(),
                            **{key: role.get(key) if isinstance(role.get(key), str)
                               and role[key].strip() else None
                               for key in ('model', 'model_reasoning_effort')}}

    if receipt is None:
        pending.append('Native config/model receipt is absent')
    elif not isinstance(receipt, dict):
        errors.append('Native receipt must be an object')
    else:
        if (receipt.get('initialize_ok') is not True or receipt.get('config_error')
                or receipt.get('models_error') or receipt.get('protocol_error')):
            errors.append('Native config/model protocol did not succeed')
        layers = receipt.get('layers', [])
        if not isinstance(layers, list):
            errors.append('Native layers must be a list')
            layers = []
        project_enabled = False
        for layer in layers:
            if not isinstance(layer, dict) or not isinstance(layer.get('name'), dict):
                continue
            name = layer['name']
            if name.get('type') != 'project':
                continue
            folder = name.get('dotCodexFolder')
            try:
                if not isinstance(folder, str) or '\x00' in folder or not Path(folder).is_absolute():
                    raise ValueError
                project_folder = Path(folder).resolve()
            except (OSError, ValueError, RuntimeError):
                errors.append('Native project folder must be a valid absolute path')
                continue
            if project_folder == root / '.codex' and layer.get('disabledReason') is None:
                project_enabled = True
        if not project_enabled:
            pending.append('Matching native project layer is absent or disabled')
        agents = receipt.get('agents')
        if not isinstance(agents, dict) or agents.get('enabled') is not True:
            pending.append('Native agents are not enabled')
            agents = {}
        local_agents = config.get('agents', {})
        if not isinstance(local_agents, dict) or local_agents.get('enabled') is not True:
            pending.append('Project agents are not enabled in the source config')
        if not isinstance(local_agents, dict):
            local_agents = {}

        models = receipt.get('models', [])
        if not isinstance(models, list) or not models:
            errors.append('Native model catalog is absent or malformed')
            models = []

        def supported(model, effort):
            return isinstance(model, str) and isinstance(effort, str) and any(
                isinstance(item, dict) and model == item.get('model')
                and isinstance(item.get('efforts'), list)
                and any(isinstance(entry, dict) and entry.get('reasoningEffort') == effort
                        for entry in item['efforts']) for item in models)

        for name, role in roles.items():
            if not supported(role['model'], role['model_reasoning_effort']):
                errors.append(f'{name}: unsupported selected model or effort')

        def check_defaults(model, effort, label):
            if model is not None and effort is not None:
                valid = supported(model, effort)
            elif model is not None:
                valid = isinstance(model, str) and any(
                    isinstance(item, dict) and item.get('model') == model for item in models)
            elif effort is not None:
                valid = isinstance(effort, str) and any(
                    isinstance(item, dict) and supported(item.get('model'), effort) for item in models)
            else:
                valid = True
            if not valid:
                errors.append(f'Unsupported {label} model or effort')
            elif model is None or effort is None:
                pending.append(f'{label.capitalize()} model/effort pair is unresolved')

        if agents:
            check_defaults(agents.get('default_subagent_model'),
                           agents.get('default_subagent_reasoning_effort'), 'default subagent')
        for source, effective, model_key, effort_key, label in (
                (local_agents, agents, 'default_subagent_model',
                 'default_subagent_reasoning_effort', 'subagent'),
                (config, receipt, 'model', 'model_reasoning_effort', 'parent')):
            if model_key not in source and effort_key not in source:
                continue
            model = source.get(model_key, effective.get(model_key))
            effort = source.get(effort_key, effective.get(effort_key))
            check_defaults(model, effort, f'source default {label}')
        metadata['parent_default'] = {'model': receipt.get('model'),
                                      'effort': receipt.get('model_reasoning_effort')}

    return {'status': 'invalid' if errors else 'pending' if pending else 'configured',
            'native_role_selection_proven': False, 'errors': errors, 'pending': pending,
            'roles': roles, 'source': metadata}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=ROOT)
    parser.add_argument('--receipt', type=Path,
                        help='Existing filtered config/model JSON (default: sibling evidence/native-config.json)')
    parser.add_argument('--json', action='store_true', help='Print machine-readable readiness')
    args = parser.parse_args(argv)
    receipt_path = args.receipt or args.project_root.resolve().parent / 'evidence/native-config.json'
    receipt = None
    receipt_error = None
    try:
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
        if receipt is None:
            receipt_error = 'Native receipt must be an object'
    except FileNotFoundError:
        pass
    except (OSError, UnicodeError, ValueError):
        receipt_error = 'Native receipt is unreadable or malformed JSON'
    result = check_readiness(args.project_root, receipt)
    if receipt_error:
        result['status'] = 'invalid'
        result['errors'].append(receipt_error)
        result['pending'].remove('Native config/model receipt is absent')
    result['receipt_path'] = str(receipt_path.resolve())
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['status']}: native_role_selection_proven=false")
        for reason in result.get('errors', []) + result.get('pending', []):
            print(reason)
    return {'configured': 0, 'pending': 1, 'invalid': 2}[result['status']]


if __name__ == '__main__':
    raise SystemExit(main())
