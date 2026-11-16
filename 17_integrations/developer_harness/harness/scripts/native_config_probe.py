"""Read-only native Codex protocol check; no model turn or config writes."""
import argparse
import json
import os
import pathlib
import queue
import subprocess
import tempfile
import threading
import time


def main(argv=None):
    harness_root = pathlib.Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('executable', help='Installed native executable')
    parser.add_argument('--project-root', type=pathlib.Path,
                        default=harness_root,
                        help='Project to read (default: harness root)')
    parser.add_argument('--output', type=pathlib.Path,
                        help='Unused JSON receipt file, required for another root; parent must exist')
    args = parser.parse_args(argv)
    project_root = args.project_root.resolve()
    cwd = str(project_root)
    legacy_output = harness_root.parent / 'evidence/native-config.json'
    if project_root != harness_root and args.output is None:
        parser.error('Another project root requires a dedicated --output')
    output = args.output or legacy_output
    try:
        # Explicit output never replaces an existing file, including hardlink aliases.
        if (output.is_symlink() or (output.exists() and
                (args.output is not None or output.stat().st_nlink > 1))):
            raise ValueError
        if args.output is None:
            if output.parent.resolve(strict=True) != output.parent:
                raise ValueError
        else:
            output = output.resolve()
        if (output.suffix.lower() != '.json' or not output.parent.is_dir()
                or (args.output is not None and output == legacy_output.resolve())
                or any(output.is_relative_to((root / folder).resolve())
                       for root in (harness_root, project_root)
                       for folder in ('.codex', '.git', 'scripts', 'tests', 'src'))):
            raise ValueError
    except (OSError, ValueError, RuntimeError):
        parser.error('Output must be a new JSON file outside source/config folders; legacy receipt aliases are forbidden')
    proc = subprocess.Popen([args.executable, "app-server", "--strict-config", "--stdio"],
                            cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True, encoding="utf-8")
    messages = queue.Queue()

    def read():
        for line in proc.stdout:
            try:
                messages.put(json.loads(line))
            except ValueError:
                pass

    threading.Thread(target=read, daemon=True).start()
    def request(ident, method, params):
        proc.stdin.write(json.dumps(dict(id=ident, method=method, params=params)) + "\n")
        proc.stdin.flush()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            try:
                message = messages.get(timeout=max(0.01, deadline - time.monotonic()))
            except queue.Empty:
                raise TimeoutError(method) from None
            if isinstance(message, dict) and message.get("id") == ident:
                if "error" in message or not isinstance(message.get("result"), dict):
                    raise ValueError(method)
                return message
        raise TimeoutError(method)

    report = {"initialize_ok": False, "config_error": None, "models_error": None,
              "config_keys": [], "agents": None, "model": None,
              "model_reasoning_effort": None, "approval_policy": None,
              "sandbox_mode": None, "layers": [], "models": []}
    failed = False
    try:
        init = request(1, "initialize", {"clientInfo": {"name": "local-capability-probe",
                                                       "version": "1.0"},
                                          "capabilities": {"experimentalApi": True}})
        report["initialize_ok"] = True
        proc.stdin.write(json.dumps({"method": "initialized"}) + "\n")
        proc.stdin.flush()
        cfg = request(2, "config/read", {"cwd": cwd, "includeLayers": True})
        models = request(3, "model/list", {"limit": 100, "includeHidden": False})
        result = cfg.get("result", {})
        config = result.get("config", {})
        if (not isinstance(result.get("config"), dict)
                or not isinstance(result.get("layers"), list)
                or any(not isinstance(layer, dict) for layer in result["layers"])):
            raise ValueError("config/read")
        if (not isinstance(models["result"].get("data"), list)
                or any(not isinstance(model, dict) for model in models["result"]["data"])):
            raise ValueError("model/list")
        report = {"initialize_ok": "result" in init,
                  "config_error": cfg.get("error", {}).get("message"),
                  "config_keys": sorted(config),
                  "agents": config.get("agents"),
                  "model": config.get("model"),
                  "model_reasoning_effort": config.get("model_reasoning_effort"),
                  "approval_policy": config.get("approval_policy"),
                  "sandbox_mode": config.get("sandbox_mode"),
                  "layers": [{"name": layer.get("name"),
                              "disabledReason": layer.get("disabledReason")}
                             for layer in result.get("layers", [])],
                  "models": [{"id": m.get("id"), "model": m.get("model"),
                              "efforts": m.get("supportedReasoningEfforts")}
                             for m in models.get("result", {}).get("data", [])],
                  "models_error": models.get("error", {}).get("message")}
    except (ValueError, TimeoutError, OSError) as error:
        failed = True
        method = str(error) if str(error) in {"initialize", "config/read", "model/list"} else "stdio"
        report["protocol_error"] = f"Native request failed: {method}"
        if method == "config/read":
            report["config_error"] = report["protocol_error"]
        elif method == "model/list":
            report["models_error"] = report["protocol_error"]
    finally:
        proc.stdin.close()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.terminate()
            proc.wait(timeout=5)
    if not failed:
        try:
            if args.output is None:
                if (output.resolve() != output or output.is_symlink()
                        or (output.exists() and output.stat().st_nlink > 1)):
                    raise ValueError
                # Publish a closed, complete file without opening a swapped receipt entry.
                staged = tempfile.NamedTemporaryFile(dir=output.parent, mode='w',
                                                     encoding='utf-8', delete=False)
                try:
                    with staged:
                        staged.write(json.dumps(report, indent=2))
                    os.replace(staged.name, output)
                except BaseException:
                    pathlib.Path(staged.name).unlink(missing_ok=True)
                    raise
            else:
                # Exclusive creation also prevents clobber if a file appears during RPC.
                with output.open('x', encoding='utf-8') as receipt_file:
                    receipt_file.write(json.dumps(report, indent=2))
        except (OSError, ValueError, RuntimeError):
            report['output_error'] = 'Receipt output could not be written safely'
            failed = True
    print(json.dumps(report, indent=2))
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
