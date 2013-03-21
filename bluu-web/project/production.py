from project.settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

EMAIL_HOST='smtp.emailsrvr.com'
EMAIL_HOST_USER='noreply@bluusystems.com'
EMAIL_HOST_PASSWORD='set this in local_settings.py'
DEFAULT_FROM_EMAIL='noreply@bluusystems.com'

ALLOWED_HOSTS=['198.61.203.159']


# celery
INSTALLED_APPS.append('kombu.transport.django')
BROKER_URL = 'django://'

try:
    from local_settings import *
except ImportError:
    pass
