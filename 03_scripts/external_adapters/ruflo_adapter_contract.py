#!/usr/bin/env python3
"""Ruflo Adapter Contract (N+6.12A) - DISABLED, non-runtime pattern stub.

This module RE-EXPRESSES, from scratch, a small coordination *pattern* observed
during read-only static inspection of Ruflo (ruvnet/ruflo, MIT). No Ruflo source
code is copied or vendored. It is an inert contract: it declares data shapes and a
default-disabled feature flag. It never launches agents, never calls a model
provider, never opens a network connection, never reads credentials, and never
runs, installs, or imports any Ruflo code.

Attribution
-----------
Pattern inspiration (idea only, not code): Ruflo / claude-flow
  https://github.com/ruvnet/ruflo
License of the inspected project: MIT (which would permit reuse). Even so, Ghoti
deliberately does NOT vendor its code - see the security note below.

Security note (why this is re-expressed, not vendored)
------------------------------------------------------
Ruflo has a documented supply-chain history recorded in this repo's prior
evaluations:
  - an obfuscated malicious npm pre-install lifecycle script (reported across
    v3.1.0-alpha.55 .. v3.5.2) that deleted directories;
  - an MCP prompt-injection issue (#1375) where tool descriptions covertly added
    the maintainer as a repository contributor;
  - a remediated SQL-injection history (fixed v3.5.40).
Because of that history, Ghoti re-expresses only the *architecture idea* as the
clean data shapes below and never installs, imports, or executes Ruflo.

Re-expressed pattern (the one safe extraction for N+6.12A)
---------------------------------------------------------
1. Role-labeled single-purpose agents - each agent has exactly one narrow job.
2. Explicit coordinator/worker separation with task hand-offs.
3. Shared *local* memory as the coordination substrate - modelled as a hand-off
   record pointing at a repo-relative file, never a live bus or network endpoint.
4. Declared skills/plugins - capabilities are declared up front, not implicit.

Activation
----------
Everything here is gated behind RUFLO_SWARM_ENABLED (default False) and the global
kill switch (engaged by default). There is no runtime to turn on: activation is a
no-op that returns a blocked reason. Wiring an actual swarm runtime is explicitly
out of scope for this milestone and would require its own approved milestone with a
Codex audit gate.

Usage:
    python 03_scripts/external_adapters/ruflo_adapter_contract.py --status --json
    python 03_scripts/external_adapters/ruflo_adapter_contract.py --describe --json
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Tuple

MILESTONE = "N+6.12A"
ADAPTER_KEY = "ruflo_multi_agent_pattern"
PATTERN_SOURCE = "Ruflo / claude-flow (ruvnet/ruflo)"
PATTERN_SOURCE_URL = "https://github.com/ruvnet/ruflo"
PATTERN_SOURCE_LICENSE = "MIT"
CODE_COPIED_FROM_SOURCE = False

# Default-disabled feature flag and global kill switch. Both are inspected by
# activation_blocked_reason(); neither enables a runtime (none exists here).
RUFLO_SWARM_ENABLED = False
GLOBAL_KILL_SWITCH_ENGAGED = True


class AgentRole(str, Enum):
    """Role labels for the coordinator/worker separation pattern."""

    COORDINATOR = "coordinator"
    WORKER = "worker"


@dataclass(frozen=True)
class DeclaredSkill:
    """A capability an agent declares up front (declared, not implicit)."""

    name: str
    summary: str


@dataclass(frozen=True)
class AgentSpec:
    """A single-purpose, role-labeled agent. Inert description only - no behaviour."""

    name: str
    role: AgentRole
    single_purpose: str
    declared_skills: Tuple[DeclaredSkill, ...] = ()


@dataclass(frozen=True)
class HandoffRecord:
    """A local, file-shaped hand-off between two agents.

    local_payload_ref is always a repo-relative path - never a URL and never a
    live message bus. This keeps the coordination substrate local-only.
    """

    from_agent: str
    to_agent: str
    task: str
    local_payload_ref: str


@dataclass
class RufloPatternContract:
    """Inert description of a coordinator + workers + local hand-offs.

    Holds data only. It has no method that performs work - the closest thing is
    activation_blocked_reason(), which always refuses.
    """

    coordinator: AgentSpec
    workers: Tuple[AgentSpec, ...] = ()
    handoffs: Tuple[HandoffRecord, ...] = ()

    def activation_blocked_reason(self) -> str:
        if GLOBAL_KILL_SWITCH_ENGAGED:
            return "global kill switch engaged"
        if not RUFLO_SWARM_ENABLED:
            return "RUFLO_SWARM_ENABLED is False"
        return "no runtime is wired (contract is non-runtime by design)"

    def describe(self) -> dict:
        return {
            "coordinator": {
                "name": self.coordinator.name,
                "role": self.coordinator.role.value,
                "single_purpose": self.coordinator.single_purpose,
                "declared_skills": [s.name for s in self.coordinator.declared_skills],
            },
            "workers": [
                {
                    "name": w.name,
                    "role": w.role.value,
                    "single_purpose": w.single_purpose,
                    "declared_skills": [s.name for s in w.declared_skills],
                }
                for w in self.workers
            ],
            "handoffs": [
                {
                    "from_agent": h.from_agent,
                    "to_agent": h.to_agent,
                    "task": h.task,
                    "local_payload_ref": h.local_payload_ref,
                }
                for h in self.handoffs
            ],
        }


def example_contract() -> RufloPatternContract:
    """A tiny, illustrative instance of the pattern. Pure data - it runs nothing."""

    coordinator = AgentSpec(
        name="planner",
        role=AgentRole.COORDINATOR,
        single_purpose="split one approved task into narrow worker hand-offs",
        declared_skills=(
            DeclaredSkill("decompose", "break a task into single-purpose steps"),
            DeclaredSkill("route", "assign each step to one worker"),
        ),
    )
    drafter = AgentSpec(
        name="drafter",
        role=AgentRole.WORKER,
        single_purpose="produce a draft for exactly one step",
        declared_skills=(DeclaredSkill("draft", "write one local artifact"),),
    )
    checker = AgentSpec(
        name="checker",
        role=AgentRole.WORKER,
        single_purpose="validate exactly one draft against the step's intent",
        declared_skills=(DeclaredSkill("validate", "check one local artifact"),),
    )
    handoffs = (
        HandoffRecord(
            from_agent="planner",
            to_agent="drafter",
            task="draft step 1",
            local_payload_ref="14_context/compact_memory/example_step_1.json",
        ),
        HandoffRecord(
            from_agent="drafter",
            to_agent="checker",
            task="validate step 1 draft",
            local_payload_ref="14_context/compact_memory/example_step_1_draft.json",
        ),
    )
    return RufloPatternContract(coordinator=coordinator, workers=(drafter, checker),
                                handoffs=handoffs)


def status() -> dict:
    contract = example_contract()
    return {
        "ok": True,
        "adapter": "ruflo_adapter_contract",
        "milestone": MILESTONE,
        "adapter_key": ADAPTER_KEY,
        "kind": "non_runtime_pattern_contract",
        "pattern_source": PATTERN_SOURCE,
        "pattern_source_url": PATTERN_SOURCE_URL,
        "pattern_source_license": PATTERN_SOURCE_LICENSE,
        "code_copied_from_source": CODE_COPIED_FROM_SOURCE,
        "re_expressed_from_scratch": True,
        "ruflo_swarm_enabled": RUFLO_SWARM_ENABLED,
        "global_kill_switch_engaged": GLOBAL_KILL_SWITCH_ENGAGED,
        "runtime_wired": False,
        "safe_to_run": False,
        "external_code_executed": False,
        "external_code_imported": False,
        "installs_performed": False,
        "network_used": False,
        "model_provider_called": False,
        "credentials_read": False,
        "activation_blocked_reason": contract.activation_blocked_reason(),
        "human_approval_required": True,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Ruflo non-runtime pattern contract (disabled by default).")
    parser.add_argument("--status", action="store_true",
                        help="report disabled/contract status")
    parser.add_argument("--describe", action="store_true",
                        help="print the inert example pattern structure")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    if args.describe:
        payload = {"milestone": MILESTONE, "adapter_key": ADAPTER_KEY,
                   "pattern": example_contract().describe()}
    else:
        payload = status()

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
