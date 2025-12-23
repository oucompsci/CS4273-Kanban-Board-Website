from .base import *
import os

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]  # required env var
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# If HTTPS is terminated by a reverse proxy (common in deployment),
# this tells Django to treat requests as secure when the proxy says so.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Security settings (controlled by env so you can enable only when HTTPS is working)
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0"))
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "False") == "True"
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False") == "True"
CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", "False") == "True"

# Optional HSTS extras (enable via env when ready)
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get("SECURE_HSTS_INCLUDE_SUBDOMAINS", "False") == "True"
SECURE_HSTS_PRELOAD = os.environ.get("SECURE_HSTS_PRELOAD", "False") == "True"
