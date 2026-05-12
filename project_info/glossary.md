# Subby — Glossary

- **Venue** — A single physical location (a pub, café, restaurant). The primary tenant unit.
- **Group** — An optional parent of multiple venues, used by small chains. Not present in v1.
- **Operator** — Staff user of the dashboard. Has a role (owner, manager, server).
- **Diner** — End customer who scans a QR, books a table, or earns a stamp. May or may not have an account.
- **Menu** — A versioned collection of sections and items for a venue.
- **Section** — A named group on the menu (e.g., "Starters", "Cocktails").
- **Item** — A single purchasable line on a menu. Has a price, optional modifiers, and dietary tags.
- **Modifier** — Add-on or option on an item (e.g., "extra shot", "no onions"). Can be priced or free.
- **Tab** — An open order against a table that may have multiple rounds before payment.
- **Order** — A confirmed set of items, optionally with a tab reference.
- **Booking** — A reservation against a date, time, and table assignment.
- **Shift** — A configured service window (e.g., "Friday Dinner") with capacity rules.
- **Stamp** — One unit of loyalty progress, typically issued automatically on payment.
- **Redemption** — A loyalty reward being used (e.g., free drink claimed once 10 stamps reached).
- **Provider** — A third-party payment processor (Stripe, SumUp, Adyen).
- **GPV** — Gross Payment Volume. Total payment value processed through Subby in a period.
