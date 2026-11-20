# Offline assistant source snapshot

The manifest pins six first-party files from the reviewed assistant candidate.
The planner and approval workflow tests use synthetic task and event data. The
workflow test needs an existing compatible Hermes source checkout and interpreter
with its dependencies. It uses an isolated temporary store. The calendar test
uses a mock transport, including the official client test.

```text
python test_nova_planner.py
python test_nova_google_readonly.py
python test_nova_workflow.py <hermes-source>
```

This port carries source and offline tests for review. The installed runtime,
authorized host callback, real accounts and live calendar acceptance have
separate gates. No runtime records, credentials, speech, or native-host
integration changes are included.
