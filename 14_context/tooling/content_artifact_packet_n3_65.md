# Content Artifact Packet Spec — N+3.65

**Milestone:** N+3.65
**Generator:** `03_scripts/supervised_content_mvp_runner.py --run --apply`
**Output dir:** `14_context/content_workflows/runs/<timestamp_slug>/`

---

## Packet Files (12 required)

| File | Purpose |
|------|---------|
| `00_manifest.json` | Safety flags, approval gates, metadata. Machine-readable. |
| `01_input_brief.md` | Brief parameters, safety declaration, scope. |
| `02_llm_council_review.md` | 3-stage LLM Council review (local_demo mode). |
| `03_strategy_decision.md` | Refined angle, key decisions, non-decisions. |
| `04_short_script.md` | Full short-form script with hook, demo, CTA, voiceover draft. |
| `05_scene_shot_list.md` | Scene-by-scene visual plan, shot list, asset rights table. |
| `06_asset_rights_tos_brand_safety.md` | All 5 approval gates + TOS + brand safety check. |
| `07_metadata_pack.md` | Title options, description draft, tags, thumbnail concept, publish params. |
| `08_human_approval_packet.md` | 5 formal gates with signature lines. Human signs before any action. |
| `09_manual_publish_checklist.md` | Pre-production, production, post-production, upload steps for human. |
| `10_obsidian_memory_snapshot.md` | Obsidian-compatible snapshot of this milestone's context. |
| `11_readiness_score.json` | supervised_mvp_slice_score: 100, production_public_release_ready: false. |
| `12_next_iteration_backlog.md` | Prioritized backlog for next iteration. Planning only. |

---

## Approval Gates (all must be pending_human_review before any publish action)

| Gate | Purpose |
|------|---------|
| rights_check | All assets verified as owned/licensed by human |
| brand_safety | No false claims, no harmful content, responsible AI messaging |
| platform_tos | YouTube Shorts TOS + AI disclosure requirements verified |
| final_human_review | Full packet reviewed and approved by human |
| publish_approval | Explicit human authorization to manually publish |

---

## Safety Assertions (encoded in manifest)

```json
{
  "live_posting": false,
  "upload": false,
  "account_login": false,
  "fake_engagement": false,
  "external_api_calls": false,
  "clone_install_run_external_repos": false,
  "human_approval_required": true
}
```

---

## Proof Topic (N+3.65 proof run)

- **Niche:** AI tools for students and creators
- **Idea:** A faceless YouTube Shorts channel testing one AI workflow per short
- **Audience:** students, creators, and solo builders
- **Platform:** YouTube Shorts
- **Goal:** Create a legal manual-publish content experiment packet
- **Script:** "Claude Summarizes My 40-Page Study Guide in 10 Seconds"

---

## Status

Every packet is generated in `pending_human_approval` state.
No packet transitions to any other state automatically.
Human manually clears gates and publishes.
