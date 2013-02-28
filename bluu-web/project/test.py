from project.settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

EMAIL_HOST='smtp.emailsrvr.com'
EMAIL_HOST_USER='noreply@bluusystems.com'
EMAIL_HOST_PASSWORD='set this in local_settings.py'
DEFAULT_FROM_EMAIL='noreply@bluusystems.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/opt/webapps/test/bluu/bluu-web/bluu.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

COMPRESS_ENABLED=True

ALLOWED_HOSTS=['test.web.bluusystems.com', '198.61.203.159']

try:
    from local_settings import *
except ImportError:
    pass
