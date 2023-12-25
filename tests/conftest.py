import pytest

# renamed to avoid name conflict with pytest fixtures
from django.conf import settings as django_settings
from django.core.cache import cache as django_cache

from tests.__django_settings__ import INSTALLED_APPS


# initialize django settings
def pytest_configure():
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
        STATIC_URL="/static/",
        MEDIA_URL="/media/",
        MIDDLEWARE_CLASSES=(),
    )


@pytest.fixture
def root_static_dir(tmpdir, settings):
    """Fixture for static root directory."""
    static_dir = tmpdir.mkdir("test_staticfiles")
    settings.STATIC_ROOT = static_dir.strpath
    return static_dir


@pytest.fixture
def root_media_dir(tmpdir, settings):
    """Fixture for media root directory."""
    media_dir = tmpdir.mkdir("test_media")
    settings.MEDIA_ROOT = media_dir.strpath
    return media_dir


@pytest.fixture(autouse=True)
def dj_cache():
    """Fixture for django cache."""
    django_cache.clear()
    yield django_cache
    django_cache.clear()
