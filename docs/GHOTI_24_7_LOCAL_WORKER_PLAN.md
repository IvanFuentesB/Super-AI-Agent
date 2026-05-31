# Ghoti 24/7 Local Worker Plan (Phase 4, planned - not enabled)

Status: **planned_only**. The 24/7 local worker mode is **planned but not enabled**. No
queue runs, no scheduled job runs, and no daemon runs by this milestone.

## Goal (future)

Let a local **Gemma summary worker** process queue files and produce scheduled summaries,
so routine summarization happens without a cloud model and without live account actions.

## Planned components (all disabled now)

| Component | Planned | Enabled now |
|-----------|---------|-------------|
| Gemma summary worker | yes | `gemma_summary_worker_enabled: false` |
| llama coordinator (model truth) | yes | documented Hermes model, not a 24/7 process |
| Queue files | yes | `queue_enabled: false` |
| Scheduled summaries / jobs | yes | `scheduled_jobs_enabled: false` |
| 24/7 local worker mode | yes | `twenty_four_seven_mode_enabled: false` |

## Safety

The 24/7 local worker mode is planned but **not enabled**. When it is built (Phase 4),
it stays **local-first**: a local Gemma worker over local queue files, with **no live
account actions**, no auto-send, and no external API calls. It is enabled only after a
human approves it.

## Not enabled now

`twenty_four_seven_mode_enabled: false`. `queue_enabled: false`.
`scheduled_jobs_enabled: false`. No scheduler, no daemon, no background account action.
