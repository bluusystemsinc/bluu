from celery import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

from bluusites.misc import cleanup_siteaccess as cleanup_task


@task()
def cleanup_siteaccess():
    cleanup_task()
    logger.info('Cleanup siteaccess task called')

