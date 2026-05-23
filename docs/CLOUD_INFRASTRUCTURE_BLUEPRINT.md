# Cloud Infrastructure Blueprint

Ghoti remains local-first. Cloud is optional and later.

## Recommended Default Stack

- Vercel for frontend/deploy.
- Supabase for Postgres, auth, storage, and backend where practical.
- Stripe for payments only after a dedicated audited payment milestone.
- Resend for email.
- Supabase Auth as the default auth choice for simple projects; Clerk is an
  alternative if the product needs richer hosted auth UI.
- Namecheap domain plus DNS provider.
- PostHog analytics after privacy review.
- Sentry for error monitoring.
- Upstash for queues/cache/rate limiting.
- Pinecone only if vector search needs managed vector DB; otherwise prefer
  local/Supabase pgvector first.
- Azure only as a later enterprise/heavier cloud option unless there is a clear
  project reason.

## Rules

- No paid VPS required now.
- No recurring paid infrastructure without human approval.
- No real credentials in docs or IaC.
- Use placeholders only.
