import contextlib
from unittest.mock import patch

import pytest
from django.db import connection

from djangoheads.management.commands.waiter import Command


def test_databases_not_configured_exits(settings):
    """Test for databases not configured exit."""
    settings.DATABASES = {}

    command = Command()
    with patch.object(command.stdout, "write") as mock_write:
        with pytest.raises(SystemExit) as exit_exception:
            command.handle()

        mock_write.assert_called_with("DATABASES ARE NOT CONFIGURED!")
        assert exit_exception.type is SystemExit
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