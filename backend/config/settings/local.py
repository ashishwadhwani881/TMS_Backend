from .base import *

DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = 'django-insecure-xcqm_an7kf6f=%zr3ytnpsgya*rlvu&ygb289!o7z^a(3)db=y'

# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",   
    "https://task-ui.company.com",  
]

CORS_ALLOW_HEADERS = [
    "authorization",
    "content-type",
    "x-requested-with",
]

# -------------------------------------------------
# Database
# -------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "taskmanager_db",
        "USER": "postgres",
        "PASSWORD": "ashish123",
        "HOST": "localhost",
        "PORT": "5432",
    }
}