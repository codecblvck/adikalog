# Adikalog one week plan

Rule for the week: scope flexes, the deadline does not. If behind at the end of day 4, drop from the cut list in requirements.md.

## Daily plan

| Day | Work | Done when |
| --- | --- | --- |
| 0 | Review requirements.md and decide each design mismatch in section 11 before any code. Items 1 and 3 change the database, so they cannot wait. Make sure you can explain each decision without notes | Requirements reviewed, section 11 decided |
| 1 | Repo with the folder layout from requirements.md section 12, app factory, config from environment variables, two blueprints, SQLAlchemy models, first migration, test database and a fixture | App starts, migration builds empty tables, one test passes |
| 2 | Login with Flask session, 4 digit PIN with attempt limit, CSRFProtect, create-user and reset-pin commands | Logged out users cannot reach sale pages. A wrong PIN fails. Five wrong PINs lock the account for 15 minutes. A post without a CSRF token is rejected |
| 3 | Create sale: Pydantic models, JSON field, one transaction, client_key. Write the tests first | Rollback test passes. Repeated save with the same client_key makes one sale. Server ignores any total sent by the browser |
| 4 | Sale details, history list with the Today, This week and All filter and daily totals, discount, search by customer name | Search finds by customer name. Daily totals match the sales listed |
| 5 | Port the design to templates with the changes decided in section 11, Tailwind built to a small CSS file with the design tokens, self hosted fonts, receipt PDF opened from Share receipt on the details page, with Share and Download | Every screen works on a phone. The receipt PDF opens in WhatsApp |
| 6 | Browser draft, CSV export, error pages, GitHub Actions running pytest, test deploy to Render with Neon | Live URL works on mobile data |
| 7 | Nightly pg_dump job, restore test, create the owner's account, sit with him for his first real sale | He records one sale. Paper stays as backup |

## Tests to write before or with the code

Day 3 is the most important:

- empty item list rejected
- quantity 0 or negative rejected
- selling_price 0 or negative rejected
- discount equal to or above the subtotal rejected
- total comes from the server, not the browser
- a failure on the second item leaves no sale and no items in the database
- the same client_key twice creates one sale
- a second post with a used client_key redirects to the existing sale and does not insert anything

Day 2:

- every sale route redirects when logged out
- POST without a CSRF token fails
- the fifth wrong PIN locks the account, and a correct PIN during the lock is still refused
- a correct PIN after the lock expires works and resets the counter
- create-user rejects 0000, 1111, 1234 and 4321

Day 1:

- building an empty database from all migrations matches the models

## Deploy checklist, days 6 and 7

- SECRET_KEY and DATABASE_URL set as environment variables, nothing secret in the repo
- Session cookie set to Secure, HttpOnly and SameSite=Lax in production
- HTTPS only
- Migrations run on deploy
- A health route
- Create the owner account with the CLI, using the production URL passed once as an environment variable and kept out of shell history
- Nightly backup works and one restore has been tested
- Recheck the free plan limits of Render and Neon before deploying

## Trial rules

- Paper stays the main record for the first two weeks.
- After two weeks ask one question: how many days did you fall back to paper?
- If paper was needed most days, design offline recording from that evidence.
- When he relies on the app, move the web service to a paid plan so it stops sleeping.

## Stretch, only after day 7

- Dockerfile for the app
- Whole sale void flag instead of delete
- Debtors
- Offline recording
