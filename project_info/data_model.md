# Subby — Data Model (sketch)

> Indicative shape, not a migration spec. Resource names will evolve.

## Core entities

### `venue`
- `id` (uuid)
- `name`, `slug`, `timezone`, `currency`
- `address`, `phone`, `cover_image_url`
- `stripe_account_id` (Connect)
- `created_at`, `updated_at`

### `user`
- `id`
- `email`, `phone`
- `role`: `owner` | `manager` | `server` | `diner`
- `venue_id` (nullable — diners have none)

### `menu`
- `id`, `venue_id`, `name`, `is_published`

### `menu_section`
- `id`, `menu_id`, `name`, `position`

### `menu_item`
- `id`, `section_id`, `name`, `description`, `price_cents`, `currency`
- `is_available`, `image_url`
- `dietary_tags` (`["vegan", "gluten_free", ...]`)
- `allergens` (`["nuts", "dairy", ...]`)

### `menu_item_modifier`
- `id`, `menu_item_id`, `name`, `price_delta_cents`, `is_required`

### `table`
- `id`, `venue_id`, `label`, `capacity`, `qr_token`

### `booking`
- `id`, `venue_id`, `diner_id` (nullable), `party_size`
- `starts_at`, `ends_at`, `status`: `pending|confirmed|seated|completed|no_show|cancelled`
- `deposit_payment_intent_id` (nullable)
- `notes`

### `tab`
- `id`, `venue_id`, `table_id`, `opened_at`, `closed_at`, `status`

### `order`
- `id`, `tab_id`, `placed_at`, `placed_by_user_id` (nullable)
- `subtotal_cents`, `tip_cents`, `service_charge_cents`, `total_cents`
- `payment_intent_id`, `payment_status`

### `order_line`
- `id`, `order_id`, `menu_item_id`, `quantity`, `unit_price_cents`, `modifiers_json`

### `loyalty_program`
- `id`, `venue_id`, `mode`: `stamp` | `points`
- `stamps_required` (for stamp mode)
- `points_per_currency_unit` (for points mode)
- `reward_description`

### `loyalty_entry`
- `id`, `program_id`, `diner_id`, `stamps_delta`, `points_delta`, `order_id` (nullable), `created_at`

### `redemption`
- `id`, `program_id`, `diner_id`, `redeemed_at`, `order_id`

## Cross-cutting
- Soft-delete via `deleted_at` on user-facing resources.
- Audit log table for any change to `menu_item.price_cents` and `booking.status`.
- All currency stored in minor units (cents/pence) as integers.
