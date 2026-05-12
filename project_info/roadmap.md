# Subby — Roadmap

> Indicative phasing. Dates intentionally omitted; sequence is the load-bearing part.

## Phase 0 — Foundations
- Auth (venue operator + customer, separate roles).
- Multi-tenant data model (venue → users → bookings → orders → loyalty entries).
- Stripe Connect onboarding for payouts.
- Basic admin dashboard skeleton.

## Phase 1 — Menu + QR ordering
- Menu CRUD.
- Per-table QR.
- Order placement (no payment yet — sends ticket to operator view).
- Operator order-management screen.

## Phase 2 — Payments
- Stripe payment intents wired to orders.
- Tip + service-charge configuration.
- Refunds.
- Basic revenue report.

## Phase 3 — Bookings
- Booking page, shift/table configuration.
- Deposit support (Stripe pre-auth).
- Confirmation email + SMS reminder.
- Link booking to eventual order/payment.

## Phase 4 — Loyalty (stamp mode)
- Auto-stamp on payment.
- Customer wallet page.
- Operator redemption screen.

## Phase 5 — Multi-site + analytics
- Group/parent-venue model.
- Cross-site reporting.
- Cohort retention reports.

## Phase 6 — Marketplace / extras (speculative)
- Additional payment providers (SumUp, Adyen).
- Points-mode loyalty.
- Inventory/stock module.
- POS hardware integrations (Star/Epson printer support).

## Explicit non-goals
- Building a delivery network.
- Custom POS hardware.
- Becoming a payment processor (always sit on top of providers).
