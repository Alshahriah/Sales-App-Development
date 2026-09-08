# Sales App

A FastAPI-based sales / order management dashboard for tracking Amazon-style orders across regions/suppliers, with CRUD, soft-delete/restore, delivery-status workflow, audit logs, and region analytics. Server-rendered with Jinja2 templates + static CSS/JS.

## Stack

- **Backend:** FastAPI, SQLAlchemy, Pydantic, Uvicorn
- **DB:** SQLite Cloud via `sqlalchemy-sqlitecloud` (`database.py`)
- **Auth store:** Redis Cloud (`routers/auth.py`, Redis hash `users`)
- **Frontend:** Jinja2 (`templates/`), vanilla CSS/JS (`static/`)
- **Other:** `itsdangerous` (sessions), `python-multipart` (forms), `pytz` (IST timestamps)

## Project Structure

```
.
├── app.py              # FastAPI app, router registration, auth middleware, static mount
├── database.py         # Engine/Session/Base, get_db, init_db (create_all on import)
├── requirements.txt
├── models/
│   ├── __init__.py
│   ├── sale.py           # Sale — core order record
│   ├── region.py         # Region (region_name, region_code) 1:N Sales
│   ├── deleted_sale.py   # DeletedSale — soft-delete archive
│   ├── crud_log.py       # CRUDLog — create/update/delete audit
│   ├── user_log.py       # UserLog — login IP / user-agent / UTC + IST time
│   └── update_status.py  # UpdateStatusRequest pydantic schema
├── routers/
│   ├── auth.py         # /login, /success_redirect, /user_logs
│   ├── dashboard.py    # / (metrics dashboard)
│   ├── sales.py        # /create_sale, /edit/{id}, /delete/{id}, /orderdetails/{id}, /update_status/{id}
│   ├── admin.py        # /admin, /admin/view_orders, /admin/deleted_orders, restore, addregion, countries, orders_by_region
│   ├── regions.py      # duplicate of region routes in admin.py (addregion, countries, orders_by_region)
│   ├── logs.py         # /logs (CRUD audit, paginated)
│   └── misc.py         # /url-list, /time
├── templates/          # login, dashboard, admin, create_sale, edit_sale, view_orders,
│                       # order_details, orders_by_region, countries, add_region,
│                       # deleted_orders, logs, user_logs, time, success_redirect
└── static/
    ├── css/  ├── js/  └── images/favicon.ico
```

## Data Models

| Model | Table | Key fields |
|---|---|---|
| `Sale` | `sales` | product_name/description, supplier_name, buyer_name/address, sale_price, buy_price, quantity, amazon_commission, forex_fees, order_datetime, ship_date, sale_date, estimated_delivery/payout_date, delivery_status (`Received/Shipped/Delivered/Returned/Cancelled`), manage/amazon/payment links, `region_id` FK |
| `Region` | `regions` | region_name + region_code (both unique) |
| `DeletedSale` | `deleted_sales` | snapshot of `Sale` + `original_sale_id` |
| `CRUDLog` | `crud_logs` | action, model, record_id, user, details (HTML link), timestamp |
| `UserLog` | `user_logs` | username, ip_address, user_agent, login_time (UTC), india_time (IST string) |

Profit logic in `routers/dashboard.py` (active = not `Returned`/`Cancelled`):
`profit = Σ(sale_price) − (Σ(buy_price) + Σ(sale_price * amazon_commission / 100))`

## Routes

Auth is session-based (`request.session["authenticated"]`). `app.py:check_authentication` redirects all paths except `/login`, `/token`, `/signup`, `/logout`, `/static/*`, `/favicon.ico` to `/login?next=...`.

| Router | Method + Path | Description |
|---|---|---|
| dashboard | `GET /` | Totals, averages, profit, status counts, sales by region/supplier, monthly sales + order counts, top-5 products |
| auth | `GET/POST /login` | Redis `HGET users <username>` password check (PBKDF2 hash, legacy plaintext auto-upgraded), writes `UserLog`, sets server session, redirects to `next` (default `/admin`) |
| auth | `GET /logout` | Clears session, redirects to `/login` |
| auth | `GET /success_redirect`, `GET /user_logs` | Post-login page; login audit list |
| sales | `GET/POST /create_sale` | Create `Sale` + `CRUDLog(CREATE)` |
| sales | `GET/POST /edit/{sale_id}` | Update `Sale` + `CRUDLog(UPDATE)`, redirects to `referrer` or `/admin` |
| sales | `POST /delete/{sale_id}` | Archive to `DeletedSale` + delete + `CRUDLog(DELETE)` |
| sales | `GET /orderdetails/{id}` | Single order view |
| sales | `POST /update_status/{sale_id}` | Update `delivery_status` + log, redirect to `redirect_url` form field |
| admin | `GET /admin?page&per_page` | Paginated order table (default 10/page) |
| admin | `GET /admin/view_orders?...` | Filter/sort/search: `period(days/months/years)+value`, `delivery_status`, `ship_date_start/end`, `payout_date_start/end`, `sale_date_start/end`, `search` (product/buyer ilike), `sort_by` + `sort_order` |
| admin | `GET /admin/deleted_orders?page&page_size` | Paginated deleted archive |
| admin | `GET /admin/restore_order/{sale_id}` | Restore `DeletedSale` → `Sale` |
| admin | `GET /admin/countries` | Regions + per-region order counts |
| admin | `GET/POST /admin/addregion` | Create region (400 if name/code exists) |
| admin | `GET /admin/orders_by_region/{region_id}` | Orders for one region |
| logs | `GET /logs?page&per_page` | `CRUDLog` newest-first, default 20/page |
| misc | `GET /url-list`, `GET /time` | Route dump (JSON), time demo page |

> Note: region/admin delete/restore routes are duplicated in both `routers/admin.py` and `routers/regions.py`, and `delete`/`restore` are defined twice inside `admin.py`. Last-registered router wins — dedupe needed.

## Setup & Run

1. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure:
   ```bash
   cp .env.example .env
   # edit .env: DATABASE_URL, SESSION_SECRET_KEY, REDIS_HOST/PORT/USERNAME/PASSWORD
   # generate a secret: openssl rand -hex 32
   ```
   Set `SESSION_HTTPS_ONLY=true` when serving over HTTPS.
3. Run:
   ```bash
   uvicorn app:app --reload
   # open http://127.0.0.1:8000/ -> redirects to /login
   ```
4. Seed auth user in Redis (passwords are PBKDF2-SHA256 hashes, stdlib only):
   ```bash
   python3 -c "
   import hashlib, secrets
   pw = input('new password: ')
   salt = secrets.token_hex(16)
   dk = hashlib.pbkdf2_hmac('sha256', pw.encode(), bytes.fromhex(salt), 200000)
   print(f'pbkdf2_sha256\$200000\${salt}\${dk.hex()}')
   "
   # then: HSET users <username> <hash above>
   # Legacy plaintext entries still work once and are auto-upgraded to a hash on next login.
   ```

No tests, Dockerfile, or CI are included.

## Security

- Secrets (`DATABASE_URL`, `SESSION_SECRET_KEY`, Redis creds) come from `.env` (gitignored); see `.env.example`. No credentials in code.
- Auth uses server-side sessions (`SessionMiddleware`, `lax` SameSite, optional HTTPS-only) instead of spoofable `authenticated=true` cookies. Generic `invalid_credentials` error, open-redirect guard on `next`, `GET /logout` clears the session.
- Passwords verified with PBKDF2-SHA256 (200k iterations) + `hmac.compare_digest`; legacy plaintext Redis entries are auto-migrated to hashes.
- **You must still rotate** the previously hardcoded SQLite Cloud API key + Redis password — they remain in git history.
- Remaining TODO: `admin.py` duplicated `delete`/`restore` handlers; `admin.py` vs `regions.py` duplicate region routes; `init_db()` runs at startup (use Alembic in prod); `func.strftime('%Y-%m', ...)` is SQLite-specific.
