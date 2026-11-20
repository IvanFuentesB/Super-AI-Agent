"""Synthetic boundaries plus genuine packaged SDK/runtime checks; no browser."""
import asyncio
import importlib.metadata
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cua_driver as sdk
from cua_observation import ObservationHost, Scope, Refused, Authorization


class Boundaries(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.scope = Scope(pid=12345, window_id=67890,
                           profile='synthetic-profile', origin='http://127.0.0.1:8765')

    async def test_default_disabled(self):
        with self.assertRaises(Refused):
            ObservationHost(self.scope)

    async def test_actual_native_runtime_and_constructor(self):
        host = ObservationHost(self.scope, enabled=True)
        try:
            metadata = await host.metadata()
            self.assertEqual(importlib.metadata.version('cua-driver'), '0.34.0')
            self.assertEqual(metadata.driver_version, '0.34.0')
            self.assertTrue(metadata.embedded)
            self.assertEqual(metadata.pid, os.getpid())
            self.assertEqual(host.execution_mode, sdk.DriverExecutionMode.EMBEDDED)
        finally:
            await host.close()

    async def test_forbidden_operations_never_dispatch(self):
        host = ObservationHost(self.scope, enabled=True)
        try:
            for operation in ['browser_click', 'browser_navigate', 'evaluate', 'clipboard_read',
                              'browser_download', 'browser_type', 'approve', 'execute', 'observe']:
                with self.subTest(operation=operation), self.assertRaises(Refused):
                    await host.request({'operation': operation, 'approved': True})
        finally:
            await host.close()

    async def test_real_shutdown_revokes_connection(self):
        host = ObservationHost(self.scope, enabled=True)
        self.assertFalse((await host.request({'operation': 'status'}))['browser_enabled'])
        await host.close()
        await host.close()
        with self.assertRaises(Refused):
            await host.metadata()

    async def test_production_shape_callback_is_denied_without_attestation(self):
        # Python policy test on real SDK record types, NOT native callback delivery.
        import json
        from cua_observation import _AuthorizationHost
        gate = Authorization(self.scope)
        callback = _AuthorizationHost(gate)
        request = sdk.DriverAuthorizationRequest(
            schema='cua-driver-authorization-request-v1', nonce='synthetic', generation=1,
            daemon_instance='synthetic', permission_mode='standard',
            managed_policy_sha256=None, user_policy_sha256=None,
            adapter_id='browser_prepare.existing_profile', risk_class='synthetic',
            public_session='synthetic', transport_session='synthetic',
            resource_json=json.dumps({'pid':12345, 'window_id':67890,
                'process_fingerprint':{'pid':12345,'start_time':1,'executable':'synthetic'},
                'browser_product':'microsoft_edge','endpoint_owner_pid':12345}),
            human_summary='synthetic only', expires_unix_ms=1,
            request_digest='synthetic-not-a-grant')
        result = await callback.authorize(request)
        self.assertEqual(result.action, sdk.DriverAuthorizationAction.DENY)
        self.assertEqual(result.request_digest, request.request_digest)
        self.assertTrue(gate.revoked)

    async def test_target_origin_profile_or_stale_ref_cannot_enable(self):
        host = ObservationHost(self.scope, enabled=True)
        try:
            for extra in [{'pid':999}, {'window_id':999}, {'profile':'other'},
                          {'origin':'http://example.invalid'}, {'ref':'stale'},
                          {'generation':'old'}, {'decision':'allow'}, {'token':'forged'}]:
                with self.subTest(extra=extra), self.assertRaises(Refused):
                    await host.request({'operation':'status', **extra})
        finally:
            await host.close()

    async def test_denial_is_terminal(self):
        gate = Authorization(self.scope)
        gate.deny()
        with self.assertRaises(Refused):
            gate.require()
        self.assertTrue(gate.revoked)

    async def test_expiry_and_revocation(self):
        gate = Authorization(self.scope, clock=lambda: 20)
        gate._until = 19
        with self.assertRaises(Refused):
            gate.require()
        gate.revoke()
        with self.assertRaises(Refused):
            gate.require()

    async def test_missing_decision(self):
        gate = Authorization(self.scope)
        with self.assertRaises(Refused):
            gate.require()

    async def test_reconnect_does_not_reuse_state(self):
        first = Authorization(self.scope)
        second = Authorization(self.scope)
        self.assertNotEqual(first.generation, second.generation)
        with self.assertRaises(Refused):
            second.require()


if __name__ == '__main__':
    unittest.main(verbosity=2)
