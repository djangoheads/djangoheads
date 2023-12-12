import hashlib
import random

import django
from django.conf import settings

from tests.__django_settings__ import INSTALLED_APPS

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=INSTALLED_APPS,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
                "TEST": {
                    "NAME": ":memory:",
                    "SERIALIZE": False,
                    "MIRROR": None,
                },
            }
        },
        STATIC_ROOT="/tmp/static/",  # noqa: S108
        STATIC_URL="/static/",
        SECRET_KEY=hashlib.md5(str(random.random()).encode()).hexdigest(),  # noqa: S324, S311
    )

    django.setup()
