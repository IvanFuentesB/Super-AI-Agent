# Docker / VPS Runtime Roadmap (N+6.10C)

Status: **planning only. Not enabled.** `docker_runtime_enabled` and `vps_runtime_enabled`
default false. This note mirrors `docs/GHOTI_DOCKER_VPS_RUNTIME_ROADMAP.md`.

## Order of operations

1. **Local laptop first** (today) - local-first keeps data on the operator's machine and
   exposes nothing to the internet.
2. **Local Docker later** - for reproducible runs, behind `docker_runtime_enabled`, and
   **Docker Compose only after an audited milestone**. Prefer open-source / self-hosted
   images.
3. **VPS later, when money allows** - a **separate future milestone** behind
   `vps_runtime_enabled`.

## VPS guardrails (future)

- **No exposing a service without authentication and HTTPS.**
- **No public dashboard until privacy readiness** is reviewed; analytics stay off.
- Prefer open-source / self-hosted infrastructure; keep cost small and reversible.

Each step is gated by its own flag, defaults false, and is reversible.
