import pytest

# renamed to avoid name conflict with pytest fixtures
from django.conf import settings as django_settings
from django.core.cache import cache as django_cache

from test_django_project.settings import INSTALLED_APPS


def pytest_configure():
    """Configure django settings for tests."""

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
        CELERY_BRORKER_URL="redis://127.0.0.1:6379/1",
        STATIC_URL="/static/",
        MEDIA_URL="/media/",
        MIDDLEWARE_CLASSES=(),
    )


@pytest.fixture
def root_static_dir(tmpdir):
    """Fixture for static root directory."""
    static_dir = tmpdir.mkdir("test_staticfiles")
    django_settings.STATIC_ROOT = static_dir.strpath
    return static_dir


@pytest.fixture
def root_media_dir(tmpdir):
    """Fixture for media root directory."""
    media_dir = tmpdir.mkdir("test_media")
    django_settings.MEDIA_ROOT = media_dir.strpath
    return media_dir


@pytest.fixture
def dj_cache():
    """Fixture for django cache."""
    django_cache.clear()
    yield django_cache
    django_cache.clear()
