import os
from typing import Any, Dict, Tuple

from django.contrib.auth.models import User
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    """Init Django command."""

    help = "Init Django (create caches, migrate, create admin user, collect static)."  # noqa: A003

    def handle(self, *args: Tuple[Any, ...], **options: Dict[str, Any]) -> None:  # noqa: ARG002
        """Init Django implementation."""
        call_command("createcachetable")
        call_command("migrate", no_input=True, interactive=False)

        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser("admin", password="admin")  # pragma: allowlist secret # noqa: S106

        call_command("collectstatic", no_input=True, interactive=False)
