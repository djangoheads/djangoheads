# import random
# import string
# import time
# from argparse import ArgumentParser
# from typing import Any, Dict, Optional, Tuple, cast
#
# from django.conf import settings
# from django.core.management import call_command
# from django.core.management.base import BaseCommand
# from django.db import connections, transaction
# from django.db.backends.utils import CursorWrapper
#
#
# class Command(BaseCommand):
#     """
#     Waiter for system checks before starting the main process.
#
#     Checks the availability of project's services dependencies.
#     """
#
#     __default_attempts = 10
#     __default_timeout = 5
#
#     help = (  # noqa: A003
#         "Waiter for system checks before starting the main process. "
#         "Checks the availability of project's services dependencies."
#     )
#
#     def add_arguments(self, parser: ArgumentParser) -> None:
#         """Add arguments to command."""
#         parser.add_argument(
#             "-n",
#             action="store",
#             type=int,
#             default=self.__default_attempts,
#             required=False,
#             help=f"Attempts count (default {self.__default_attempts})",
#         )
#         parser.add_argument(
#             "-t",
#             action="store",
#             type=int,
#             default=self.__default_timeout,
#             help=f"Timeout in seconds between attempts (default {self.__default_timeout})",
#             required=False,
#         )
#
#     def handle(self, *args: Tuple[Any, ...], **options: Dict[str, Any]) -> None:  # noqa: ARG002
#         """Command implementation."""
#         attempts = cast(int, options.get("n", self.__default_attempts))
#         timeout = cast(int, options.get("t", self.__default_timeout))
#
#         for _ in range(attempts):
#             for check_func in (
#                 self.check_db_availability,
#                 self.check_db_can_write,
#                 self.check_migrations_are_applied,
#             ):
#                 check_result = check_func()
#                 if not check_result:
#                     break
#
#             if check_result:
#                 break
#
#             time.sleep(timeout)
#
#     def check_db_availability(self) -> bool:
#         """Check databases availability."""
#         message = "DB AVAILABILITY [{}]"
#         all_ok = True
#         for alias in settings.DATABASES:
#             try:
#                 with connections[alias].cursor() as cursor:  # type: CursorWrapper
#                     cursor.execute("SELECT 1")
#                 self._print_check(message.format(alias), True)
#                 return True
#             except Exception as e:
#                 self._print_check(message.format(alias), exception=e)
#                 all_ok = False
#                 break
#         return all_ok
#
#     def check_db_can_write(self) -> bool:
#         """Check databases write."""
#         message = "DB CAN WRITE [{}]"
#         all_ok = True
#         for alias in settings.DATABASES:
#             try:
#                 with connections[alias].cursor() as cursor:  # type: CursorWrapper
#                     self._create_random_table(cursor)
#                 self._print_check(message.format(alias), True)
#                 return True
#             except Exception as e:
#                 self._print_check(message.format(alias), exception=e)
#                 all_ok = False
#                 break
#         return all_ok
#
#     def check_migrations_are_applied(self) -> bool:
#         """Check migrations."""
#         try:
#             call_command("migrate", "--check", no_input=True)
#             self._print_check("MIGRATIONS ARE APPLIED", True)
#             return True
#         except SystemExit:
#             self._print_check("MIGRATIONS ARE APPLIED", False)
#             return False
#         except Exception as e:
#             self._print_check("MIGRATIONS ARE APPLIED", False, exception=e)
#             return False
#
#     @transaction.atomic
#     def _create_random_table(self, cursor: CursorWrapper) -> None:
#         """Wite SQL commands by transaction."""
#         random_hash = "".join(random.choice(string.hexdigits + string.digits) for _ in range(10))
#         table_name = f"__TEST_TABLE_{random_hash}__"
#         cursor.execute(f"CREATE TABLE {table_name} (id serial PRIMARY KEY, num integer);")
#         cursor.execute(f"INSERT INTO {table_name} (num) VALUES (1);")
#         cursor.execute(f"UPDATE {table_name} SET num = 2 WHERE id = 1;")
#         cursor.execute(f"DELETE FROM {table_name} WHERE id = 1;")
#         cursor.execute(f"DROP TABLE {table_name};")
#
#     def _print_check(
#         self,
#         label: str,
#         success: Optional[bool] = True,
#         *,
#         width: int = 64,
#         exception: Optional[Exception] = None,
#     ) -> None:
#         """
#         Log a message with a label and a status indicator.
#
#         Args:
#         ----
#             label: A message label.
#             success: A status indicator. Defaults to True. If None, the status indicator is SKIPPED.
#             width: A width of the message. Defaults to 80.
#             exception: An exception instance. Defaults to None.
#
#         Returns:
#         -------
#             None
#         """
#         status_indicator = "SKIPPED" if success is None else ("OK" if success else "FAILED")
#         if isinstance(exception, Exception):
#             status_indicator = "FAILED"
#
#         spacers = width - len(label) - len(status_indicator)
#         msg = f"{label}{'.' * spacers}{status_indicator}"
#         self.stdout.write(msg)
#
#         if isinstance(exception, Exception):
#             self.stdout.write(f"\n{exception.__class__.__name__}: {exception}" + "\n" * 5)
