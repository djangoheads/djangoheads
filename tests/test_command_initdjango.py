import os

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command


@pytest.fixture
def extra_static_dir(tmpdir, settings):
    """Create a temporary directory for static files."""
    extra_dir = tmpdir.mkdir("staticfiles_extra")
    settings.STATICFILES_DIRS = [extra_dir.strpath]
    return extra_dir


@pytest.fixture
def test_file(extra_static_dir):
    """Create a test file in the extra static directory."""
    test_static_file = extra_static_dir.join("testfile.txt")
    test_static_file.write("content")
    return test_static_file


@pytest.mark.django_db
def test_init_django_command(dj_cache, test_file, root_static_dir) -> None:
    """Test the initdjango command."""
    call_command("initdjango")

    assert User.objects.filter(username="admin").exists()

    dj_cache.set("test_key", "test_value")
    assert dj_cache.get("test_key") == "test_value"

    assert os.path.exists(os.path.join(root_static_dir, test_file.basename))
