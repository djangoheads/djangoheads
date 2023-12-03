from unittest import TestCase

from djangoheads.apps import (
    AppConfig,
    DjangoheadsConfig,
)


class TestDjangoheadsConfig(TestCase):
    """Test the DjangoheadsConfig class."""

    def test_subclass(self) -> None:
        self.assertTrue(issubclass(DjangoheadsConfig, AppConfig))

    def test_name(self) -> None:
        self.assertTrue(hasattr(DjangoheadsConfig, "name"))
        self.assertIsInstance(DjangoheadsConfig.name, str)
        self.assertEqual(DjangoheadsConfig.name, "djangoheads")

    def test_verbose_name(self) -> None:
        self.assertTrue(hasattr(DjangoheadsConfig, "verbose_name"))
        self.assertIsInstance(DjangoheadsConfig.verbose_name, str)
        self.assertEqual(DjangoheadsConfig.verbose_name, "Django Heads")
