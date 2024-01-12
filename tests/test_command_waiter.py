import contextlib
import importlib
import sys
from unittest.mock import patch

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.db import connection, connections

from djangoheads.management.commands.waiter import Command
from djangoheads.management.commands.waiter_checks.check_caches import CachesAvailableCheck
from djangoheads.management.commands.waiter_checks.check_celery import CeleryBrokerAvailableCheck
from djangoheads.management.commands.waiter_checks.check_migrate import MigrateCheck


@pytest.fixture(scope="function")
def waiter_command():
    """Fixture for command."""

    if "djangoheads.management.commands.waiter" in sys.modules:
        importlib.reload(sys.modules["djangoheads.management.commands.waiter"])

    if "test_django_project.celery" in sys.modules:
        importlib.reload(sys.modules["test_django_project.celery"])

    command = Command()
    setattr(command, "_attempts", 2)
    setattr(command, "_timeout", 0)
    return command


@pytest.mark.django_db
def test_databases_not_configured_exits(waiter_command):
    """Test for databases not configured exit."""

    with pytest.raises(SystemExit) as exit_exception:
        with patch.object(connections["default"], "cursor", side_effect=ImproperlyConfigured) as mock:
            waiter_command.handle()
            assert mock.call_count == 1

        assert exit_exception.value.code == 1


@pytest.mark.django_db
def test_handle_with_no_errors(waiter_command):
    """Test for successful command execution."""
    waiter_command.handle()


@pytest.mark.django_db
@patch("djangoheads.management.commands.waiter_checks.check_caches.CachesAvailableCheck.check")
def test_handle_with_errors(db_available_check_mock, waiter_command):
    """Test for failed command execution."""

    db_available_check_mock.return_value = False
    with pytest.raises(SystemExit) as excinfo:
        waiter_command.handle()
        assert excinfo.value.code == 1
    assert db_available_check_mock.call_count == 2


@pytest.mark.django_db
def test_migrations_are_applied_failure(waiter_command):
    """Test for failed migrations check."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 'DROP TABLE ' || name || ';' FROM sqlite_master WHERE type='table';")
        drop_table_commands = cursor.fetchall()
        for (command,) in drop_table_commands:
            with contextlib.suppress(Exception):
                cursor.execute(command)

    assert MigrateCheck(waiter_command.stdout).check() is False


def test_command_arguments(waiter_command):
    """Test for command arguments."""
    parser = waiter_command.create_parser("manage.py", "waiter")
    parsed_args = parser.parse_args(["-n", "5", "-t", "15"])
    assert parsed_args.n == 5
    assert parsed_args.t == 15


@pytest.mark.django_db
def test_cache_configured_and_accessible(waiter_command):
    """Test for cache configured and accessible."""
    assert CachesAvailableCheck(waiter_command.stdout).check() is True


@pytest.mark.django_db
def test_redis_cache_not_available(waiter_command, settings):
    """Test for redis cache not available."""

    settings.CACHES["redis"] = {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.127:66999/111",
    }

    assert CachesAvailableCheck(waiter_command.stdout).check() is False


@pytest.mark.django_db
def test_celery_broker_is_available(waiter_command):
    """Test for celery broker configured and accessible."""
    assert CeleryBrokerAvailableCheck(waiter_command.stdout).check() is True


@pytest.mark.django_db
@patch("djangoheads.management.commands.waiter_checks.check__base.CheckBase._print_check")
def test_celery_broker_isnt_configured(print_check_mock, waiter_command, settings):
    """Test for celery broker not configured."""

    print_check_mock.return_value = None
    if hasattr(settings, "CELERY_BROKER_URL"):
        delattr(settings, "CELERY_BROKER_URL")
    assert CeleryBrokerAvailableCheck(waiter_command.stdout).check() is True
    assert print_check_mock.call_count == 1
    assert print_check_mock.call_args_list[0][0] == ("CELERY IS NOT CONFIGURED", None)


@pytest.mark.django_db
def test_celery_broker_wrong_configured(waiter_command, settings):
    """Test for celery broker not configured."""
    settings.CELERY_BROKER_URL = 1231451252512
    assert CeleryBrokerAvailableCheck(waiter_command.stdout).check() is False


@pytest.mark.django_db
def test_celery_broker_not_available(waiter_command, settings):
    """Test for celery broker not available."""
    settings.CELERY_BROKER_URL = "amqp://guest@guest127.0.0.127:66999//"
    assert CeleryBrokerAvailableCheck(waiter_command.stdout).check() is False
