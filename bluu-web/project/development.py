
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

# CELERY
from celery.schedules import crontab
djcelery.setup_loader()

BROKER_URL = 'redis://localhost:6379/0'

CELERY_IMPORTS = ('bluusites.tasks', 'companies.tasks') 
CELERYBEAT_SCHEDULE = {
    'cleanup_siteacess': {
        'task': 'bluusites.tasks.cleanup_siteaccess',
        'schedule': crontab(hour='*', minute='*/1'),
    },
    'cleanup_companyaacess': {
        'task': 'companies.tasks.cleanup_companyaccess',
        'schedule': crontab(hour='*', minute='*/1'),
    },
}

EMAIL_ROOT = os.path.join(os.path.dirname(__file__), 'emails')
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = EMAIL_ROOT
