import random
import string
import sys
import time
from argparse import ArgumentParser
from collections import deque
from typing import Any, Callable, Deque, Dict, Optional, Tuple, cast

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.backends.utils import CursorWrapper  # noqa


class Command(BaseCommand):
    """Waiter for system checks before starting the main process.

    Checks the availability of project's services dependencies.
    """

    def __init__(self) -> None:
        super().__init__()
        self._attempts = 6
        self._timeout = 10
        self._check_funcs: Deque[Callable[..., bool]] = deque()

    help = (  # noqa: A003
        "Waiter for system checks before starting the main process. "
        "Checks the availability of project's services dependencies."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add arguments to command."""
        parser.add_argument(
            "-n",
            action="store",
            type=int,
            default=self._attempts,
            required=False,
            help=f"Attempts count (default {self._attempts})",
        )
        parser.add_argument(
            "-t",
            action="store",
            type=int,
            default=self._timeout,
            help=f"Timeout in seconds between attempts (default {self._timeout})",
            required=False,
        )

    def handle(self, *args: Tuple[Any, ...], **options: Dict[str, Any]) -> None:  # noqa: ARG002
        """Command implementation."""
        self._attempts = cast(int, options.get("n", self._attempts))
        self._timeout = cast(int, options.get("t", self._timeout))

        self._check_funcs.append(self.check_db_read)
        self._check_funcs.append(self.check_db_write)
        self._check_funcs.append(self.check_migrations_are_applied)

        while self._check_funcs and self._attempts > 0:
            check_func = self._check_funcs.popleft()
            if not check_func():
                self._check_funcs.append(check_func)
                self._attempts -= 1
                if self._attempts > 0:
                    time.sleep(self._timeout)
                    continue
                sys.exit(1)

    def check_db_read(self) -> bool:
        """Check database read availability."""
        message_read = "DB AVAILABILITY [{}]"
        message = ""
        try:
            for alias in settings.DATABASES:
                with connections[alias].cursor() as cursor:  # type: CursorWrapper
                    message = message_read.format(alias)
                    cursor.execute("SELECT 1")
                    self._print_check(message)
            return True
        except Exception as exc:
            self._print_check(message, exception=exc)
        return False

    def check_db_write(self) -> bool:
        """Check databases availability."""
        message_write = "DB CAN WRITE [{}]"
        message = ""
        try:
            random_hash = "".join(random.choice(string.hexdigits + string.digits) for _ in range(8))
            test_table_name = f"__TEST_{random_hash}__".upper()
            for alias in settings.DATABASES:
                with connections[alias].cursor() as cursor:  # type: CursorWrapper
                    message = message_write.format(alias)
                    cursor.execute(f"CREATE TABLE {test_table_name} (id serial PRIMARY KEY, num integer);")
                    cursor.execute(f"INSERT INTO {test_table_name} (num) VALUES (1);")
                    cursor.execute(f"UPDATE {test_table_name} SET num = 2 WHERE id = 1;")
                    cursor.execute(f"DELETE FROM {test_table_name} WHERE id = 1;")
                    cursor.execute(f"DROP TABLE {test_table_name};")
                    self._print_check(message)
            return True
        except Exception as e:
            self._print_check(message, exception=e)
        return False

    def check_migrations_are_applied(self) -> bool:
        """Check migrations."""
        try:
            call_command("migrate", "--check", no_input=True)
            self._print_check("MIGRATIONS ARE APPLIED")
            return True
        except SystemExit:
            self._print_check("MIGRATIONS ARE APPLIED", False)
        except Exception as e:
            self._print_check("MIGRATIONS ARE APPLIED", exception=e)
        return False

    def _print_check(
        self,
        label: str,
        success: Optional[bool] = True,
        *,
        width: int = 64,
        exception: Optional[Exception] = None,
    ) -> None:
        """Log a message with a label and a status indicator.

        Args:
        ----
            label: A message label.
            success: A status indicator. Defaults to True. If None, the status indicator is SKIPPED.
            width: A width of the message. Defaults to 80.
            exception: An exception instance. Defaults to None.

        Returns:
        -------
            None
        """
        status_indicator = "SKIPPED" if success is None else ("OK" if success else "FAILED")
        if isinstance(exception, Exception):
            status_indicator = "FAILED"

        spacers = width - len(label) - len(status_indicator)
        msg = f"{label}{'.' * spacers}{status_indicator}"
        self.stdout.write(msg)

        if isinstance(exception, Exception):
            self.stdout.write(f"\n{exception.__class__.__name__}: {exception}" + "\n" * 5)
