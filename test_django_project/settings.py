# It is used in `mypy.ini` and tests.
# The following installed apps are required for stubtest to run correctly.
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.flatpages",
    "django.contrib.redirects",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "djangoheads",
]
# The following url is required for Celery to run tests correctly.
CELERY_BROKER_URL = "redis://127.0.0.1:48765/1"
