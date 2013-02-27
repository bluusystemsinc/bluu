from project.settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

MANAGERS = (
    ('Jakub Wisniowski', 'jwisniowski@milosolutions.com'),
)

EMAIL_HOST='smtp.emailsrvr.com'
EMAIL_HOST_USER='noreply@bluusystems.com'
EMAIL_HOST_PASSWORD='set this in local_settings.py'
DEFAULT_FROM_EMAIL='noreply@bluusystems.com'

try:
    from local_settings import *
except ImportError:
    pass
