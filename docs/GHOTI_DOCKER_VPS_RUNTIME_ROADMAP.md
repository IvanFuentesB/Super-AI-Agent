# Ghoti Docker / VPS Runtime Roadmap

This is **planning only**. Docker and VPS runtimes are **not enabled** by this milestone,
and the `docker_runtime_enabled` and `vps_runtime_enabled` feature flags default false.
Nothing here is wired up yet.

## Local laptop first

Ghoti runs on the local laptop today. That is deliberate: local-first keeps data on the
operator's machine, costs nothing, and avoids exposing anything to the public internet.
The status bot, the runtime, and the dashboard all run locally.

## Docker later

Containerizing Ghoti is a **future** step, useful for reproducible local runs and for a
clean path to a server later. When it happens:

- Prefer **open-source / self-hosted** images; avoid paid managed services where a free
  local option works.
- **Docker Compose only after an audited milestone.** No compose file becomes part of a
  default "just run everything" flow until it has been reviewed.
- Containers stay local until the VPS milestone; building an image does not expose a port
  to the internet.

## VPS later (when money allows)

A VPS is a **separate future milestone**, taken only **when money allows** and only after
the privacy and safety foundations are in place. When it happens:

- **No exposing a service without authentication and HTTPS.** A public endpoint must sit
  behind auth and TLS; never expose a raw port.
- **No public dashboard until privacy readiness.** The dashboard stays local-only until a
  privacy-readiness review passes; analytics stay off (`dashboard_local_analytics_enabled`
  defaults false).
- Prefer open-source / self-hosted infrastructure; keep the monthly cost small and
  reversible.

## Order of operations

1. Local laptop (today).
2. Local Docker for reproducibility - after an audited milestone, behind
   `docker_runtime_enabled`.
3. VPS deployment - a separate future milestone, behind `vps_runtime_enabled`, with auth +
   HTTPS, only when money allows and privacy readiness is met.

Each step is gated by its own feature flag, defaults false, and is reversible.
