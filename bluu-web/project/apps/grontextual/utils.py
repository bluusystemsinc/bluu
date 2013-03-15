import logging
logger = logging.getLogger(__name__)


def clean_orphan_obj_perms():
    """
    Seeks and removes all object permissions entries pointing at non-existing
    targets.

    Returns number of removed objects.
    """
    from grontextual.models import UserObjectGroup

    deleted = 0
    # TODO: optimise
    for uog in UserObjectGroup.objects.all():
        if uog.content_object is None:
            logger.debug("Removing %s (pk=%d)" % (uog, uog.pk))
            uog.delete()
            deleted += 1
    logger.info("Total removed orphan object permissions instances: %d" %
        deleted)
    return deleted

