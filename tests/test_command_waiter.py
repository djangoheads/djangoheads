import pytest
from django.core.management import call_command


@pytest.mark.django_db()
def test_init_django_command() -> None:
    """Test the initdjango command."""
    call_command("waiter", "-n", "1", "-t", "0")
