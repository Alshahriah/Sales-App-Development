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

Auth is cookie-based (`authenticated=true`, `username`). `app.py:check_authentication` redirects all paths except `/login`, `/token`, `/signup` to `/login?next=...`.

| Router | Method + Path | Description |
|---|---|---|
| dashboard | `GET /` | Totals, averages, profit, status counts, sales by region/supplier, monthly sales + order counts, top-5 products |
| auth | `GET/POST /login` | Redis `HGET users <username>` password check, writes `UserLog`, sets cookies, redirects to `next` (default `/admin`) |
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
   # also needed but missing from requirements.txt:
   pip install python-dotenv redis sqlalchemy-sqlitecloud
   ```
2. Configure (see Security section — currently hardcoded):
   - SQLite Cloud URL, Redis host/port/username/password, session `secret_key`.
3. Run:
   ```bash
   uvicorn app:app --reload
   # open http://127.0.0.1:8000/ -> redirects to /login
   ```
4. Seed auth user in Redis (auth expects `users` hash):
   ```
   HSET users <username> <password>
   ```

No tests, Dockerfile, or CI are included.

## Security / TODO Before Production

- **Leaked secrets in repo:** `database.py` hardcodes a SQLite Cloud URL + API key; `routers/auth.py` hardcodes Redis host/password; `app.py` uses `SessionMiddleware(secret_key="secret")`. Move all to `.env` (already gitignored) + `os.getenv`, rotate the exposed keys.
- `requirements.txt` is missing `python-dotenv` (imported in `database.py`) and pins no versions; `redis` dep is unused except in auth.
- Auth is plaintext password compare + unsigned `authenticated` cookie with no logout, hashing, or role checks (admin auth checks are commented out).
- `admin.py` has duplicated `delete`/`restore` handlers; `admin.py` vs `regions.py` duplicate region routes.
- `database.py:init_db()` runs `create_all` on import — fine for dev, use migrations (Alembic) in prod.
- `func.strftime('%Y-%m', ...)` monthly grouping is SQLite-specific; will break on Postgres/MySQL.
