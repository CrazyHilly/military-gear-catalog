from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("neondb"),
        "USER": os.environ.get("neondb_owner"),
        "PASSWORD": os.environ.get("npg_ZoqeX53UNGac"),
        "HOST": os.environ.get("ep-frosty-sound-a21a4um5-pooler.eu-central-1.aws.neon.tech"),
        "PORT": "5432",
    }
}
