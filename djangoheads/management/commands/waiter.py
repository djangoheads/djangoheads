import sys
import time
from argparse import ArgumentParser
from collections import deque
from typing import TYPE_CHECKING, Any, Deque, Dict, Tuple, cast

from django.core.management.base import BaseCommand

from .waiter_checks.check_caches import CachesAvailableCheck
from .waiter_checks.check_celery import CeleryBrokerAvailableCheck
from .waiter_checks.check_db_available import DbAvailableCheck
from .waiter_checks.check_migrate import MigrateCheck

if TYPE_CHECKING:
    from .waiter_checks.check__base import CheckBase


class Command(BaseCommand):
    """Waiter for system checks before starting the main process.

    Checks the availability of project's services dependencies.
    """

    help = (  # noqa: A003
        "Waiter for system checks before starting the main process. "
        "Checks the availability of project's services dependencies."
    )

    def __init__(self) -> None:
        super().__init__()
        self._checks_queue: Deque[CheckBase] = deque()
        self._attempts = 6
        self._timeout = 10

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

    def register_checks(self) -> None:
        """Register checks."""
        self._checks_queue.extend((
            DbAvailableCheck(self.stdout),
            # TODO: returns write check to queue later
            # DbWriteCheck(self.stdout),
            MigrateCheck(self.stdout),
            CachesAvailableCheck(self.stdout),
            CeleryBrokerAvailableCheck(self.stdout),
        ))

    def handle(self, *args: Tuple[Any, ...], **options: Dict[str, Any]) -> None:  # noqa: ARG002
        """Command implementation."""
        self._attempts = cast(int, options.get("n", self._attempts))
        self._timeout = cast(int, options.get("t", self._timeout))

        self.register_checks()
        while self._checks_queue and self._attempts > 0:
            checker = self._checks_queue.popleft()
            if not checker.check():
                self._checks_queue.appendleft(checker)
                self._attempts -= 1
                if self._attempts > 0:
                    time.sleep(self._timeout)
                    continue
                sys.exit(1)
