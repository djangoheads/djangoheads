import contextlib
from unittest.mock import patch

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.db import connection, connections

from djangoheads.management.commands.waiter import Command


@pytest.mark.django_db
def test_databases_not_configured_exits():
    """Test for databases not configured exit."""

    command = Command()

    with pytest.raises(SystemExit) as exit_exception:
        with patch.object(connections["default"], "cursor", side_effect=ImproperlyConfigured) as mock:
            command.handle()
            assert mock.call_count == 1

        assert exit_exception.value.code == 1


@pytest.mark.django_db
def test_handle_with_no_errors():
    """Test for successful command execution."""
    Command().handle()


@pytest.mark.django_db
def test_handle_with_errors():
    """
    Тестирование поведения команды при ошибках.
    """
    with patch.object(Command, "check_db_read", return_value=False) as mock:
        command = Command()
        setattr(command, "_attempts", 2)
        setattr(command, "_timeout", 0)
        with pytest.raises(SystemExit) as excinfo:
            command.handle()
            assert excinfo.value.code == 1
        assert mock.call_count == 2


@pytest.mark.django_db
def test_migrations_are_applied_failure():
    """Test for failed migrations check."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 'DROP TABLE ' || name || ';' FROM sqlite_master WHERE type='table';")
        drop_table_commands = cursor.fetchall()
        for (command,) in drop_table_commands:
            with contextlib.suppress(Exception):
                cursor.execute(command)
    assert Command().check_migrations_are_applied() is False


def test_command_arguments():
    """Test for command arguments."""
    command = Command()
    parser = command.create_parser("manage.py", "waiter")
    parsed_args = parser.parse_args(["-n", "5", "-t", "15"])
    assert parsed_args.n == 5
    assert parsed_args.t == 15


@pytest.mark.django_db
def test_cache_configured_and_accessible():
    """Test for cache configured and accessible."""
    command = Command()
    assert command.check_caches() is True


@pytest.mark.django_db
def test_redis_cache_not_available():
    """Test for redis cache not available."""

    from django.conf import settings as django_settings  # noqa: PLC0415

    django_settings.CACHES["redis"] = {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:48765/1",
    }

    command = Command()
    assert command.check_caches() is False
