import random
from abc import ABCMeta, abstractmethod
from typing import Optional

from django.conf import settings
from django.core.management.base import OutputWrapper


class CheckBase(metaclass=ABCMeta):
    """Waiter check base class."""

    message_template = ""
    message = ""
    extra_info: Optional[str] = None

    def __init__(self, handler_stdout: OutputWrapper) -> None:
        self.stdout: OutputWrapper = handler_stdout

    @abstractmethod
    def check(self) -> bool:
        """Check method implementation."""
        raise NotImplementedError

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


class DbInfoMixin:
    """Database info mixin."""

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
        return (
            (
                f"{settings.DATABASES[alias]['ENGINE']}//"
                f"{settings.DATABASES[alias]['USER']}@"
                f"{settings.DATABASES[alias]['HOST']}:"
                f"{settings.DATABASES[alias]['PORT']}/"
                f"{settings.DATABASES[alias]['NAME']}"
            )
            if alias in settings.DATABASES
            else None
        )
