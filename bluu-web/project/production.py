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

CELERY_IMPORTS = ('bluusites.tasks', 'companies.tasks', 'alerts.tasks')
CELERYBEAT_SCHEDULE = {
    'cleanup_siteacess': {
        'task': 'bluusites.tasks.cleanup_siteaccess',
        'schedule': crontab(hour='*', minute='*/1'),
    },
    'cleanup_companyaccess': {
        'task': 'companies.tasks.cleanup_companyaccess',
        'schedule': crontab(hour='*', minute='*/1'),
    },
    'cleanup_alert_runners': {
        'task': 'alerts.clean_runners',
        'schedule': crontab(hour='0', minute='0'),
    },
    'cleanup_system_alert_runners': {
        'task': 'alerts.clean_system_runners',
        'schedule': crontab(hour='0', minute='0'),
    },
    'trigger_runners': {
        'task': 'alerts.trigger_runners',
        'schedule': crontab(hour='*', minute='*/1'),
    },
    'trigger_system_runners': {
        'task': 'alerts.trigger_system_runners',
        'schedule': crontab(hour='*', minute='*/1'),
    },
    'trigger_motion_in_room_checks': {
        'task': 'alerts.trigger_motion_in_room_checks',
        'schedule': crontab(hour='*', minute='*/30'),
    },
}

try:
    from local_settings import *
except ImportError:
    pass
