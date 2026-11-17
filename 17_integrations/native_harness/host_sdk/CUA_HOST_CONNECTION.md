# Cua SDK host connection — incomplete, fail-closed candidate

This is NOT the requested finished human-controlled observation integration.
It establishes the exact official Python/native runtime and an immutable deny
callback in a same-process host. It exposes only content-free runtime status.
No browser, UI input, clipboard, download/upload, script execution, preparation,
attachment or navigation method is exposed. All browser work is held.

## Reproduce the isolated proof (Windows AMD64, Python >=3.10)

Create a project-local venv. Do not install into an existing runtime/global Python.

```
python -m venv <isolated-venv>
<isolated-venv>/Scripts/python.exe -I -B -m pip install --no-deps --require-hashes -r cua-sdk-requirements.txt
<isolated-venv>/Scripts/python.exe -I -B test_cua_observation.py
<isolated-venv>/Scripts/python.exe -I -B cua_observation.py
```

The script is a metadata-only probe; it does not enable observation. The library
constructor is disabled by default. Explicit `enabled=True` only constructs the
SDK host, not a browser session. Version mismatches fail closed. There is no
fallback to the working CLI/MCP runtime. Runtime shutdown revokes the local gate;
a new process starts with no authority. No consent persistence or approval RPC.

The official wheel is pinned by release URL and GitHub release asset SHA256 in
the requirements file. It includes the Windows native DLL and generated Python
bindings, with no required third-party Python runtime dependencies. Provenance:
https://github.com/trycua/cua/releases/tag/cua-driver-rs-v0.34.0
Inspected source revision: b0968e1b12834e485dda68789541a3cc57664a9f.

## Actual execution versus missing proof

Passed: real SDK/native DLL loading, native constructor with authorization host,
metadata reports runtime0.34.0 embedded in the test process, shutdown, disabled
startup, closed request schema, denial and local gate expiration/revocation.
The direct callback test uses real generated SDK record types and calls Python
policy only. It is explicitly NOT native-to-Python callback delivery proof.
No test returns a fabricated SDK success. Ten focused tests passed; broad repo
suites are not represented by this count.

NOT exercised: an accepted observation, target/profile/origin enforcement on a
real binding, native callback invocation, human dialog interaction, browser
reconnect/stale-ref behavior, or authority transfer after a real browser restart.
Rejection of forged request keys is NOT proof of those unimplemented behaviors.
The earlier UI prototype is retained as task-local unintegrated evidence, not
included in this candidate or exposed as an approval surface.

## Why activation is held

At the inspected exact upstream revision:
- `cua-driver-sdk/src/lib.rs:823-844` registers the immutable callback only at
  same-process runtime construction. The real packaged constructor succeeds.
- `cua-driver-core/src/browser/prepare.rs:1124-1154` requests consent only after
  exact native window/process/browser/endpoint checks. Its resource contains
  pid, window_id, process_fingerprint (pid/start_time/executable), browser_product
  and endpoint_owner_pid. It contains NO profile pathname or page origin.
- `cua-driver-sdk/src/authorization_host.rs:130-184` has a Rust-only synthetic
  broker test. This is not an exported Python fixture API.
- The installed wheel has no supported synthetic callback trigger. Calling the
  Python callback directly or invoking private generated FFI would not prove the
  required production path and is not substituted here.

The original assumption that callback registration alone could produce a fully
attested profile/origin decision was too strong. Those facts need independently
verified trusted-host discovery and per-observation binding validation; do not
invent fields or show requested labels as driver attestations. A hostname-only
check is not a harmless-click contract. Navigation remains excluded.

A legitimate next integration test needs an explicitly scoped disposable browser
fixture: new empty synthetic profile, owned local page/window, no private profile
or credentials, native callback exercised through the actual SDK operation.
That browser launch/attachment was not performed under the current prohibition
on automatic browser attachment. No new native grant is inferred from setup.

## Review disposition

Review this as partial executable evidence and source, NOT a completed host
connection or adoption candidate. Keep UI9613 running, preserve exact fallback
manifest and both releases, and leave existing conditional/service grants unused.
Paperclip remains a separate owner/reviewer lane; no transaction repair here.
