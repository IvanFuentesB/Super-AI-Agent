"""Disabled-by-default Cua 0.34.0 host connection.

The real same-process SDK runtime is constructed here, never a CLI/MCP fallback.
Browser operations remain unavailable: 0.34.0's attachment callback cannot attest
this host's requested profile/origin contract. Do not describe this candidate as
an operational browser-observation adapter.
"""
import importlib.metadata
import json
import os
import time
import uuid
from dataclasses import dataclass

import cua_driver as sdk


class Refused(RuntimeError):
    """Content-free failure suitable for an untrusted caller."""


@dataclass(frozen=True)
class Scope:
    pid: int
    window_id: int
    profile: str
    origin: str

    def __post_init__(self):
        if type(self.pid) is not int or self.pid <= 0:
            raise ValueError('invalid process')
        if type(self.window_id) is not int or self.window_id <= 0:
            raise ValueError('invalid window')
        if not self.profile or self.origin != 'http://127.0.0.1:8765':
            raise ValueError('scope is not the local NOVA observation contract')


class Authorization:
    """No persisted grant, caller-provided approval or cross-generation reuse."""

    def __init__(self, scope, clock=time.monotonic):
        self.scope = scope
        self.generation = uuid.uuid4().hex
        self.revoked = False
        self._until = 0.0
        self._clock = clock

    def require(self):
        if self.revoked or self._clock() >= self._until:
            raise Refused('missing_expired_or_revoked_decision')

    def revoke(self):
        self.revoked = True
        self._until = 0.0

    deny = revoke


class _AuthorizationHost(sdk.DriverAuthorizationHost):
    """Actual SDK callback implementation; no externally supplied decision path."""

    def __init__(self, gate):
        self._gate = gate

    async def authorize(self, request):
        # Do not log requests, resource JSON, nonce, digest or target identities.
        # A prior denial cannot be converted into a new prompt/retry.
        self._gate.deny()
        return sdk.DriverAuthorizationDecision(
            action=sdk.DriverAuthorizationAction.DENY,
            request_digest=request.request_digest)


def _options():
    return sdk.ConfiguredDriverOptions(
        claude_code_compatibility=False,
        authorization=sdk.RuntimeAuthorizationOptions(
            allowed_modes=[sdk.SessionPermissionMode.STANDARD],
            compatibility_mode=sdk.SessionPermissionMode.STANDARD,
            compatibility_capability_manifest_path=None,
            compatibility_bounded_manifest_path=None,
            unrestricted_acknowledged=False,
            max_session_ttl_seconds=60, max_idle_ttl_seconds=30))


class ObservationHost:
    """Owns an SDK runtime, not a browser attachment. Initial integration held.

    ``enabled`` permits only constructing this isolated host connection, not
    browser access. No command-line server, network listener or model-facing
    authority setter is installed. Production adoption requires separate review.
    """

    def __init__(self, scope, *, enabled=False):
        if enabled is not True:
            raise Refused('host_connection_disabled')
        if importlib.metadata.version('cua-driver') != '0.34.0':
            raise Refused('sdk_version_mismatch')
        self._owner = os.getpid()
        self._gate = Authorization(scope)
        self._callback = _AuthorizationHost(self._gate)
        self._driver = sdk.CuaDriver.create_configured_with_authorization_host(
            _options(), self._callback)
        self._closed = False

    @property
    def execution_mode(self):
        return self._driver.execution_mode()

    async def metadata(self):
        if self._closed or os.getpid() != self._owner:
            raise Refused('closed_or_different_process')
        data = await self._driver.metadata()
        if data.driver_version != '0.34.0' or not data.embedded or data.pid != self._owner:
            await self.close()
            raise Refused('native_runtime_identity_mismatch')
        return data

    async def request(self, payload):
        # Closed schema; no arbitrary SDK tool names/arguments or approval keys.
        # No browser call is attempted, including preflight/setup calls that may
        # mutate debugging settings before the SDK invokes its callback.
        if type(payload) is not dict or payload != {'operation': 'status'}:
            raise Refused('observation_contract_unavailable')
        data = await self.metadata()
        return {'sdk_version': data.driver_version, 'embedded': data.embedded,
                'browser_enabled': False,
                'reason': 'profile_origin_attestation_and_callback_test_unverified'}

    async def close(self):
        if not self._closed:
            self._closed = True
            self._gate.revoke()
            await self._driver.shutdown()


async def _probe():
    # Synthetic scope only; constructing a runtime does not inspect this target.
    host = ObservationHost(Scope(1, 1, 'synthetic', 'http://127.0.0.1:8765'), enabled=True)
    try:
        print(json.dumps(await host.request({'operation': 'status'})))
    finally:
        await host.close()


if __name__ == '__main__':
    import asyncio
    # Explicit metadata-only executable. No browser activation option exists.
    asyncio.run(_probe())
