from celery import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

from companies.misc import cleanup_companyaccess as cleanup_task


@task()
def cleanup_companyaccess():
    cleanup_task()
    logger.info('Cleanup companyaccess task called')

