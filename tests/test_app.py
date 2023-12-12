from django.apps import apps
from django.conf import settings
from django.test import TestCase

import tests.__setup_django__  # noqa: F401
from djangoheads.apps import DjangoheadsConfig


class TestDjangoheadsConfig(TestCase):
    """Tests for DjangoheadsConfig."""

    def test_app_loading(self) -> None:
        """Tests the app has been loaded."""
        self.assertIn("djangoheads", settings.INSTALLED_APPS)
        app_config = apps.get_app_config("djangoheads")
        self.assertIsInstance(app_config, DjangoheadsConfig)
