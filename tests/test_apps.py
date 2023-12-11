from unittest import TestCase

import django
from django.apps import apps
from django.conf import settings

from djangoheads.apps import DjangoheadsConfig

if not settings.configured:
    settings.configure(INSTALLED_APPS=["djangoheads"])


class TestDjangoheadsConfig(TestCase):
    """Test our app can be loaded correctly by Django."""

    def setUp(self) -> None:
        django.setup()

    def test_app_loading(self) -> None:
        self.assertIn("djangoheads", settings.INSTALLED_APPS)
        app_config = apps.get_app_config("djangoheads")
        self.assertIsInstance(app_config, DjangoheadsConfig)
