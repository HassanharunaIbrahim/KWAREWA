# KWAREWA
![Tests](https://github.com/HassanharunaIbrahim/KWAREWA/actions/workflows/tests.yml/badge.svg)
KWAREWA is a local classifieds marketplace for Zaria, Nigeria. People can find skilled workers (electricians, mechanics, tailors and more) and buy or sell goods (phones, laptops, furniture and more), and contact sellers directly by phone call or WhatsApp.

It is a final-semester computer engineering project, built as a website first, with a mobile app planned later. The idea is inspired by Divar, adapted for a local community, with a strong focus on trust and safety.

**Live test version:** https://engineeer.pythonanywhere.com (a test version for feedback, not a public launch)

Built by: `<HASSAN HARUNA IBRAHIM>`, `<AHLUL-BAYT INTERNATIONAL UNIVERSITY>`

## Features

**For visitors**
- Search by keyword, listing type (service or product), category, location and price range
- Sort by newest, oldest or price; 12 listings per page
- Listing detail page with photos, price, contact buttons (Call, WhatsApp) and safety tips
- Public seller page (username, member since, active listings; no private data)
- Marketplace rules, privacy notice and help pages

**For sellers (registered users)**
- Register, log in, log out
- Publish a listing with a photo; edit, mark as sold, or delete it
- "My listings" page showing the review status of each listing
- Contact and appeal form to reach the team

**Trust and safety**
- New listings are **pending** until a moderator approves them in the admin
- Editing an approved listing sends it back to **pending**
- Users can report a listing (one report per user per listing, not their own)
- When 3 different users have open reports on a listing, it is hidden automatically (back to pending)
- Moderators see the full report history inside each listing, and can approve, hide, close, review or dismiss in bulk
- Abuse limits per user per 24 hours: 5 new listings and 5 contact messages
- Only the owner can edit, delete or close a listing (others get a 404)
- Phone numbers are validated (digits only, with country code)

## Tech stack

- Python and Django 6.1
- SQLite for development and the current test deployment; PostgreSQL is supported through `DATABASE_URL`
- Pillow for image uploads
- WhiteNoise for static files, Gunicorn for production servers
- Hosted on PythonAnywhere (free plan)

## Project structure

```
KWAREWA/
├── config/         project settings and root URLs
├── accounts/       register, log in, log out
├── marketplace/    listings, reports, contact messages, seller pages
│   ├── models.py   Category, Listing, ListingImage, Report, ContactMessage
│   ├── views.py
│   ├── forms.py
│   ├── admin.py    moderation tools
│   ├── tests.py
│   ├── templates/marketplace/
│   └── static/marketplace/
├── manage.py
├── requirements.txt
└── .env.example
```

## Run it locally (Windows)

```
git clone https://github.com/HassanharunaIbrahim/KWAREWA.git
cd KWAREWA
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and set a secret key. Generate one with:

```
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

Then:

```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000, then http://127.0.0.1:8000/admin/ to add **Categories** (for example Mechanics, Electricians, Tailors, Phones, Laptops). Listings need a category.

## Environment variables

Settings are read from environment variables, or from a local `.env` file that is never committed.

| Variable | Purpose | Example |
|---|---|---|
| `DJANGO_DEBUG` | Development mode. Defaults to off. | `True` |
| `DJANGO_SECRET_KEY` | Required when debug is off | long random text |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host names | `127.0.0.1,localhost` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Production origins | `https://yourdomain.com` |
| `DJANGO_SSL_REDIRECT` | Redirect to HTTPS when debug is off | `True` |
| `DJANGO_HSTS_SECONDS` | HSTS; keep `0` until HTTPS works | `0` |
| `DATABASE_URL` | Use PostgreSQL instead of SQLite | `postgres://user:pass@host:5432/db` |
| `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP email in production | |
| `DEFAULT_FROM_EMAIL` | Sender address | `KWAREWA <noreply@yourdomain.com>` |

## Tests

```
python manage.py test
```

The test suite covers search and filters, pagination, the pending and approval workflow, ownership permissions, the detail and seller pages, reports and the auto-hide rule, mark as sold, the contact form and abuse limits, and the information pages.

Before a release, also run:

```
python manage.py check --deploy
python manage.py makemigrations --check --dry-run
```

## Moderation workflow

1. A user submits a listing, which is created with status **pending**.
2. A moderator opens **Admin, Listings**, filters by *Pending review*, and runs **Approve selected listings**.
3. Visitors can report an approved listing. Three open reports hide it again automatically.
4. A moderator reviews the reports shown inside the listing, then runs **Hide**, **Mark reviewed** or **Dismiss** in **Admin, Reports**. Review the reports before re-approving a listing, otherwise open reports still count.
5. Sellers appeal through the contact form. Messages appear under **Admin, Contact messages**.

## Deployment notes (PythonAnywhere)

1. Clone the repository, create a virtual environment with Python 3.13 and install `requirements.txt`.
2. Create a server `.env` with a **new** secret key, `DJANGO_DEBUG=False`, the allowed host, the CSRF trusted origin and `DJANGO_SSL_REDIRECT=False` (the platform handles HTTPS).
3. Run `python manage.py migrate`, `python manage.py collectstatic --noinput` and `python manage.py createsuperuser`.
4. In the Web tab: set the virtualenv path, edit the WSGI file to load `config.settings`, and map `/static/` to `staticfiles` and `/media/` to `media`.
5. Updating: `git pull`, `python manage.py migrate`, `python manage.py collectstatic --noinput`, then reload the web app.

Back up `db.sqlite3` and the `media/` folder regularly, and keep a copy off the server.

## Known limitations

- Free-tier hosting has limited CPU time, so this is a test deployment, not a public launch.
- Password reset by email is not available yet; forgotten passwords are handled by an administrator.
- Sellers can add photos to a listing but cannot yet remove them.
- No seller verification and no automatic scam detection.

## Roadmap

- Photo management (remove and reorder)
- Password reset by email
- Seller verification badge
- IP-based rate limiting
- Automated tests on every push (GitHub Actions)
- REST API and a mobile app

## License

`<Copyright (c) 2026 hassanharunaibrahim. All rights reserved. "All rights reserved">`
