from .settings import *  # noqa: F401,F403

# Fast password hashing for tests only. Never use this in production.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]