#!/usr/bin/env python3
"""Local-first Hermes Agent bootstrap helper for Windows ai_sandbox.

The script can download and inspect the official installer, but it does not
blindly execute external installer code. The install path is guarded because
this milestone forbids package installation and live provider setup.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import html
import json
import platform
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = REPO_ROOT / "14_context" / "hermes_agent" / "runs"
INSTALLER_URL = "https://hermes-agent.nousresearch.com/install.sh"


def slug_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ_hermes_local_bootstrap")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def run_dir() -> Path:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    path = RUN_ROOT / slug_now()
    suffix = 2
    while path.exists():
        path = RUN_ROOT / f"{slug_now()}_{suffix}"
        suffix += 1
    path.mkdir(parents=True)
    return path


def latest_run() -> Path | None:
    if not RUN_ROOT.exists():
        return None
    runs = [path for path in RUN_ROOT.iterdir() if path.is_dir()]
    return sorted(runs, key=lambda item: item.name)[-1] if runs else None


def command_found(name: str) -> bool:
    return shutil.which(name) is not None


def git_bash_paths() -> list[str]:
    candidates = [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Users\ai_sandbox\AppData\Local\Programs\Git\bin\bash.exe",
    ]
    return [item for item in candidates if Path(item).exists()]


def is_admin() -> bool:
    if platform.system().lower() != "windows":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def safe_version(cmd: list[str], timeout: int = 6) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except Exception as exc:
        return f"unavailable: {type(exc).__name__}"
    text = (result.stdout or result.stderr or "").strip().splitlines()
    return text[0][:160] if text else f"exit={result.returncode}"


def run_probe(cmd: list[str], timeout: int = 8) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except Exception:
        return None


def wsl_ubuntu_info() -> dict:
    info = {
        "wsl_ubuntu_available": False,
        "wsl_ubuntu_hermes_command_found": False,
        "wsl_ubuntu_hermes_path": "not found",
        "wsl_ubuntu_hermes_version": "not found",
    }
    if not command_found("wsl"):
        return info
    ubuntu = run_probe(["wsl", "-d", "Ubuntu", "--", "bash", "-lc", "true"])
    info["wsl_ubuntu_available"] = bool(ubuntu and ubuntu.returncode == 0)
    if not info["wsl_ubuntu_available"]:
        return info
    hermes_path = run_probe(["wsl", "-d", "Ubuntu", "--", "bash", "-lc", "command -v hermes"])
    if hermes_path and hermes_path.returncode == 0 and hermes_path.stdout.strip():
        info["wsl_ubuntu_hermes_command_found"] = True
        info["wsl_ubuntu_hermes_path"] = hermes_path.stdout.strip().splitlines()[0][:160]
        version = run_probe(["wsl", "-d", "Ubuntu", "--", "bash", "-lc", "hermes --version || true"])
        if version and (version.stdout or version.stderr):
            info["wsl_ubuntu_hermes_version"] = (version.stdout or version.stderr).strip().splitlines()[0][:160]
    return info


def prereqs() -> dict:
    git_bash = git_bash_paths()
    wsl_ubuntu = wsl_ubuntu_info()
    local_hermes_found = command_found("hermes")
    hermes_found = local_hermes_found or wsl_ubuntu["wsl_ubuntu_hermes_command_found"]
    data = {
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "is_windows": platform.system().lower() == "windows",
        "is_admin": is_admin(),
        "ai_sandbox_profile": str(Path.home()).lower().endswith("ai_sandbox"),
        "curl_exe_found": command_found("curl.exe"),
        "curl_alias_warning": "Use curl.exe in PowerShell; curl may be Invoke-WebRequest.",
        "bash_found": command_found("bash"),
        "git_bash_paths": git_bash,
        "wsl_found": command_found("wsl"),
        "git_found": command_found("git"),
        "uv_found": command_found("uv"),
        "node_found": command_found("node"),
        "docker_found_optional": command_found("docker"),
        "ollama_found": command_found("ollama"),
        "hermes_command_found": hermes_found,
        "local_windows_hermes_command_found": local_hermes_found,
        "wsl_ubuntu_available": wsl_ubuntu["wsl_ubuntu_available"],
        "wsl_ubuntu_hermes_command_found": wsl_ubuntu["wsl_ubuntu_hermes_command_found"],
        "wsl_ubuntu_hermes_path": wsl_ubuntu["wsl_ubuntu_hermes_path"],
        "hermes_help": safe_version(["hermes", "--help"]) if local_hermes_found else (
            f"found in Ubuntu WSL: {wsl_ubuntu['wsl_ubuntu_hermes_path']}"
            if wsl_ubuntu["wsl_ubuntu_hermes_command_found"] else "not found"
        ),
        "hermes_version": safe_version(["hermes", "--version"]) if local_hermes_found else wsl_ubuntu["wsl_ubuntu_hermes_version"],
    }
    data["can_download_installer"] = data["curl_exe_found"] or True
    data["local_shell_available"] = data["bash_found"] or bool(git_bash) or data["wsl_found"]
    data["install_safe_now"] = False
    data["install_safe_reason"] = (
        "Installation is guarded in this milestone because package installation "
        "and external installer execution are not allowed without separate human approval."
    )
    return data


def base_manifest(extra: dict | None = None) -> dict:
    p = prereqs()
    manifest = {
        "local_only": True,
        "paid_vps_required": False,
        "vps_used": False,
        "admin_required": False,
        "external_installer_downloaded": False,
        "installer_executed": False,
        "hermes_command_found": p["hermes_command_found"],
        "codex_provider_supported": None,
        "codex_provider_truth": "pending / not verified until Hermes provider docs or a local Hermes command confirm Codex support",
        "telegram_token_required_from_user": True,
        "secrets_written": False,
        "live_api_used": False,
        "human_review_required": True,
    }
    if extra:
        manifest.update(extra)
    return manifest


def installer_path_for(path: Path) -> Path:
    return path / "install.sh"


def find_latest_installer() -> Path | None:
    if not RUN_ROOT.exists():
        return None
    candidates = sorted(RUN_ROOT.glob("*/install.sh"), key=lambda item: item.parent.name)
    return candidates[-1] if candidates else None


def download_installer() -> dict:
    out_dir = run_dir()
    installer = installer_path_for(out_dir)
    downloaded = False
    error = ""
    try:
        with urllib.request.urlopen(INSTALLER_URL, timeout=30) as response:
            body = response.read()
        installer.write_bytes(body)
        downloaded = True
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        error = f"{type(exc).__name__}: {str(exc)[:180]}"
    manifest = base_manifest({"external_installer_downloaded": downloaded})
    write_report_files(out_dir, manifest, installer if downloaded else None, install_attempt={
        "install_attempted": False,
        "installer_download_error": error,
    })
    return {
        "ok": True,
        "action": "download-installer",
        "downloaded": downloaded,
        "installer_path": rel(installer) if downloaded else None,
        "error": error,
        "run_dir": rel(out_dir),
        "manifest": manifest,
    }


def inspect_installer(path: Path | None = None) -> dict:
    installer = path or find_latest_installer()
    if not installer or not installer.exists():
        return {
            "ok": True,
            "action": "inspect-installer",
            "inspected": False,
            "error": "No downloaded installer found. Run --download-installer first.",
        }
    data = installer.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    text = data.decode("utf-8", errors="replace")
    first_lines = text.splitlines()[:40]
    codex_mentions = [line for line in text.splitlines() if "codex" in line.lower()][:5]
    provider_truth = (
        "pending / not verified: downloaded installer text mentions Codex, but no local Hermes provider command has confirmed support"
        if codex_mentions
        else "pending / not verified: downloaded installer text did not clearly advertise Codex provider support"
    )
    return {
        "ok": True,
        "action": "inspect-installer",
        "inspected": True,
        "installer_path": rel(installer),
        "sha256": digest,
        "first_lines": first_lines,
        "codex_provider_supported": None,
        "codex_provider_truth": provider_truth,
        "secrets_redacted": True,
    }


def windows_commands() -> str:
    return "\n".join([
        "PowerShell safe download:",
        f"  curl.exe -L {INSTALLER_URL} -o install.sh",
        "",
        "PowerShell curl alias note:",
        "  Use curl.exe, not curl, because curl can resolve to Invoke-WebRequest in PowerShell.",
        "",
        "If bash is missing, install or open Git Bash, then inspect before running:",
        "  bash --version",
        "  head -n 40 install.sh",
        "",
        "If WSL is already installed and approved for local use:",
        "  wsl bash -lc 'bash --version'",
        "  wsl -d Ubuntu -- bash -lc 'bash --version'",
        "  wsl.exe -d Ubuntu -- bash -lc 'bash --version'",
        "",
        "If Ubuntu opens but Hermes is not found, the installer was not completed inside Ubuntu.",
        "Run these manually inside Ubuntu only after human review:",
        f"  curl -fsSL {INSTALLER_URL} | bash -s -- --skip-setup",
        "  source ~/.bashrc",
        "  command -v hermes",
        "  hermes --help",
        "",
        "Bash from PowerShell can route to WSL on some Windows setups; prefer explicit wsl -d Ubuntu when troubleshooting distro-specific installs.",
        "",
        "Do not paste Telegram tokens into git. Put secrets only in a local .env file.",
        "No paid VPS is required for this local-first plan.",
    ])


def install_local() -> dict:
    out_dir = run_dir()
    installer = find_latest_installer()
    p = prereqs()
    reason = p["install_safe_reason"]
    attempt = {
        "install_attempted": False,
        "installer_executed": False,
        "status": "blocked_by_policy",
        "reason": reason,
        "installer_available": bool(installer and installer.exists()),
        "is_admin": p["is_admin"],
        "next_steps": [
            "Review installer hash and first lines.",
            "Open a non-admin Git Bash or WSL shell only if the user approves.",
            "For Ubuntu WSL troubleshooting, use wsl -d Ubuntu or wsl.exe -d Ubuntu and rerun command -v hermes.",
            "Provide provider and Telegram secrets manually in a local .env file later.",
        ],
    }
    manifest = base_manifest({"external_installer_downloaded": bool(installer), "installer_executed": False})
    write_report_files(out_dir, manifest, installer, install_attempt=attempt)
    return {"ok": True, "action": "install-local", "attempt": attempt, "run_dir": rel(out_dir), "manifest": manifest}


def write_report_files(out_dir: Path, manifest: dict, installer: Path | None = None, install_attempt: dict | None = None) -> None:
    p = prereqs()
    review = inspect_installer(installer) if installer and installer.exists() else {
        "inspected": False,
        "error": "No installer downloaded in this run.",
    }
    if review.get("codex_provider_truth"):
        manifest["codex_provider_truth"] = review["codex_provider_truth"]
        manifest["codex_provider_supported"] = review.get("codex_provider_supported")
    write_json(out_dir / "00_manifest.json", manifest)
    (out_dir / "01_prereq_report.md").write_text(
        "# Hermes Prerequisite Report\n\n"
        f"- Windows: {p['is_windows']}\n"
        f"- ai_sandbox profile: {p['ai_sandbox_profile']}\n"
        f"- Admin shell: {p['is_admin']}\n"
        f"- curl.exe found: {p['curl_exe_found']}\n"
        f"- bash found: {p['bash_found']}\n"
        f"- WSL found: {p['wsl_found']}\n"
        f"- Ubuntu WSL available: {p['wsl_ubuntu_available']}\n"
        f"- Ubuntu WSL Hermes command found: {p['wsl_ubuntu_hermes_command_found']}\n"
        f"- Ubuntu WSL Hermes path: {p['wsl_ubuntu_hermes_path']}\n"
        f"- Git Bash paths: {', '.join(p['git_bash_paths']) or 'none detected'}\n"
        f"- Hermes command found: {p['hermes_command_found']}\n"
        f"- Hermes version: {p['hermes_version']}\n"
        f"- Install safe now: {p['install_safe_now']} ({p['install_safe_reason']})\n",
        encoding="utf-8",
    )
    (out_dir / "02_installer_review.md").write_text(
        "# Installer Review\n\n"
        f"- Installer URL: {INSTALLER_URL}\n"
        f"- Inspected: {review.get('inspected', False)}\n"
        f"- SHA256: {review.get('sha256', 'not available')}\n"
        f"- Codex provider truth: {manifest['codex_provider_truth']}\n\n"
        "## First Lines\n\n"
        "```text\n" + "\n".join(review.get("first_lines", []))[:4000] + "\n```\n",
        encoding="utf-8",
    )
    write_json(out_dir / "03_install_attempt.json", install_attempt or {"install_attempted": False, "installer_executed": False})
    (out_dir / "04_provider_support_review.md").write_text(
        "# Provider Support Review\n\n"
        f"- Codex preferred: true\n"
        f"- Codex provider supported: {manifest['codex_provider_supported']}\n"
        f"- Truth: {manifest['codex_provider_truth']}\n"
        "- ChatGPT/Claude/Codex model council remains manual/planning-only.\n"
        "- Gemma/Ollama local worker lane remains a cheap local worker direction.\n",
        encoding="utf-8",
    )
    (out_dir / "05_telegram_setup_plan.md").write_text(read_text(REPO_ROOT / "docs" / "HERMES_TELEGRAM_MANUAL_SETUP_PLAN.md"), encoding="utf-8")
    (out_dir / "06_local_ai_sandbox_plan.md").write_text(read_text(REPO_ROOT / "docs" / "LOCAL_FIRST_NO_VPS_AGENT_STRATEGY.md"), encoding="utf-8")
    (out_dir / "07_model_council_integration.md").write_text(read_text(REPO_ROOT / "docs" / "HERMES_LOCAL_INSTALL_AND_PROVIDER_PLAN.md"), encoding="utf-8")
    (out_dir / "08_human_next_steps.md").write_text(
        "# Human Next Steps\n\n"
        "1. Review installer hash and first lines.\n"
        "2. Decide whether to run installer manually in a non-admin local shell.\n"
        "3. If WSL Ubuntu opens but Hermes is missing, run `wsl -d Ubuntu` or `wsl.exe -d Ubuntu` and complete the installer inside Ubuntu after review.\n"
        "4. Create Telegram bot token/chat ID manually if desired.\n"
        "5. Store secrets only in local `.env`.\n"
        "6. Rerun status checks after setup.\n",
        encoding="utf-8",
    )
    (out_dir / "09_preview.html").write_text(
        "<!doctype html><meta charset='utf-8'><title>Hermes Local Bootstrap</title>"
        "<h1>Hermes Local Bootstrap</h1>"
        f"<p>Local only: {html.escape(str(manifest['local_only']))}</p>"
        f"<p>Paid VPS required: {html.escape(str(manifest['paid_vps_required']))}</p>"
        f"<p>Hermes command found: {html.escape(str(manifest['hermes_command_found']))}</p>"
        f"<p>Codex provider truth: {html.escape(manifest['codex_provider_truth'])}</p>",
        encoding="utf-8",
    )


def write_report() -> dict:
    out_dir = run_dir()
    installer = find_latest_installer()
    manifest = base_manifest({"external_installer_downloaded": bool(installer)})
    write_report_files(out_dir, manifest, installer)
    return {"ok": True, "action": "write-report", "run_dir": rel(out_dir), "manifest": manifest}


def status() -> dict:
    return {
        "ok": True,
        "action": "status",
        "installer_url": INSTALLER_URL,
        "prereqs": prereqs(),
        "manifest": base_manifest(),
        "latest_run": rel(latest_run()) if latest_run() else None,
    }


def latest() -> dict:
    run = latest_run()
    if not run:
        return {"ok": False, "error": "no Hermes bootstrap runs found"}
    manifest_path = run / "00_manifest.json"
    manifest = json.loads(read_text(manifest_path)) if manifest_path.exists() else {}
    return {"ok": True, "action": "latest", "run_dir": rel(run), "manifest": manifest}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hermes local bootstrap helper")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--check-prereqs", action="store_true")
    parser.add_argument("--download-installer", action="store_true")
    parser.add_argument("--inspect-installer", action="store_true")
    parser.add_argument("--install-local", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--latest", action="store_true")
    parser.add_argument("--print-windows-commands", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.print_windows_commands:
        print(windows_commands())
        return 0
    if args.download_installer:
        data = download_installer()
    elif args.inspect_installer:
        data = inspect_installer()
    elif args.install_local:
        data = install_local()
    elif args.write_report:
        data = write_report()
    elif args.latest:
        data = latest()
    elif args.check_prereqs:
        data = {"ok": True, "action": "check-prereqs", "prereqs": prereqs(), "manifest": base_manifest()}
    else:
        data = status()

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(f"hermes_local_bootstrap ok={data.get('ok')} action={data.get('action')}")
    return 0 if data.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
