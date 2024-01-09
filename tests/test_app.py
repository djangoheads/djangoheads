from django.apps import apps

from djangoheads.apps import DjangoheadsConfig


def test_app_loading(settings) -> None:
    """Tests the app has been loaded."""
    assert "djangoheads" in settings.INSTALLED_APPS
    app_config = apps.get_app_config("djangoheads")
    assert isinstance(app_config, DjangoheadsConfig)
