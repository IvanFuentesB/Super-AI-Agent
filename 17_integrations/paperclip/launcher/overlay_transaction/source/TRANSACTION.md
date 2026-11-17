# Paperclip overlay transaction contract (helper schema `paperclip_overlay_txn/2`)

Scope: one target checkout T, one accepted package P (read only), one transaction directory X.
T, P and X must be physically disjoint, and X must be on T's volume. Every operation holds the
target lock `T/.git/paperclip-overlay.lock` (an OS byte-range lock, released by the OS when the
holder dies) from its first check to its last write. A lock held by a live process is a refusal,
never stolen.

## Owned components and their exact states
| Component | old (baseline) | new (applied) | owned transient |
|---|---|---|---|
| HEAD | symbolic `branch_ref`, which resolves to BASE | detached at TARGET | — |
| `branch_ref` | BASE | BASE (never moved) | — |
| index entries | = BASE tree | = TARGET tree | — |
| each of the 10 source files | raw = installed preimage (or absent) | raw = expected installed afterimage | absent while moved to `X/rb-src` |
| `ui/dist`, `cli/dist` | exact old manifest | exact new manifest | missing while parked in `X/parked` (old) or `X/rb-out` (new) |
| temp ref `refs/paperclip-overlay/<txn_id>` | absent | absent | = TARGET between fetch and git switch |
| owner marker `T/.git/paperclip-overlay-owner.json` | absent | names this txn | names this txn |
| pinned deployed files | raw pins | raw pins (never touched) | — |

Anything else is foreign: later work, another transaction, or damage. It causes a refusal
(exit 2) or an INCONSISTENT stop (exit 3). In both cases that invocation wrote no transaction state.
The one exception is the empty lock file `T/.git/paperclip-overlay.lock`: opening the lock creates it
once, and it is not transaction state. Every precondition below is checked before the first write;
a failure discovered after a write is exit 1, and `recover` resumes from it.

A transient is accepted only in the phases that can produce it:
- **Missing output:** accepted during the output swap (phase `apply-sources-switched`) or any `rollback-*` phase.
- **Missing pre-existing source:** accepted only in a `rollback-*` phase.
- **Absent owner marker:** accepted only at `apply-begun`, or in a `rollback-*` phase after `X/owner-released.json` names this transaction.
- **Journal says `apply-complete`:** the target must be exactly this transaction's applied state, original branch still at BASE included.

## Journal phases (atomic writes to X/journal.json; phase names are whitelisted, history must end with phase)
Apply: `apply-begun` → `apply-staged` → `apply-fetched` → `apply-sources-switched` → `apply-outputs-switched` → `apply-git-switched` → `apply-complete`
Rollback: `rollback-begun` → `rollback-git-restored` → `rollback-sources-restored` → `rollback-outputs-restored` → `rollback-complete`

Only `apply-begun` and `rollback-begun` are write-ahead intent records. X is created atomically together
with `apply-begun` (built under a hidden sibling name, then renamed). `rollback-begun` is written before
the rollback's first mutation. The other phases are progress records, written after the step they name.
The actual position is always re-derived from T, so a crash between a step and its progress record is
recoverable. A crash after a complete apply but before `apply-complete` is rolled back by `recover`,
as an interrupted apply.

## Transitions
| Command | Journal phase | Actual state of T | Action | Result |
|---|---|---|---|---|
| preflight | — | old | none | READY (0) |
| preflight / apply | — | new, owned by some txn | none | ALREADY_APPLIED (0), no writes |
| apply | — | anything else | none | REJECTED (2), X not created |
| apply | — | old | journal, marker, stage, fetch, sources, outputs, git, verify | APPLIED (0) |
| rollback / recover | apply-* (incomplete) or rollback-* (incomplete) | every component old/new/owned-transient and restorable | write `rollback-begun` if not already, then resume each step idempotently | ROLLED_BACK (0) |
| rollback | apply-complete | new, marker = this txn | same as above | ROLLED_BACK (0) |
| rollback | apply-complete | any component foreign (later edit, moved branch, other owner, foreign ref) | none | REJECTED (2), no writes |
| recover | apply-complete | new, marker = this txn | none | NOTHING_TO_RECOVER (0), state verified |
| recover | apply-complete | not exactly new | none | INCONSISTENT (3) |
| rollback / recover | rollback-complete | old, marker absent | none | ALREADY_ROLLED_BACK (0), state verified |
| rollback / recover | rollback-complete | anything else (e.g. a later apply) | none | REJECTED (2): the target no longer belongs to this txn |
| any | — | a Git lock file present, or a journal identity, phase or history that does not match | none | INCONSISTENT (3) or REJECTED (2) |

Rollback step order (each step skips itself when already done):
1. Git: `symbolic-ref HEAD branch_ref` if HEAD is detached at TARGET (`branch_ref` must still be BASE); `read-tree BASE` if the index is not BASE.
2. Sources: a new file moves to `X/rb-src/`, then the old bytes return from `X/src-old/` by atomic replace (absent-in-base files stay absent).
3. Outputs: a new dir is renamed to `X/rb-out/`, then the parked old dir is renamed back from `X/parked/`.
4. Temp ref deleted only with expected value TARGET; owner marker moved to `X/owner-released.json` only if it names this txn.
5. Verify the exact old state, then `rollback-complete`.

Nothing is deleted. Displaced bytes stay in X as evidence.

## Git execution
- **Inherited environment:** any inherited `GIT_*` variable other than `GIT_PAGER` is refused first, before any other check, as the launcher does.
- **Executable:** `git.exe` is taken from absolute PATH entries only, never the current directory, and must lie outside T, P and X. It must have no link or reparse components. Hardlinks are allowed for this read-only use, as in the reviewed helper.
- **Environment and fixed configuration:** the environment is an allowlist, as in the reviewed helper's `clean_env`/`git_env`, plus:
  - `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=nul`, `GIT_NO_REPLACE_OBJECTS=1`;
  - `core.fsmonitor=false`, `core.untrackedCache=false`;
  - `core.autocrlf=true`, the installed byte convention, stated explicitly because the system config is disabled;
  - `core.hooksPath=nul`, so no hooks run; `gc.auto=0` and `maintenance.auto=false`, so nothing detaches.
- **Repository checks:** the `.git` directory must be the real git dir and the common dir; any `commondir` redirection is refused.
- **Repo config allowlist:**
  - allowed: core.repositoryformatversion, filemode, bare, logallrefupdates, symlinks, ignorecase and autocrlf=true;
  - allowed: `remote.<n>.url`, `remote.<n>.fetch`, `branch.<n>.remote` and `branch.<n>.merge`;
  - anything else is refused.
- **Attributes:** the 10 source paths must have no `filter`, `text`, `eol`, `crlf`, `working-tree-encoding` or `ident` attribute.
- **Stale Git locks:** `index.lock`, `HEAD.lock`, `packed-refs.lock` or any `refs/**.lock` stops the operation with INCONSISTENT before writes.
- **Byte checks:** sources are written by the helper as exact bytes, computed from the TARGET blobs and verified against the package's expected installed hashes before any write. Source backups and afterimages are fsynced. Raw-byte checks stay separate from Git content checks.

## Test hooks
`PAPERCLIP_OVERLAY_TEST_STOP_AT` (exit 75) and `PAPERCLIP_OVERLAY_TEST_PAUSE_AT` (wait for an external kill) are honoured only when the target carries `.git/paperclip-overlay-test-staging`. Fixtures and `stage_baseline.py` create that marker; an installed intake never has it. Any `PAPERCLIP_OVERLAY_TEST_*` variable on an unmarked target is refused before any write.
