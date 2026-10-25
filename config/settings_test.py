"""
Settings for database-backed tests:

    python manage.py test leave.tests_integration --settings=config.settings_test

The project's migrations assume tables that schema.sql / ensure_db_schema already created
(many models are `managed = False`), so they cannot run on an empty test database.  For tests we
skip migrations and let the test case create the tables straight from the models.
"""
from .settings import *  # noqa: F401,F403


class _DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = _DisableMigrations()
TESTS_WITHOUT_MIGRATIONS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
