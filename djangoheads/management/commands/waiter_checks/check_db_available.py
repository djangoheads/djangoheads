import sys

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connections
from django.db.backends.utils import CursorWrapper  # noqa

from .check__base import CheckBase, DbInfoMixin


class DbAvailableCheck(CheckBase, DbInfoMixin):
    """Check database availability."""

    message_template = "DB IS AVAILABLE [{}]"

    def check(self) -> bool:
        """Check method implementation."""
        try:
            for alias in settings.DATABASES:
                self.message = self.message_template.format(alias)
                self.extra_info = self._get_database_extra_info(alias)
                with connections[alias].cursor() as cursor:  # type: CursorWrapper
                    cursor.execute("SELECT 1")
                    self._print_check(self.message)
            return True
        except ImproperlyConfigured:
            self.stdout.write("DATABASES ARE NOT CONFIGURED!")
            sys.exit(1)
        except Exception as exc:
            self._print_check(self.message, exception=exc, exta_info=self.extra_info)
        return False
