# Stack Decision

## Default

- Frontend/deploy: Vercel
- Database/auth/storage: Supabase first
- Payments: Stripe after a dedicated audited milestone
- Email: Resend after a dedicated email milestone
- Auth alternative: Clerk if the product needs richer hosted auth UI
- Analytics: PostHog after privacy review
- Errors: Sentry
- Queues/cache/rate limiting: Upstash
- Vector search: local/Supabase pgvector first, Pinecone only if needed
- Enterprise/heavy cloud: Azure later only with a clear reason

## Why

This stack keeps Ghoti local-first while giving future SaaS projects a pragmatic
path that does not require paying for a VPS up front.
