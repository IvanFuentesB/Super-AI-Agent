# N+6.5A Safe Computer-Use Observation Harness

## Verdict

IMPLEMENTED_AND_READY_FOR_PUSH, pending final commit-message check and remote
push verification.

## Branch

- Branch: `feat/ghoti-agent-codex-n6-5a-safe-computer-use-observation-harness`
- Base: `origin/main`
- Starting main hash: `67eb4a51ac8d5de538b39ab9437e994c375838cd`
- Required commit message: `feat(ghoti): add safe computer-use observation harness`

## Start Evidence

The worktree was created from the N+6.4B main state. Required N+6.4A/N+6.4B
evidence was present at start:

- `14_context/ghoti_current_truth.md`
- `14_context/agent_handoff_vault/`
- `docs/HERMES_LOCAL_SETUP_CURRENT_TRUTH.md`
- `docs/GHOTI_SKILLS_AND_AGENT_WORKFLOW.md`
- `14_context/codex_n6_4b_main_merge_gate.md`

Recent base history:

- `67eb4a5 docs(ghoti): record n6.4b main merge gate`
- `1e7762c merge(ghoti): integrate n6.4a Hermes truth and skill workflow`
- `0ad9d16 audit(ghoti): validate clean replacement branch`

## Files Added

- `03_scripts/safe_computer_use_observation_harness.py`
- `14_context/computer_use/fixtures/apple_mac_compare_fixture.json`
- `14_context/computer_use/README_SAFE_OBSERVATION_HARNESS.md`
- `docs/GHOTI_N6_5_SAFE_COMPUTER_USE_OBSERVATION_HARNESS.md`
- `01_projects/runtime_mvp/tests/test_n6_5a_safe_computer_use_observation_harness.py`
- `14_context/codex_n6_5a_safe_computer_use_observation_harness.md`

## CLI

```powershell
python 03_scripts/safe_computer_use_observation_harness.py --fixture 14_context/computer_use/fixtures/apple_mac_compare_fixture.json --json
```

## Sample Safety Summary

```json
{
  "safety_verdict": "OBSERVATION_ONLY_REQUIRES_HUMAN_APPROVAL",
  "required_human_approval": true,
  "allowed_actions_now": ["summarize_fixture", "propose_plan"],
  "safety_flags": {
    "local_only": true,
    "observation_only": true,
    "browser_opened": false,
    "chrome_opened": false,
    "live_site_visited": false,
    "clicked_or_typed": false,
    "live_network_used": false,
    "live_api_used": false
  }
}
```

## Validation

Fresh validation before commit:

- `git diff --check`: PASS
- `python -m unittest discover -s 01_projects/runtime_mvp/tests -p "test_n6_*.py" -v`: 37 OK
- Harness CLI JSON run: PASS
- `python 03_scripts/ghoti_product_launcher.py --status --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --context-pack --json`: PASS
- `python 03_scripts/ghoti_product_launcher.py --repo-map --json`: PASS
- `python 03_scripts/public_repo_security_audit.py --run --json`: 150 checks, 0 failed, 7 warnings, 0 blockers

Generated context-pack and repo-map validation residue was restored before
commit staging.

## Safety Verdict

The harness is local-only and fixture-only. It does not launch a browser, open
Chrome, visit Apple, click, type, scrape live websites, use a network, call live
APIs, handle accounts, add items to a cart, purchase anything, or bypass CAPTCHA
or cookie controls.

## Not Enabled

- Live browser control
- Chrome launch
- Apple live visit
- Click/type computer-use
- Account/login/cart/purchase flows
- CAPTCHA, cookie, bot, or cloak bypass
- Live APIs or provider calls
- Hermes provider setup
- Telegram setup
- Tool execution from fixture output

## Next Milestone

N+6.6A should wrap this local fixture harness into Hermes-safe planning flows
only, still without live browser control or autonomous account actions.
