# Subby — Tech Stack (proposed)

> These are working defaults, not final decisions. Each line should be revisited as the team forms an opinion.

## Frontend
- **Framework:** Next.js (App Router) — server components for SEO on public menu/booking pages, client components for the operator dashboard.
- **Styling:** Tailwind CSS + a small component library (shadcn/ui).
- **Forms:** React Hook Form + Zod.

## Backend / API
- **Runtime:** Node.js (TypeScript end-to-end with the frontend) OR a Python FastAPI backend if the team leans Python.
- **API style:** REST + per-resource RPC for write-heavy flows (e.g., `POST /bookings/{id}/confirm`).
- **Auth:** Email-link + OAuth providers for operators; passwordless OTP for diners.

## Data
- **Primary DB:** Postgres (Supabase or self-managed).
- **Cache / queues:** Redis for rate limits and short-lived booking holds.
- **Object storage:** S3-compatible (Cloudflare R2 / Supabase Storage) for menu images.

## Payments
- **Primary:** Stripe (PaymentIntents, Connect for venue payouts).
- **Future:** SumUp (UK card-present), Adyen (multi-country).

## Notifications
- **Email:** Resend or Postmark.
- **SMS:** Twilio (booking reminders only — keep cost predictable).

## Infrastructure
- **Hosting:** Vercel for frontend; Fly.io or Railway for stateful workers.
- **CI:** GitHub Actions.
- **Observability:** Sentry + a lightweight logs/metrics stack (Logtail/Better Stack to start).

## Open questions
- Single Next.js monorepo vs. split frontend/backend repos.
- Build the booking engine in-house vs. integrate an existing one (ResDiary, SevenRooms) and own only the loyalty/payment glue.
- How much of the POS surface (printer, receipt) to attempt before v2.
