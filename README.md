# KWAREWA

KWAREWA is a local marketplace for discovering and posting services and classified goods. Browse listings by keyword, category, location, and listing type, or create an account to post and manage your own listings.

## Features

- Browse active service and product listings.
- Search listings by title, description, category, or location, and filter by type.
- Create an account, sign in, and manage your listings.
- Submit listings with contact details, optional pricing, and an optional photo.
- Report inappropriate listings. Listings are hidden for review after they receive multiple reports.
- Administer listings and categories through Django Admin.

## Tech stack

- Python and Django
- Django templates with HTML and CSS
- SQLite by default; a database supplied through `DATABASE_URL` can be used for deployment

## Getting started

### Requirements

- Python compatible with the Django version pinned in `requirements.txt`
- `pip`

### Install and run locally

```bash
git clone https://github.com/HassanharunaIbrahim/KWAREWA.git
cd KWAREWA

python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser. The Django admin is available at <http://127.0.0.1:8000/admin/>.

Before listings can be categorized, add categories in Django Admin. New listings are submitted as pending review; activate approved listings in the admin so they appear publicly.

### Environment variables

KWAREWA reads settings from environment variables and a local `.env` file. `.env.example` documents the available options. For local development, the defaults are configured for SQLite and `127.0.0.1`/`localhost`.

Important settings include:

| Variable | Purpose |
| --- | --- |
| `DJANGO_DEBUG` | Enables or disables Django debug mode. |
| `DJANGO_SECRET_KEY` | Secret key; set a unique, private value outside local development. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of allowed host names. |
| `DATABASE_URL` | Optional database connection URL. If omitted, SQLite is used. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Optional comma-separated HTTPS origins trusted for CSRF. |
| `DJANGO_HSTS_SECONDS` | HSTS duration in production; only increase after HTTPS is working. |
| `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP settings for deployment. |

Never commit your real `.env` file or production secrets.

## Useful commands

```bash
# Run automated tests
python manage.py test

# Check project configuration
python manage.py check

# Collect static files for deployment
python manage.py collectstatic
```

## Deployment notes

For production, set `DJANGO_DEBUG=False`, provide a strong `DJANGO_SECRET_KEY`, configure `DJANGO_ALLOWED_HOSTS`, and supply a production database using `DATABASE_URL`. Configure HTTPS and the appropriate `DJANGO_CSRF_TRUSTED_ORIGINS` before deployment. The repository includes Gunicorn and WhiteNoise for serving the Django application and static assets; a typical application start command is:

```bash
gunicorn config.wsgi:application
```

Uploaded listing images are stored under `MEDIA_ROOT` by default. Configure persistent media storage or an external media service for production, and back up the database and uploaded files.

## Project structure

```text
config/       Django project settings and URL configuration
accounts/     Registration, login, and logout
marketplace/  Listings, categories, images, and reports
manage.py     Django management command entry point
```

## Contributing

Contributions and suggestions are welcome. For substantial changes, open an issue to discuss the proposal before submitting a pull request.
