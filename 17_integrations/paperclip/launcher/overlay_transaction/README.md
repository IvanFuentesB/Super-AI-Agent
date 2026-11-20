# Reviewed transaction source snapshot

This source-only DRAFT updates the existing publication lane to owner candidate
`76c8c81d5a896d4955984c44e5b6fbe897fddc28` / tree
`b82342676de9218f63fe9a34f7a8a026adc135dc`. It is **CHANGES_REQUESTED**,
not adoption-approved, an installer, or permission to run an installed service.

The original rejected snapshot and its 5 PASS / 1 FAIL independent result remain
in public history and in SOURCE_MANIFEST.json. This successor removes destructive
rollback copying, introduces a target lock, constrains Git authority and enforces
the rehearsal aggregate gate. Those improvements do not erase remaining findings.

Independent static review still identifies missing-component rollback provenance
and insufficient physical fencing of internal Git/absent restore paths. Retained
and new independent executable results are reported separately; owner totals of
33 regression tests, eight driver-gate tests and 18 rehearsal scenarios are not
independent execution. Do not adopt this transaction while findings remain open.

`source/` contains exact committed first-party helper, transition contract, driver,
staging utilities and focused tests. SOURCE_MANIFEST binds every raw source file
to its original Git blob and provenance; no private ancestry is imported. No
source transformation is intended.

Supported dependency scope remains the exact reviewed overlay from e04e2ae to
e8ad1fd and package index recorded in the manifest. The separate launcher pin
review for 1e788e6 remains intact. Package payloads, native helpers and runtime
configuration are not supplied here; this is not a portable installation recipe.

Process-interruption recovery evidence is distinct from power-loss durability.
Actual host adoption, human permissions, finite service operation and live
acceptance remain owned by the authorized host operator and are not proved here.

## Independent boundary reproductions

The portable independent probe retains the two failing ownership assertions.
It uses only small synthetic real-Git fixtures; it does not prove built-output
compatibility. Supply two fresh/disjoint owned directories outside the source.
The regression is expected RED on this rejected candidate, not a passing suite.

```text
python -I -B independent_tests/transaction_boundary_probes.py <fresh-disposable-root> <owned-evidence-dir>
```

F1: after rollback intent, an output disappears without rb-out move evidence;
recover incorrectly repairs it. F2: an internal Git ref namespace junction lets
fetch write outside the target. Both were independently reproduced on the exact
helper with valid fixture preflights:0 PASS/2 RED/0 setup errors. Raw index/target,
journal and outside-sentinel assertions are retained. Publication changes only
fixture/report path binding and host-specific PATH, never the acceptance rules.

Separate parent real-build evidence has11 acceptance checks PASS, plus two fixture
preflight/cleanup records. It includes a real owned-process kill during rollback
with exact fresh-process recovery. One earlier Windows venv PID setup assertion
is retained separately, not counted as a product failure or silently discarded.
These results do not cancel the two RED findings or authorize adoption.

The exact original committed source bytes, including CRLF Python and Markdown,
are retained with the scoped `.gitattributes` rule `source/** -text`. Staged-blob
normalization mismatches were caught before publication and inventoried together.
No silent normalization or global Git setting change is permitted.
