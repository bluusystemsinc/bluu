# Django settings for project project.

import os
import djcelery

DEBUG = False

ADMINS = (
    ('Admin', 'jwisniowski@milosolutions.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'bluu.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Warsaw'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

ROOT_DIRECTORY = os.path.dirname(__file__)
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(ROOT_DIRECTORY, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(ROOT_DIRECTORY, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'fp!@p5(qne*cft+iw_72a6%u@k0ecoz#@pnoj=i8enwd7wh9r8'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    'django.core.context_processors.tz',
    "django.core.context_processors.request",
    "django.core.context_processors.csrf",
    "django.contrib.messages.context_processors.messages",
)

ROOT_URLCONF = 'project.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #os.path.join(os.path.dirname(__file__), "templates"),
)

INSTALLED_APPS = [
    'theme',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    #'django.contrib.flatpages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'easy_thumbnails',
    'django_extensions',
    'pagination',
    'registration',
    'south',
    'mailer',
    'compressor',
    'crispy_forms',
    'rest_framework',
    'braces',
    'guardian',
    'accounts',
    'companies',
    'bluusites',
    'devices',
    'alerts',
    'utils',
    'grontextual',
    'invitations',
    'dashboard',
    'autoslug',
    'djcelery',
    'rest_framework.authtoken',
]

EMAIL_BACKEND = "mailer.backend.DbBackend"

AUTH_USER_MODEL = 'accounts.BluuUser'

AUTHENTICATION_BACKENDS = (
                           'django.contrib.auth.backends.ModelBackend',
                           'grontextual.backends.UserObjectGroupBackend',
                           #'accounts.auth_backends.EmailAuthBackend',
                           'guardian.backends.ObjectPermissionBackend',
                           )

# django-registration settings
ACCOUNT_ACTIVATION_DAYS = 14
LOGIN_REDIRECT_URL = '/dashboard/'
LOGIN_URL = '/'

# invitations settings
ACCOUNT_INVITATION_DAYS = 14
INVITE_MODE = True

#django-crispy-forms settings
CRISPY_TEMPLATE_PACK = 'bootstrap'
CRISPY_FAIL_SILENTLY = not DEBUG

# Default groups - groups that are assigned to each user
DEFAULT_GROUPS = ['Base User']
# Default company groups - groups that are assigned to each user that belongs to any company
DEFAULT_COMPANY_GROUPS = ['Company Employee']

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
            'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'bluu_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(ROOT_DIRECTORY, 'logs', 'bluu.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 100,  # 100 mb
        },
        'celery_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(ROOT_DIRECTORY, 'logs', 'celeryd_django.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 100,  # 100 mb
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'bluu': {
            'level': 'INFO',
            'handlers': ['bluu_file', 'console'],
            'propagate': False
        },
        'celery': {
            'level': 'DEBUG',
            'handlers': ['mail_admins', 'celery_file'],
            'propagate': False,
        },
    }
}

#django-compress settings
COMPRESS_ENABLED = False
COMPRESS_CACHE_BACKEND = 'locmem:///'

#django-guardian
ANONYMOUS_USER_ID = -1

SOUTH_TESTS_MIGRATE = False

TOS_URL = u'#'

# REST Framework
REST_FRAMEWORK = {
    'FILTER_BACKEND': 'rest_framework.filters.DjangoFilterBackend',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

SOUTH_MIGRATION_MODULES = {
    'guardian': 'ignore',
}

APPEND_SLASH = False
# Session timeout in seconds
SESSION_COOKIE_AGE = 3600


# App specific settings
COMPANY_GROUPS = ['Dealer', 'Technician']
SITE_GROUPS = ['Master User', 'User']
WEBSERVICE_USERNAME_PREFIX = 'controller'

# Algorithms
# gaps in minutes
MOTION_TIME_GAP = 5
SLEEP_TIME_GAP = 15

# duration in minutes
# if someone is in a bed for a time longer than SLEEP_DURATION
# then count is as a sleep
SLEEP_DURATION = 60

try:
    from settings_local import *
except Exception, err:
    import sys
    print >> sys.stderr, "Warning - Unable to import settings_local: %s" % err
