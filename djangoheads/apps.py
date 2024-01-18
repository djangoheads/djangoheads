from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured


class DjangoheadsConfig(AppConfig):
    """DjangoHeads app config."""

    name = "djangoheads"
    verbose_name = "DjangoHeads Core Library"

    def ready(self):
        self.init_sentry_sdk()

    def init_sentry_sdk(self):
        sentry_dsn = getattr(settings, "SENTRY_DSN", None)
        if not sentry_dsn:
            return

        try:
            import sentry_sdk
        except ImportError:
            raise ImproperlyConfigured("sentry_sdk is not installed but SENTRY_DSN is set")

        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                DjangoIntegration(),
            ],
            traces_sample_rate=getattr(settings, "SENTRY_TRACES_SAMPLE_RATE", 0.1),
            send_default_pii=settings.DEBUG,
            release=getattr(settings, "SENTRY_RELEASE", "service@release-undefined"),
        )
