import random
import sys
import time
from argparse import ArgumentParser
from collections import deque
from typing import Any, Callable, Deque, Dict, Optional, Tuple, cast

from django.conf import settings
from django.core.cache import InvalidCacheBackendError, caches
from django.core.exceptions import ImproperlyConfigured
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
        self._check_funcs.append(self.check_caches)

        while self._check_funcs and self._attempts > 0:
            check_func = self._check_funcs.popleft()
            res = check_func()
            if not res:
                self._check_funcs.appendleft(check_func)
                self._attempts -= 1
                if self._attempts > 0:
                    time.sleep(self._timeout)
                    continue
                sys.exit(1)

    def check_db_read(self) -> bool:
        """Check database read availability."""
        message_read = "DB IS AVAILABLE [{}]"
        extra_info = None
        message = ""
        try:
            for alias in settings.DATABASES:
                message = message_read.format(alias)
                extra_info = self._get_database_extra_info(alias)
                with connections[alias].cursor() as cursor:  # type: CursorWrapper
                    cursor.execute("SELECT 1")
                    self._print_check(message)
            return True
        except ImproperlyConfigured:
            self.stdout.write("DATABASES ARE NOT CONFIGURED!")
            sys.exit(1)
        except Exception as exc:
            self._print_check(message, exception=exc, exta_info=extra_info)
        return False

    def check_db_write(self) -> bool:
        """Check databases availability."""
        message_write = "DB CAN WRITE [{}]"
        extra_info = None
        message = ""
        try:
            test_table_name = f"__test_{self._get_random_hexstr()}__"
            for alias in settings.DATABASES:
                message = message_write.format(alias)
                extra_info = self._get_database_extra_info(alias)
                with connections[alias].cursor() as cursor:  # type: CursorWrapper
                    cursor.execute(f"CREATE TABLE {test_table_name} (id serial PRIMARY KEY, num integer);")
                    cursor.execute(f"INSERT INTO {test_table_name} (num) VALUES (1);")
                    cursor.execute(f"UPDATE {test_table_name} SET num = 2 WHERE id = 1;")
                    cursor.execute(f"DELETE FROM {test_table_name} WHERE id = 1;")
                    cursor.execute(f"DROP TABLE {test_table_name};")
                    self._print_check(message)
            return True
        except Exception as e:
            self._print_check(message, exception=e, exta_info=extra_info)
        return False

    def check_migrations_are_applied(self) -> bool:
        """Check migrations."""
        message = "MIGRATIONS ARE APPLIED"
        try:
            call_command("migrate", "--check", no_input=True)
            self._print_check(message)
            return True
        except SystemExit:
            self._print_check(message, False)
        except Exception as e:
            self._print_check(message, exception=e)
        return False

    def check_caches(self) -> bool:
        """Check caches."""
        message_cache = "CACHE IS AVAILABLE [{}]"
        message = ""
        try:
            for cache_name in settings.CACHES:
                message = message_cache.format(cache_name)
                cache = caches[cache_name]
                test_key = f"__test_{self._get_random_hexstr()}__"
                test_value = "1"
                cache.set(test_key, test_value, timeout=60)
                if cache.get(test_key) != test_value:
                    self._print_check(message, False)
                    break
            else:
                self._print_check(message, True)
                return True
        except InvalidCacheBackendError as exc:
            if isinstance(exc, InvalidCacheBackendError):
                self._print_check("CACHES ARE NOT CONFIGURED", None)
                return True
            self._print_check(message_cache.format(message), False, exception=exc)
        return False

    # def check_celery(self) -> bool:
    #     """Check celery availability."""
    #     if not hasattr(settings, "CELERY_BROKER_URL"):
    #         self._print_check("CELERY IS NOT CONFIGURED", None)
    #         return True
    #
    #     message = "CELERY IS AVAILABLE"
    #     try:
    #         result = subprocess.run(
    #             ("celery", "-A", settings.CELERY_APP_NAME, "inspect", "ping"),
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE,
    #             check=True,
    #         )
    #         if result.returncode == 0:
    #             self._print_check(message)
    #             return True
    #         else:
    #             self._print_check(message, False)
    #             return False
    #     except subprocess.CalledProcessError as e:
    #         self._print_check(message, False, exception=e)
    #         return False
    #     except Exception as e:
    #         self._print_check(message, False, exception=e)
    #         return False

    def _print_check(
        self,
        label: str,
        success: Optional[bool] = True,
        *,
        width: int = 96,
        exta_info: Optional[str] = None,
        exception: Optional[Exception] = None,
    ) -> None:
        """Log a message with a label and a status indicator.

        Args:
        ----
            label: A message label.
            success: A status indicator. Defaults to True. If None, the status indicator is SKIPPED.
            width: A width of the message. Defaults to 80.
            exta_info: Extra info string. Defaults to None.
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

        if exta_info is not None:
            self.stdout.write(exta_info + "\n")

        if isinstance(exception, Exception):
            self.stdout.write(f"{exception.__class__.__name__}: {exception}" + "\n" * 3)

    @staticmethod
    def _get_database_extra_info(alias: str) -> Optional[str]:
        """Get extra info about database by alias.

        Args:
        ----
            alias: A database alias.

        Returns:
        -------
            Extra info about database.
        """
        if alias not in settings.DATABASES:
            return None

        extra_info = f"{settings.DATABASES[alias]['ENGINE']}//"
        extra_info += f"{settings.DATABASES[alias]['USER']}@"
        extra_info += f"{settings.DATABASES[alias]['HOST']}:{settings.DATABASES[alias]['PORT']}"
        extra_info += f"/{settings.DATABASES[alias]['NAME']}"

        return extra_info

    @staticmethod
    def _get_random_hexstr(length: int = 8) -> str:
        """Generate a random hash.

        Args:
        ----
            length: A length of the hash. Defaults to 8.

        Returns:
        -------
            A random hash.
        """
        return "".join(random.choices("0123456789abcdef", k=length))
