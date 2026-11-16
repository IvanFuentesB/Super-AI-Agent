# Ghoti Current Product Status

## Publication and installation snapshot — 2026-11-16

Source publication, independent acceptance, main integration and installed-host
adoption are separate gates. This snapshot supersedes the historical MVP claims
below; neither a draft PR nor a successful patch apply is deployment approval.

| Component | Source commit | Remote branch/PR | Review | Main integration | Installed version |
| --- | --- | --- | --- | --- | --- |
| NOVA static UI and retained regressions | `9ad5a3938d4762e28a8e684b2637d8eae2b6fb7f` (parent `e108378`) | [PR #24](https://github.com/IvanFuentesB/Super-AI-Agent/pull/24), `IvanCX/nova-ui-publication`, port `043aee997bd9f621885be26351a9081775d0ecaf` | DRAFT / CHANGES_REQUESTED; safe source publication, product not accepted | Not merged | Installed NOVA pointer names `9613e877bcc57475c8e168bd6778523a31d83ff9`; no live-process acceptance performed |
| Optional native coding harness | `890b48c2380f5d43b3c89a7ecec3381ca6b2116d` | [PR #25](https://github.com/IvanFuentesB/Super-AI-Agent/pull/25), `IvanCX/native-harness-publication`, port `7c2e2a56cbbe3f8455f9e71d26f54e842876e38e` | Independently APPROVED for optional source integration; 70 offline tests PASS | Merged at `782b247cd22561cba26bbc248088fbff84d0e483`; all 14 blobs verified | Published component not host-adopted; live adapter remains disabled |
| Paperclip Windows repair/declaration patch recipe | `f2b01139d79c71e4596c0e0aaab105e194b18c19` / `e04e2ae1a0d47cdedf5380b5a0d94f280a82d5d1` | [PR #26](https://github.com/IvanFuentesB/Super-AI-Agent/pull/26), `IvanCX/paperclip-worker-patches` | DRAFT; retained repair/declaration approvals; four earlier prerequisites NOT independently approved | Not merged; eight patches reproduce the exact approved final tree | Owner-confirmed installed declaration/preflight at `e04e2ae`; no new service start or runtime acceptance here |
| Corrected Paperclip launcher source port | `13857ef7dbcf7be9d5a93b2da5bf90bf9d3edd25`, with ONE recorded interpreter-path transformation | [PR #27](https://github.com/IvanFuentesB/Super-AI-Agent/pull/27), `IvanCX/paperclip-launcher-source`, port `cc862486d5a4d47b78de0023cbc75f1332acbc24` | Independently safe for DRAFT publication; 5 focused checks PASS; original approval does not automatically cover this port | Not merged; exact host/helper dependencies remain required | Original corrected launcher owner-confirmed installed; published transformed port NOT adopted |
| Narrow Paperclip configuration operation | Eight dirty source files at `e04e2ae` base | Unpublished; frozen owner commit requested | Existing control 2/2 PASS; same 12 candidate cases: 8 PASS, 4 FAIL; test-only snapshot, no approval | Not integrated | Not established; no production save attempted |
| Runtime Paperclip status contract | Frozen three-file overlay delivered in archive `8bf3fd4891383a737b6aabcfde52e75d0541a2fc6f24dbca654c6c5976bb5382`, `e108378` base | Unpublished: private company binding and absent runtime dependencies require an owner-prepared privacy-safe candidate | Independent 14/14 synthetic tests PASS; not live-state acceptance or publication clearance | Not integrated | Not installed by this run |
| Checkpoint/approval correction | Seven dirty source files at `e2d1c3992f0160414eb48c125b70057aec80aa39` base | Unpublished; immutable owner candidate and scoped review required | Independent acceptance remains gated; historical raw-byte requirements unchanged | Not integrated | No migration, restart or publication authorized by this source review |
| Remaining personal toolchain delivery | `ed090282671fb9ba7fafda264c5d5a9cfb942be4` base, 131 source changes at inspection | Unpublished pending frozen first-party source slice; harness separated above | No approval of dirty working tree or upstream/vendor history | Not integrated | Existing host setup unchanged |

### Executed checks and known defects

- UI: 103 Node tests and 6 markup tests passed. Retained independent regression
  suite: 1 PASS / 3 FAIL. Pending Stop and the running snapshot after failed Stop
  can lose unresolved visibility; top-level free text can claim verification
  without structured SUCCESS. Same-value Paperclip attribute mutation also remains.
  The earlier `e108378` scoped review does not approve its successor.
- Harness: 70 tests ran once in a separate clean current-main worktree; all
  frozen hashes stayed unchanged. Default adapter is disabled; missing native
  receipt returns PENDING. This publication does not prove custom-role selection
  or execute an inference provider. Nested `.codex` roles do not replace root or
  global model, sandbox, approval, trust, MCP or hook settings. OpenJarvis source
  pin is `e97088f199cf86ea5f78de921772357d1f0d2cec`; no upstream tree is vendored.
- Paperclip packaging: all eight raw patches applied in an isolated clone from
  public upstream `d0bdbe11a9624435b6dca3968389bd59c6a559a2`. Each intermediate
  tree matched; final tree is `89e3964b370d6cd1474be03c04a3c3328521947f`.
  The public v0.3.1 tag is a different pin. This is apply/provenance evidence,
  not another lifecycle test, prerequisite security approval or installation.
- Configuration route: the baseline import cycle was resolved by inlining only
  `drizzle-orm` in the disposable runner. Three candidate cases return HTTP 500;
  the fourth reads old extraArgs after a simulated post-write error. Direct
  secret-service import versus the fixture's barrel mock is a suspected fixture
  gap, not a proven production defect. Assertions/mocks were not weakened, and
  the eight owner files remained unchanged.
- Frozen status overlay: an initial missing-psutil loader error executed zero
  cases. Selecting an existing compatible environment then ran all 14 unchanged
  tests once: 14 PASS, all three source hashes unchanged. No dependencies were
  installed and no live processes or service observations were queried.
- Launcher port: one absolute user-specific interpreter literal is replaced by
  Path.home() plus the same relative tool location. Two tests remain exact source
  blobs; source/published hashes and the transformation are recorded. Five
  focused offline checks passed for the one-expression delta, current-host
  environment equivalence, safe inheritance and override refusals. No unchanged
  original launcher review or installed-artifact test was repeated. The original
  unsanitized local publication candidate was NOT pushed; a new clean branch
  avoids making its history public. Global Git settings were not changed.
- Earlier current-main baseline separately passed 50 focused tests and four
  dashboard checks. Counts above describe different scopes and are not combined.
  UI, harness, worker-patch and sanitized-launcher public-repository audits each reported 150 checks, 142 PASS,
  0 failed and 8 warnings; they are bounded scans, not comprehensive clearance
  of unpublished local history.

### Publication and adoption boundaries

The UI publication contains only 32 explicit files on clean main ancestry; its
99-commit historical branch and 855-path net history were not pushed. Harness
publication contains 14 explicit files. The Paperclip package contains 20
patch/license/recipe files, not a vendor installation or foreign Git history.
The separate launcher draft contains five explicit source/test/metadata files.
Raw remote readback found CRLF-to-LF normalization in fifteen text artifacts:
the UI regression fixture/README, harness README, patch-package metadata/docs/
series/license and launcher manifest serialization. All thirteen original
harness source/test/config blobs and all eight raw patches were byte-identical
to the inputs; all fourteen main harness blobs match its published port.
Original raw-input records are retained separately from published Git-blob
hashes. The patch-package license pin is corrected to its published upstream
LF blob, retaining the original checkout hash. No source assertion or patch
payload was changed to make readback pass. Review this explicit transformation
record rather than assuming working-tree byte equality from Git content alone.
Private receipts, user data, memory databases, transcripts, dependency trees,
credentials and owner-live dirty changes remain excluded.

[PR #21](https://github.com/IvanFuentesB/Super-AI-Agent/pull/21) and
[PR #22](https://github.com/IvanFuentesB/Super-AI-Agent/pull/22) were not blindly
merged. [PR #23](https://github.com/IvanFuentesB/Super-AI-Agent/pull/23) remains a
stacked draft on #21; old tool/version claims are not current host acceptance.
No required CI checks or branch rules were reported at merge inspection; normal
PR merge with an expected-head guard was used after independent harness review.
No protection or permission setting was bypassed or changed.

The discovery map covers ten named active roots, not every historical worktree.
Claude owns the UI/configuration corrections. Hermes owns checkpoint changes,
installed runtime adoption and the running Paperclip service. Next: provide
corrected immutable UI/configuration/checkpoint candidates, correct the four configuration-fixture failures and
retain the UI regressions. Adopt accepted components only through the existing
review/host procedure; source publication does not authorize a restart, live
actions, cloud calls, hook/MCP enabling or deployment.

Hermes delivered the frozen NOVA packet (`8bf3fd4891383a737b6aabcfde52e75d0541a2fc6f24dbca654c6c5976bb5382`)
and the required corrected-launcher supplement
(`3f4ce6ca6d642bb95725aaf6135c8e345e1a922d5476f4d56a9ea8a2ac70a9cb`).
Both archive hashes and CRC checks matched. The obsolete launcher and rollback
instructions remain excluded. Owner-reported health/static-byte matches coexist
with blank-content screenshots; rendered/authenticated UI and a successful
Paperclip task/run/result/cancellation have not been established by that delivery.

---

## Historical Agent OS MVP baseline (retained)

The following material predates the publication snapshot above and documents
that earlier branch's capabilities and limits.

**Status:** Working local MVP (supervised, deny-by-default)
**Base:** PR #17 (Agent OS MVP) and PR #18 (approved execution substrate) are
merged. This feature branch clean-ports the sandboxed runner onto that base.
**Entry points:** `03_scripts/agent_os/ghoti_agent_os.py`,
`03_scripts/ghoti_product_launcher.py`

---

## Summary

This is the one-screen honest snapshot of what Ghoti can actually do on this
branch today. Everything real is local, repo-bound, and human-supervised:
suggestions, bounded text/JSON writes, and one approved allowlisted local
worker process at a time, behind two Rust guards and an explicit approval
queue. Ghoti launches no external agent and every process run requires an
explicit operator approval.

## What is real now

| Capability | Where it lives |
|------------|----------------|
| Local dashboard (localhost only) | `03_scripts/ghoti_product_launcher.py`, `01_projects/dashboard_mvp/` (`http://127.0.0.1:3210`) |
| Agent OS panel (dashboard left-nav) | `01_projects/dashboard_mvp/` Agent OS panel |
| Memory/search pointers (path:line) | `03_scripts/agent_os/local_worker.py` `search_memory` over `14_context/compact_memory`, `14_context/obsidian_vault`, `14_context/repo_knowledge/generated`, `docs` |
| Workflow templates (7 workflows) | `03_scripts/agent_os/workflow_templates.py` |
| Handoff generation (copy-paste only) | `14_context/agent_os/handoffs/` |
| Local worker suggestion outputs | `03_scripts/agent_os/local_worker.py` |
| Rust guard 1: ownership/recipe checks | `rust/ghoti_policy_checker` (`--check`, `--input`, `--ownership-input`) |
| Rust guard 2: approved-action validation | `rust/agent_os_guard` (`validate ... --json`, `guard_version agent_os_guard/0.4.0`) |
| Approval queue (inspectable JSON state) | `03_scripts/agent_os/approval_queue.py`, `14_context/agent_os/approval_queue/{pending,approved,rejected,executed,failed}/` |
| Approved bounded artifact writing | `03_scripts/agent_os/approved_executor.py` (text/JSON only, 4 allowlisted actions, 2 repo-local roots) |
| Swarm coordinator (planning-only, one-worker-lock) | `03_scripts/agent_os/swarm_coordinator.py` (plans multiple workers; queues at most ONE step at a time through the approval queue; no parallel launch) |
| Full local demo | `ghoti_agent_os.py --full-demo` |
| Full approved demo | `ghoti_agent_os.py --full-approved-demo` |
| Sandboxed repo-summary worker | `ghoti_agent_os.py --full-worker-demo` |
| Deterministic summary/classification worker | `ghoti_agent_os.py --full-local-model-worker-demo` |
| Full swarm planning demo | `ghoti_agent_os.py --full-swarm-planning-demo` |
| Run records and evidence | `14_context/agent_os/runs/`, `14_context/agent_os/evidence/` |

The bounded executor writes only under `14_context/agent_os/` and
`14_context/operator_reports/generated/`, only the four allowlisted actions
(`write_handoff_file`, `write_workflow_plan`, `write_evidence_note`,
`update_latest_state_note`), plus the separately guarded `run_local_worker`
action. It refuses content with secret markers or absolute
Windows paths, and uses no subprocess or network of its own. Every run record
asserts `live_execution=false`, `network_used=false`, `browser_used=false`,
`account_action=false`, and `shell_command_executed=false`.

## What is still blocked

| Blocked capability | Why it is blocked |
|--------------------|-------------------|
| Browser control and computer-use | No control path is built or wired |
| Mouse and keyboard input | No input path is built or wired |
| Account access | No credentials path is approvable |
| Email sending | Draft-only; no send path |
| Posting to any channel | Draft-only; no publish path |
| Purchases, payments, trading, money movement | Never approvable |
| Telegram live actions | Status-doc only; no live action path |
| n8n live wiring | Not wired |
| Real multi-agent swarms | Simulation/planning only |
| External (out-of-repo) writes | Refused by the executor and guard |
| Model-output-as-command loops | No command surface accepts model output |

## Exact commands

Dashboard (localhost only):

```powershell
python 03_scripts/ghoti_product_launcher.py --start-dashboard --open-dashboard
python 03_scripts/ghoti_product_launcher.py --agent-os-status --json
```

Full local demo and full approved demo:

```powershell
python 03_scripts/agent_os/ghoti_agent_os.py --full-demo --json
python 03_scripts/agent_os/ghoti_agent_os.py --full-approved-demo --json
python 03_scripts/agent_os/ghoti_agent_os.py --full-worker-demo --json
python 03_scripts/agent_os/ghoti_agent_os.py --full-local-model-worker-demo --json
```

Swarm coordinator (planning-only, one-worker-lock):

```powershell
python 03_scripts/agent_os/ghoti_agent_os.py --plan-swarm coding-task-swarm-plan --json
python 03_scripts/agent_os/ghoti_agent_os.py --list-swarm-plans --json
python 03_scripts/agent_os/ghoti_agent_os.py --queue-next-swarm-step <plan_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --swarm-status --json
python 03_scripts/agent_os/ghoti_agent_os.py --full-swarm-planning-demo --json
```

Approval flow:

```powershell
python 03_scripts/agent_os/ghoti_agent_os.py --propose-action coding-task --json
python 03_scripts/agent_os/ghoti_agent_os.py --list-approvals --json
python 03_scripts/agent_os/ghoti_agent_os.py --approval-status --json
python 03_scripts/agent_os/ghoti_agent_os.py --approve-action <request_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --reject-action <request_id> --json
python 03_scripts/agent_os/ghoti_agent_os.py --execute-approved <request_id> --json
```

Rust guards:

```powershell
cargo run --release --bin agent_os_guard -- validate --request 14_context/agent_os/contracts/action_request.schema.example.json --repo-root . --json
cargo run --release --bin ghoti_policy_checker -- --check
cargo run --release --bin ghoti_policy_checker -- --ownership-input <wave.json>
```

## Next real step

The next big target is approved local model routing (cheap local drafts behind
the output guard), then a browser/computer-use observation harness (observation
only, zero control paths). Building on those, the first sandboxed local agent
process runner uses the Rust guard plus approval queue to run exactly ONE
allowlisted local worker process, with a timeout, a kill path, capped logs,
repo-local IO, and a full trace. It is the first time Ghoti launches a process,
it stays bounded to one approved allowlisted worker at a time, and it unlocks
nothing in the blocked table above. The swarm coordinator is the planning-only
control plane that will feed that runner one approved step at a time.

## Related docs

- Overview: `docs/GHOTI_AGENT_OS_OVERVIEW.md`
- Approved execution substrate: `docs/GHOTI_APPROVED_EXECUTION_SUBSTRATE.md`
- Swarm coordinator: `docs/GHOTI_APPROVED_WORKER_SWARM_COORDINATOR.md`
- Roadmap: `docs/GHOTI_ROADMAP_TO_FULL_COMPUTER_USE.md`

## Environment note

Windows Defender Controlled Folder Access blocks Python writes under
`Documents`; run write-heavy validation from a scratch worktree under
`%LOCALAPPDATA%/Temp`.
