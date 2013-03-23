from project.settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

EMAIL_HOST='smtp.emailsrvr.com'
EMAIL_HOST_USER='noreply@bluusystems.com'
EMAIL_HOST_PASSWORD='set this in local_settings.py'
DEFAULT_FROM_EMAIL='noreply@bluusystems.com'

ALLOWED_HOSTS=['198.61.203.159']

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

try:
    from local_settings import *
except ImportError:
    pass
