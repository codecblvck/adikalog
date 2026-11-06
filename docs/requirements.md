# Adikalog requirements

Status: draft 1, written 5 November 2026. Owner: codecblvck.

## 1. Problem

Adikalog is a sales log for a family auto parts shop. The seller records each sale with one or more items, saves it, and gets a receipt that can be sent to the buyer on WhatsApp. Sales are recorded on paper today. The app must let the seller find an old sale later and reissue its receipt.

Only the seller uses the app. The buyer never logs in.

## 2. Goals and non-goals

Goals:

- Record multi-item sales safely. A failed save never leaves a partial sale.
- Never lose a saved sale.
- Work on a weak connection (MTN).
- Ship in one week, with paper as the backup during the trial.

Non-goals for v1:

- Stock tracking, debtors, reports
- Editing or deleting sales
- Offline sync or a fully offline app
- A signup screen or password reset by email

## 3. Features, ranked

Must have:

1. Login with name and a 4 digit PIN
2. Create a multi-item sale, with full rollback on any failure
3. Sale details page
4. Sales history list
5. Deploy to a real host

Should have:
6. Receipt as a PDF file the seller can send to WhatsApp (replaces print CSS)
7. Whole sale discount
8. Search in history by customer name
9. Draft items survive a refresh (localStorage)
10. Today, This week and All filter, with a sales count and total for each day

Cut first, in this order, if behind at the end of day 4:

1. CSV export of sales
2. Search
3. Browser draft

Login, create sale, details, history, receipt PDF and deploy are never cut.

## 4. Data model

users

- id
- name (unique)
- pin_hash
- failed_attempts (default 0)
- locked_until (optional)
- created_at

sales

- id (also the receipt number)
- client_key (unique, created when a new draft starts, stops duplicate saves)
- customer_name (optional, shown as Walk-in when empty)
- discount (whole naira, default 0)
- total (whole naira, set by the server)
- created_by (user id)
- created_at

sale_items

- id
- sale_id
- product_name
- quantity
- selling_price (the amount charged for the whole line, not per unit)

Indexes: sales.created_at, sale_items.sale_id.

## 5. Rules

- quantity is a whole number of 1 or more
- selling_price is a whole number of 1 or more, in naira
- discount is 0 or more and less than the sum of selling prices
- total = sum of selling prices minus discount, always calculated by the server
- a sale has at least one item
- sales cannot be edited or deleted in v1
- any error during save rolls back everything
- the same client_key saves only once
- the browser keeps the client_key in localStorage together with the draft, so a refresh keeps the same key. It is deleted only after a successful save, and a failed save keeps it. If localStorage is blocked, the key lives in page memory and the app still works, without refresh protection
- a PIN is exactly 4 digits, and create-user and reset-pin refuse repeated digits (0000, 1111) and straight runs (1234, 4321)
- 5 wrong PINs lock that account for 15 minutes, and a correct PIN resets the counter. The count and the lock live in the database, so they work across workers

Each rule is enforced twice: Pydantic gives the seller a readable message, and a database CHECK constraint is the last defense.

## 6. Save sale flow

1. The seller adds items in the browser. The list is a draft held in browser memory and localStorage.
2. Save sends one form post with the CSRF token, client_key, customer name, discount and the items as one JSON field.
3. The server checks the session and the CSRF token, then validates with Pydantic.
4. If the client_key already exists, redirect to the existing sale.
5. Inside one transaction: insert the sale, insert every item, calculate the total, commit once.
6. On success: redirect to the sale details page and clear the draft. The receipt opens only from the Share receipt button on that page.
7. On a validation error: show the form again with the message and the same draft. On a system error: roll back, log it, show "nothing was saved, try again".

## 7. Receipt

The server builds a PDF for any saved sale. It shows the shop name, date, sale number, customer, each item with quantity and selling price, subtotal, discount and total.

The seller reaches the receipt screen with the Share receipt button on the sale details page. On a phone, a Share PDF button there sends the PDF file straight to WhatsApp using the browser share feature, with a Download PDF button as the fallback. The same PDF can be opened and printed.

Status: proposed. Confirm the approach on day 5.

## 8. Decision record

| Area | Decision | Why | Rejected |
| --- | --- | --- | --- |
| Process | Short upfront design, then thin vertical slices | Requirements are mostly known, and the owner's feedback will change details | Pure waterfall, full agile |
| Structure | App factory with auth and sales blueprints | Each test gets a fresh app and database | One global app.py |
| Sessions | Flask session, written by hand | Two or three users, and it teaches the layer under Flask-Login | Flask-Login |
| CSRF | CSRFProtect from Flask-WTF, no WTForms | Do not write your own security primitives | Custom tokens |
| Validation | Pydantic with plain HTML forms | Readable errors, one place for rules | WTForms |
| Draft items | Browser memory plus localStorage | No network call per item, survives lost signal | Hidden fields, server session |
| Accounts | CLI commands create-user and reset-pin | No signup attack surface | Signup screen |
| Login | Name plus a 4 digit PIN, hashed, with a lock after 5 wrong tries | The family can remember it, and the attempt limit is what protects it | 6 digit PIN, password |
| Money | Whole naira integers | No float errors | Decimals, floats |
| Line price | Store selling_price per line | Prices are negotiated | quantity times unit price |
| Offline | Level 1 only: draft kept, retry-safe save | Sync costs more than the whole week | Offline recording |
| Database | Postgres | Safer for data that matters, same engine in dev and production | SQLite |
| Data layer | SQLAlchemy with Flask-Migrate | Safe schema changes once real data exists | Raw SQL, create_all |
| Hosting | Free trial: Render free web service plus Neon free Postgres plus own nightly dump. Paid web service when the owner relies on it | Free plans checked on 5 Nov 2026, recheck before deploy | Render free Postgres, Supabase free |
| Backups | Nightly pg_dump kept off the host, restored once as a test | Neon free restore window is only 6 hours | Relying on the host |
| Tests | pytest against a Postgres test database | CHECK constraints and transactions behave like production | SQLite tests |
| Docker | Not in v1, a stretch after deploy | Optional for one Flask app on a managed host | Dockerfile in the week |

## 9. Risks

- The Render free web service sleeps when idle and takes about a minute to wake. Acceptable for the trial only.
- Free database plans have limits. Never put real sales on Render free Postgres or Supabase free.
- A weak MTN connection can cause double taps. The client_key and a disabled Save button cover this.
- One week is tight. The cut order in section 3 decides what drops.
- The owner may go back to paper. Paper stays during the trial, and the question after two weeks is how often it was needed.
- A 4 digit PIN has only 10,000 combinations, so anyone who gets a copy of the database can recover every PIN. The attempt limit only stops guessing through the website. Tell users not to reuse the PIN anywhere else, such as a phone lock or a bank card.
- The attempt limit lets someone lock the owner out for 15 minutes at a time by guessing his name. This is accepted for v1 because the lock is short and he can wait it out.

## 10. Open items

- Shop name and contact line for the receipt
- Confirm the receipt PDF approach on day 5
- Where the nightly backup file is stored
- How the paid web service will be paid for
- Decide each design mismatch in section 11

## 11. Design alignment

Checked on 5 November 2026 against the Adikalog Design canvas (11 screens: mobile login, PIN, new sale, receipt, history and details, plus the desktop versions). The owner decided item 1 (PIN) and item 5 (after save) himself and accepted the other proposals, so all 11 resolutions below are decided.

| # | Area | Design shows | Requirement says | Proposed resolution |
| --- | --- | --- | --- | --- |
| 1 | Login | Name, then a 4 digit PIN on a keypad. The name is remembered on the device | Name and password | Decided: name plus a 4 digit PIN, since the family can remember it. The attempt limit protects it, so it is required: 5 wrong tries lock the account for 15 minutes, using users.failed_attempts and users.locked_until. Refuse trivial PINs. Design adds a locked state |
| 2 | Line price | Price field is per unit. Rows read "2 x 1,200". Details has a Unit price column | selling_price is the amount for the whole line | Label the field "Selling price for all units". Show quantity and the line amount. Drop the Unit price column |
| 3 | Discount | No discount field and no subtotal anywhere | Discount on every sale | Add a Discount field above Total on New sale. Show Subtotal, Discount and Total on details and receipt |
| 4 | Receipt actions | Send on WhatsApp and Copy receipt text on the receipt. Print receipt and Export PDF on details | A PDF file shared to WhatsApp | Decided: details has one Share receipt button that opens the receipt screen. The receipt screen has Share PDF on WhatsApp and Download PDF. Remove Copy receipt text, Print receipt and Export PDF |
| 5 | After save | Save sale opens the receipt | Redirect to sale details | Decided: keep the requirement. Save sale opens sale details, and Share receipt there opens the receipt. The design changes |
| 6 | Search | Customer name only | Customer name and item name | Decided: customer name only for v1. The requirement changes |
| 7 | Extra features | Today, This week and All filter. Daily totals in history | Not listed, reports are a non-goal | Decided: keep both, now listed under Should have in section 3 |
| 8 | Receipt number | No. 0001 on the receipt, #001 elsewhere | Sale id | Use one format everywhere, such as four digits padded |
| 9 | Missing states | No validation error, empty list, saving, failed save, or sign out | Save flow in section 6 | Design: validation message that keeps the draft, "nothing was saved, try again", Save disabled while saving, empty history, a sign out control |
| 10 | Fonts | Space Grotesk and DM Mono loaded from Google Fonts | Light pages on weak MTN | Self host both as woff2 files in app/static/fonts |
| 11 | Time | Times like 18:40 | Not stated | Store created_at in UTC and show Africa/Lagos time (UTC+1, no daylight saving) |

What already matches: customer is optional and shows as Walk-in, whole naira with the naira sign, items list with remove before saving, one Grand total, details with product and quantity counts, history search and a New sale button, the desktop split layout, and a receipt with shop name, date, customer, items and total.

Design tokens to put in the Tailwind config:

- ground #f2efe9, ink #1a1a18, accent #b93d0e, slate #4a5d6b
- card border #d8d2c6, input border #918a7b, divider #e6e0d4, muted text #6b6660, white #ffffff
- fonts: Space Grotesk 400, 500, 700 and DM Mono 400, 500

## 12. Folder structure (app factory)

```text
adikalog/
  app/
    __init__.py          create_app(config_name) builds and returns the app
    config.py            Development, Testing and Production settings from env vars
    extensions.py        db, migrate and csrf objects, created without an app
    models.py            User, Sale, SaleItem
    schemas.py           Pydantic models: LoginIn, SaleItemIn, SaleIn
    auth/
      __init__.py        auth blueprint
      routes.py          sign in, sign out
      decorators.py      login_required
      cli.py             create-user and reset-pin commands
    sales/
      __init__.py        sales blueprint
      routes.py          new sale, history, details, receipt, CSV export
      service.py         create_sale, list and search sales, totals
      receipt_pdf.py     builds the receipt PDF for one sale
    templates/
      base.html
      auth/
      sales/
      errors/
    static/
      css/               compiled Tailwind file, committed to the repo
      js/                new_sale.js (draft list, localStorage, share button)
      fonts/             self hosted woff2 files
  migrations/            Flask-Migrate files, one per schema change
  tests/
    conftest.py          app, client and clean database fixtures
    test_auth.py
    test_create_sale.py
    test_history.py
    test_receipt.py
    test_migrations.py
  scripts/
    backup.sh            pg_dump to a file
  .github/workflows/
    ci.yml               runs pytest on every push
    backup.yml           nightly pg_dump
  docs/
    requirements.md
    plan.md
  tailwind.config.js     design tokens from section 11
  src/input.css          Tailwind entry file
  wsgi.py                gunicorn entry point
  requirements.txt       pinned runtime libraries
  requirements-dev.txt   pytest and ruff
  .env.example           names of env vars, no values
  .gitignore
  README.md
```

Why this shape:

- One blueprint per area (auth, sales). Each has routes.py for HTTP and, for sales, service.py for the logic, so tests call create_sale directly without a request.
- No repository classes, no extra layers. The first version of the inventory app was over-engineered, and this one stays small.
- extensions.py holds the objects without an app, which avoids circular imports and lets each test build its own app.

## 13. Stack and libraries

| Layer | Choice | Notes |
| --- | --- | --- |
| Language | Python (the version in your WSL, 3.11 or newer) | Pin it on the host |
| Web framework | Flask with an app factory | Blueprints for auth and sales |
| Database | PostgreSQL | Local in WSL for development |
| ORM | SQLAlchemy 2.x through Flask-SQLAlchemy | CHECK constraints in the models |
| Driver | psycopg 3 | URL form postgresql+psycopg:// |
| Migrations | Flask-Migrate (Alembic) | Read every generated file |
| Validation | Pydantic v2 | Plain HTML forms, items as one JSON field |
| CSRF | Flask-WTF CSRFProtect only | No WTForms |
| Hashing | Werkzeug generate_password_hash | Comes with Flask |
| Sessions | Flask session | Hand written login glue |
| Receipt PDF | ReportLab (proposed) | Pure Python, no system libraries. Confirm on day 5 |
| Templates | Jinja2 | Comes with Flask |
| Styling | Tailwind CSS, standalone CLI | Output file committed, so the host needs no build step |
| Front end code | Plain JavaScript | Draft list, localStorage, Web Share API with download fallback |
| Production server | gunicorn | Start command on the host |
| Env files | python-dotenv | Local development only |
| Tests | pytest with the Flask test client | Postgres test database |
| Lint and format | ruff | Already in your editor setup |
| CI and backups | GitHub Actions | Postgres service container for tests, scheduled pg_dump |

Left out on purpose: Flask-Login, WTForms, Docker for v1, Redis, Celery, any JavaScript framework.

## 14. Hosting and environments

| Environment | Where | Notes |
| --- | --- | --- |
| Development | WSL, local Postgres, adikalog_dev database | flask run |
| Testing | WSL, local Postgres, adikalog_test database | Built from migrations on each run |
| CI | GitHub Actions with a Postgres service container | Runs on every push |
| Trial | Render free web service plus Neon free Postgres | Paper stays the main record |
| Live | Paid web service on Render or Railway, Neon or a paid Postgres | Move when the owner relies on it |

Environment variables: SECRET_KEY, DATABASE_URL, APP_ENV. Nothing secret is committed. .env.example lists the names only.

Deploy details to settle on day 6:

- Start command: run migrations, then gunicorn, for example flask db upgrade followed by gunicorn wsgi:app. Render may restrict pre-deploy commands to paid plans, so check before relying on one.
- Backups: nightly pg_dump through backup.yml, stored away from the host. The storage target is an open item in section 10.
- Account creation: run the CLI once with the production DATABASE_URL set only for that command.
- Recheck free plan limits for Render and Neon on the day you deploy.
