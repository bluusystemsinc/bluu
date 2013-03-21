
from project.settings import *
DEBUG = True
TEMPLATE_DEBUG = DEBUG

COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'bluu',                      # Or path to database file if using sqlite3.
        'USER': 'django',                      # Not used with sqlite3.
        'PASSWORD': 'django',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }

}

# celery
INSTALLED_APPS.append('kombu.transport.django')
BROKER_URL = 'django://'
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'clean-up-perms': {
        'task': 'bluusites.tasks.clean',
        'schedule': crontab(hour=7, minute=30, day_of_week=1),
        'args': (16, 16),
    },
}

EMAIL_ROOT = os.path.join(os.path.dirname(__file__), 'emails')
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = EMAIL_ROOT
