from __future__ import unicode_literals
from django.db.models import Model
from django.contrib.contenttypes.models import ContentType
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


def get_obj_perms_model(obj, base_cls, generic_cls):
    if isinstance(obj, Model):
        obj = obj.__class__
    ctype = ContentType.objects.get_for_model(obj)
    for name in dir(obj):
        try:
            attr = getattr(obj, name)
        except AttributeError:
            # this might be thrown if field is a FileField
            continue
        if hasattr(attr, 'related'):
            related = attr.related
            model = getattr(related, 'model', None)
            if (model and issubclass(model, base_cls) and
                    model is not generic_cls):
                # if model is generic one it would be returned anyway
                if not model.objects.is_generic():
                    # make sure that content_object's content_type is same as
                    # the one of given obj
                    fk = model._meta.get_field_by_name('content_object')[0]
                    if ctype == ContentType.objects.get_for_model(fk.rel.to):
                        return model
    return generic_cls


def get_user_obj_perms_model(obj):
    """
    Returns model class that connects given ``obj`` and User class.
    """
    from guardian.models import UserObjectPermissionBase
    from guardian.models import UserObjectPermission
    return get_obj_perms_model(obj, UserObjectPermissionBase, UserObjectPermission)


def get_group_obj_perms_model(obj):
    """
    Returns model class that connects given ``obj`` and Group class.
    """
    from guardian.models import GroupObjectPermissionBase
    from guardian.models import GroupObjectPermission
    return get_obj_perms_model(obj, GroupObjectPermissionBase, GroupObjectPermission)