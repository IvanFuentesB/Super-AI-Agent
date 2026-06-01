#!/usr/bin/env python3
"""Computer-Use Adapter Contract (N+6.12A) - DISABLED, non-runtime stub.

Inert interface contract for a future *supervised* computer-use capability. It
documents - as data shapes and default-False flags - the observe -> plan -> action
loop common to the computer-use stacks Ghoti statically inspected this milestone.
No third-party code is copied, imported, installed, or run. Nothing here drives a
browser, controls a desktop, presses a pointer or key, or opens the network. Every
capability flag defaults to disabled and is additionally overridden by the global
kill switch.

Patterns documented (inspiration only; read-only static inspection; no code copied)
-----------------------------------------------------------------------------------
- UI-TARS .............. observation-first screen parsing (source-needed; not cloned)
- Browser Harness ...... thin CDP-to-Chrome harness (MIT) - self-writing-code risk
- Vercel agent-browser . native CLI driving pinned Chrome-for-Testing (Apache-2.0)
- TryCUA / CUA Driver .. containerised desktop sandbox + capability/policy split (MIT)
- Browser-use .......... browser-agent framework (MIT) - stealth/captcha risk

Apache-2.0 (agent-browser) would require preserving NOTICE/attribution IF any of
its code were reused. None is reused here - patterns only - so no NOTICE applies.

Safety
------
computer_use_enabled defaults False. Each sub-capability (live browser, desktop
control, click, type, hotkeys, network, container sandbox, self-writing code)
defaults False. Stealth / captcha-bypass / proxy-rotation capabilities are
PERMANENTLY refused under Ghoti's no-bypass policy and cannot be enabled by this
contract at all. Wiring an actual runtime is out of scope for this milestone and
would require its own approved milestone behind a human approval gate and a Codex
audit.

Usage:
    python 03_scripts/external_adapters/computer_use_adapter_contract.py --status --json
    python 03_scripts/external_adapters/computer_use_adapter_contract.py --describe --json
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Tuple

MILESTONE = "N+6.12A"
ADAPTER_KEY = "computer_use_stack"
CODE_COPIED_FROM_SOURCE = False

# Master flag plus global kill switch. Both are reported by status(); neither
# turns anything on, because no runtime is wired in this contract.
COMPUTER_USE_ENABLED = False
GLOBAL_KILL_SWITCH_ENGAGED = True

# Capabilities that can never be enabled by this contract (no-bypass policy).
PERMANENTLY_REFUSED_CAPABILITIES = ("stealth", "captcha_solving", "proxy_rotation")


class ComputerUsePhase(str, Enum):
    """Observation-first loop. ACTION is reached only after OBSERVE and PLAN, and
    only under a human approval gate that this contract does not grant."""

    OBSERVE = "observe"
    PLAN = "plan"
    ACTION = "action"


@dataclass(frozen=True)
class ComputerUseCapabilities:
    """Every capability defaults disabled. Field names match the repo's existing
    observation-adapter convention (click_enabled / type_enabled / hotkeys_enabled)
    so the disabled posture reads the same everywhere."""

    computer_use_enabled: bool = False
    live_browser_enabled: bool = False
    desktop_control_enabled: bool = False
    click_enabled: bool = False
    type_enabled: bool = False
    hotkeys_enabled: bool = False
    network_enabled: bool = False
    container_sandbox_enabled: bool = False
    self_writing_code_enabled: bool = False
    stealth_enabled: bool = False
    live_api_enabled: bool = False


@dataclass(frozen=True)
class InspectedStack:
    """One inspected upstream and the single pattern Ghoti took from it (idea only)."""

    name: str
    license_family: str
    cloned: bool
    documented_pattern: str
    primary_risk: str


INSPECTED_STACKS: Tuple[InspectedStack, ...] = (
    InspectedStack("UI-TARS", "unknown", False,
                   "observation-first screen parsing into elements/actions",
                   "source ambiguous - not cloned; desktop control if ever run"),
    InspectedStack("Browser Harness", "MIT", True,
                   "thin one-socket CDP-to-Chrome harness",
                   "self-writing helper code during a task"),
    InspectedStack("Vercel agent-browser", "Apache-2.0", True,
                   "discrete CLI commands driving pinned Chrome-for-Testing",
                   "global native-binary install; downloads a Chrome build"),
    InspectedStack("TryCUA / CUA Driver", "MIT", True,
                   "containerised desktop sandbox; capability/policy separation",
                   "live desktop control; Docker/QEMU/KASM runtime"),
    InspectedStack("Browser-use", "MIT", False,
                   "browser-agent framework with custom-tool registration",
                   "cloud stealth/captcha/proxy features conflict with no-bypass"),
)


def capabilities() -> ComputerUseCapabilities:
    """The single source of truth for the disabled posture (all flags False)."""

    return ComputerUseCapabilities(computer_use_enabled=COMPUTER_USE_ENABLED)


def action_blocked_reason(caps: ComputerUseCapabilities) -> str:
    """Why the ACTION phase is unreachable. Always returns a refusal."""

    if GLOBAL_KILL_SWITCH_ENGAGED:
        return "global kill switch engaged"
    if not caps.computer_use_enabled:
        return "computer_use_enabled is False"
    return "no runtime is wired (contract is non-runtime by design)"


def status() -> dict:
    caps = capabilities()
    return {
        "ok": True,
        "adapter": "computer_use_adapter_contract",
        "milestone": MILESTONE,
        "adapter_key": ADAPTER_KEY,
        "kind": "non_runtime_capability_contract",
        "phases": [p.value for p in ComputerUsePhase],
        "capabilities": asdict(caps),
        "permanently_refused_capabilities": list(PERMANENTLY_REFUSED_CAPABILITIES),
        "code_copied_from_source": CODE_COPIED_FROM_SOURCE,
        "patterns_documented_only": True,
        "global_kill_switch_engaged": GLOBAL_KILL_SWITCH_ENGAGED,
        "runtime_wired": False,
        "safe_to_run": False,
        "external_code_executed": False,
        "external_code_imported": False,
        "installs_performed": False,
        "network_used": False,
        "live_browser_used": False,
        "desktop_controlled": False,
        "action_blocked_reason": action_blocked_reason(caps),
        "human_approval_required": True,
    }


def describe() -> dict:
    return {
        "milestone": MILESTONE,
        "adapter_key": ADAPTER_KEY,
        "loop": [p.value for p in ComputerUsePhase],
        "inspected_stacks": [asdict(s) for s in INSPECTED_STACKS],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Computer-use non-runtime capability contract (disabled).")
    parser.add_argument("--status", action="store_true",
                        help="report disabled/contract status")
    parser.add_argument("--describe", action="store_true",
                        help="print the inert loop + inspected-stack summary")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    payload = describe() if args.describe else status()

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
