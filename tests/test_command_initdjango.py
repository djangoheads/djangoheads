import os

from django.core.management import call_command
from django.test import TransactionTestCase

import tests.__setup_django__  # noqa: F401


class InitDjangoCommandTest(TransactionTestCase):
    """Tests for initdjango command."""

    def test_init_django_command(self) -> None:
        os.environ["RUNNING_TESTS"] = "true"

        # import user model
        from django.contrib.auth.models import User

        # Call initdjango command
        call_command("initdjango")

        is_admin_user_exists = User.objects.filter(username="admin").exists()
        self.assertTrue(is_admin_user_exists)
