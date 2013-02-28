from project.settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

EMAIL_HOST='smtp.emailsrvr.com'
EMAIL_HOST_USER='noreply@bluusystems.com'
EMAIL_HOST_PASSWORD='set this in local_settings.py'
DEFAULT_FROM_EMAIL='noreply@bluusystems.com'

COMPRESS_ENABLED = True

ALLOWED_HOSTS=['test.web.bluusystems.com', '198.61.203.159']

try:
    from local_settings import *
except ImportError:
    pass
