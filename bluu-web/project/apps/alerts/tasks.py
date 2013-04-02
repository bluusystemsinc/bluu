from celery import task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@task()
def alert_longer_than():
    logger.info('Alert longer than task called')

