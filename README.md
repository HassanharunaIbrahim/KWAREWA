# KWAREWA

![Tests](https://github.com/HassanharunaIbrahim/KWAREWA/actions/workflows/tests.yml/badge.svg)

KWAREWA is a classifieds marketplace for Nigeria. Sellers and workers publish services (electricians, mechanics, tailors and more) and goods (phones, laptops, furniture and more), and buyers search by state, category and price, then contact the seller.

**Live test version:** https://engineeer.pythonanywhere.com (a feedback version, not yet a public launch)

**Author:** Hassan Haruna Ibrahim, Ahlul-Bayt International University (final-year computer engineering project)

## Features

**Visitors**
- Search and filter by keyword, type (service or product), category, state, area and price range
- Sort by newest, oldest or price; 12 listings per page
- Listing pages with photos, price, location and seller rating
- Seller pages with active listings and reviews
- Installable on a phone home screen as an app, with an offline page

**Registered users**
- Publish, edit, mark as sold or delete own listings, with up to 5 photos each
- Contact details (phone and WhatsApp) are shown to registered users only, to protect sellers from spam
- Rate a seller from 1 to 5 stars, with an optional comment (one rating per seller, editable)
- Save listings to a personal Saved page
- Report a listing, or contact the team with a question or an appeal

**Moderation and safety**
- New and edited listings are reviewed before they become public
- Three open reports from different users hide a listing until a moderator reviews it
- Moderators manage listings, reports, ratings and messages in the admin
- Daily limits per user: 5 new listings, 5 contact messages and 10 ratings
- Users can only edit, delete or close their own listings and photos

## How it works

1. A seller publishes a listing. It is saved as **pending review** and is not public.
2. A moderator approves it in the admin. It becomes **active** and appears in search.
3. If the seller edits an active listing, it returns to pending review. Three open reports also return it to pending.
4. A seller can mark it **closed (sold)**, which removes it from search.

Phone numbers must contain digits only, with the country code and no `+` sign (for example `2348012345678`), so that WhatsApp links work.

## Technology

- Python 3.13 and Django 6.1
- SQLite database; PostgreSQL is supported through the `DATABASE_URL` setting
- Pillow for photo uploads, WhiteNoise for static files, Gunicorn for production
- GitHub Actions runs the test suite on every push and pull request
- Hosted on PythonAnywhere

## Project structure

```
KWAREWA/
├── config/          settings and root URLs
├── accounts/        registration, login, logout
├── marketplace/     listings, photos, reports, ratings, saved listings, messages
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   ├── tests.py
│   ├── templates/marketplace/
│   └── static/marketplace/
├── .github/workflows/tests.yml
├── manage.py
├── requirements.txt
└── .env.example
```

## Running it locally (Windows)

```
git clone https://github.com/HassanharunaIbrahim/KWAREWA.git
cd KWAREWA
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

Set a secret key in `.env`. Generate one with:

```
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

Then:

```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000. Add **Categories** (for example Mechanics, Electricians, Tailors, Phones) in the admin at http://127.0.0.1:8000/admin/, because listings need one.

## Configuration

Settings come from environment variables, or from a local `.env` file that is never committed.

| Variable | Purpose |
|---|---|
| `DJANGO_DEBUG` | `True` for development. Off by default. |
| `DJANGO_SECRET_KEY` | Required when debug is off |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host names |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Trusted site origins, for example `https://yourdomain.com` |
| `DJANGO_SSL_REDIRECT` | Redirect to HTTPS when debug is off |
| `DJANGO_HSTS_SECONDS` | HSTS duration; `0` until HTTPS is confirmed everywhere |
| `DATABASE_URL` | PostgreSQL connection string, instead of SQLite |
| `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP email in production |
| `DEFAULT_FROM_EMAIL` | Sender address for email |

## Tests

```
python manage.py test --settings=config.test_settings
```

The suite has 75 tests. They cover listing workflow and ownership, search and filters, pagination, reports and the automatic hide rule, photos and limits, contact-number privacy, ratings, saved listings, contact and appeals, information pages and the installable app. The same tests run on GitHub for every push and pull request.

Before a release, also run:

```
python manage.py check --deploy
python manage.py makemigrations --check --dry-run
```

## Deployment (PythonAnywhere)

1. Clone the repository, create a virtual environment with Python 3.13, and install `requirements.txt`.
2. Create a server `.env` with a new secret key, `DJANGO_DEBUG=False`, the allowed host, the trusted origin, and `DJANGO_SSL_REDIRECT=False`, because the platform already forces HTTPS.
3. Run `migrate`, `collectstatic --noinput` and `createsuperuser`.
4. In the Web tab, set the virtualenv path, point the WSGI file at `config.settings`, and map `/static/` to `staticfiles` and `/media/` to `media`.
5. To update: `git pull`, `migrate`, `collectstatic --noinput`, then reload the web app.

Back up the database and the `media/` folder regularly, and keep a copy off the server.

## Known limitations

- Free hosting has limited CPU time, so this is a feedback version, not a public launch.
- Password reset by email is not available yet; an administrator resets passwords.
- Locations are chosen by state, with the area entered as text.
- No seller verification and no automatic scam detection.
- Ratings can be removed by moderators, but there is no appeal workflow for sellers yet.

## License

Copyright (c) 2026 Hassan Haruna Ibrahim. All rights reserved.