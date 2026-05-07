# N+3.39 Supabase API And Security Notes

Status: Codex engineering/security notes only.
Date: 2026-05-05

These notes preserve API/security basics for future app/business/product work.

## Supabase RLS Baseline

- Row Level Security must be enabled for user-owned or tenant-owned tables.
- Every table with user data needs clear policies for select, insert, update, and delete.
- Policies should be tested with real user roles, not only with admin/service role.
- Do not trust client data.
- Validate authentication and authorization on every server-side mutation.
- Keep storage bucket policies as strict as table policies.

## Supabase Key Rules

- Never leak the `service_role` key.
- The `service_role` key bypasses RLS and must stay server-side only.
- Use the anon/publishable key client-side.
- Do not put service keys in browser code, mobile apps, desktop apps, public docs, URLs, logs, screenshots, or chat.
- Do not commit keys to Git.
- API keys must go in `.env` or the approved deployment secret store.
- `.env` files must stay ignored.

## Server-Side Rules

- Service-role clients belong only in trusted server code, jobs, or admin tooling.
- Server code must implement its own authorization checks before using elevated keys.
- Do not mix user-session clients with service-role clients.
- Do not let client-provided IDs decide tenancy without checking ownership.

## APILAYER Notes

- APILAYER can be useful for quick MVPs that need commodity APIs.
- Free APIs still need rate-limit, reliability, license, privacy, and cost review.
- Do not hardcode APILAYER keys.
- Log API usage per experiment if it costs credits or money.
- Define a spending cap before paid API use.

## Logging And Rate Limiting

Future public apps should include:

- request logging without secrets
- rate limiting where useful
- abuse detection for public endpoints
- validation errors that do not reveal internals
- audit logs for money-facing or account-facing actions

## Deployment Gate

No public deployment without:

- RLS review
- secret scan
- dependency review
- auth/authorization test
- rate-limit review
- code review
- security review
- rollback plan

Code review and security review skills should become a standard gate before release, but only after the skills themselves are source-audited.
