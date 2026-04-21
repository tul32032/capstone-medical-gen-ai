import os
from pathlib import Path

import django
import pytest
from django.core.management import call_command
from django.test import Client


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "betesbot.test_settings")
os.environ["DEBUG"] = "1"


def pytest_configure():
    django.setup()
    call_command("migrate", interactive=False, verbosity=0)


def pytest_sessionfinish(session, exitstatus):
    from django.conf import settings

    db_name = settings.DATABASES["default"]["NAME"]
    db_path = Path(db_name)
    if db_path.exists():
        db_path.unlink()


@pytest.fixture(autouse=True)
def reset_database():
    call_command("flush", interactive=False, verbosity=0)


@pytest.fixture
def client():
    return Client()
