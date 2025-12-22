from .base import *

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]  # required env var

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
