from django.conf import settings
from django.db import connections
from django.db.backends.utils import CursorWrapper  # noqa

from .check__base import CheckBase, DbInfoMixin


class DbWriteCheck(CheckBase, DbInfoMixin):
    """Check database write availability."""

    message_template = "DB CAN WRITE [{}]"

    def check(self) -> bool:
        """Check method implementation."""
        try:
            test_table_name = f"__test_{self._get_random_hexstr()}__"
            for alias in settings.DATABASES:
                self.message = self.message_template.format(alias)
                self.extra_info = self._get_database_extra_info(alias)
                with connections[alias].cursor() as cursor:  # type: CursorWrapper
                    cursor.execute(f"CREATE TABLE {test_table_name} (id serial PRIMARY KEY, num integer);")
                    cursor.execute(f"INSERT INTO {test_table_name} (num) VALUES (1);")
                    cursor.execute(f"UPDATE {test_table_name} SET num = 2 WHERE id = 1;")
                    cursor.execute(f"DELETE FROM {test_table_name} WHERE id = 1;")
                    cursor.execute(f"DROP TABLE {test_table_name};")
                    self._print_check(self.message)
            return True
        except Exception as exc:
            self._print_check(self.message, exception=exc, exta_info=self.extra_info)
        return False
