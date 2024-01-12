from django.core.management import call_command

from .check__base import CheckBase


class MigrateCheck(CheckBase):
    """Check migrations."""

    message = "MIGRATIONS ARE APPLIED"

    def check(self) -> bool:
        """Check method implementation."""
        try:
            call_command("migrate", "--check", no_input=True)
            self._print_check(self.message)
            return True
        except SystemExit:
            self._print_check(self.message, False)
        except Exception as exc:
            self._print_check(self.message, exception=exc)
        return False
