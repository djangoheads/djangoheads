import pytest

# renamed to avoid name conflict with pytest fixtures
from django.conf import settings as django_settings
from django.core.cache import cache as django_cache

from tests.__django_settings__ import INSTALLED_APPS

# initialize django settings
django_settings.configure(
    INSTALLED_APPS=INSTALLED_APPS,
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    },
    STATIC_ROOT="/tmp/static/",  # noqa: S108
    STATIC_URL="/static/",
    MEDIA_ROOT="/tmp/media/",  # noqa: S108
    MEDIA_URL="/media/",
    MIDDLEWARE_CLASSES=(),
)


@pytest.fixture
def root_static_dir(tmpdir):
    """Fixture for static root directory."""
    return tmpdir.mkdir("static")


@pytest.fixture
def root_media_dir(tmpdir):
    """Fixture for media root directory."""
    return tmpdir.mkdir("media")


@pytest.fixture(autouse=True)
def dj_settings(root_static_dir, root_media_dir):
    """Fixture for django settings."""
    django_settings.STATIC_ROOT = root_static_dir.strpath
    django_settings.MEDIA_ROOT = root_media_dir.strpath
    return django_settings


@pytest.fixture(autouse=True)
def dj_cache():
    """Fixture for django cache."""
    django_cache.clear()
    yield django_cache
    django_cache.clear()
