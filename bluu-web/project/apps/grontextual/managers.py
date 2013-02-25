from django.db import models
from django.contrib.contenttypes.models import ContentType

from guardian.exceptions import ObjectNotPersisted


class UserObjectGroupManager(models.Manager):

    def assign(self, group, user, obj):
        """
        Assigns ``group`` for an instance ``obj`` and ``user``.
        """
        if getattr(obj, 'pk', None) is None:
            raise ObjectNotPersisted("Object %s needs to be persisted first"
                % obj)
        ctype = ContentType.objects.get_for_model(obj)

        obj_access, created = self.get_or_create(
            content_type = ctype,
            group = group,
            object_pk = obj.pk,
            user = user)
        return obj_access

    def remove_access(self, group, user, obj):
        """
        Removes permission ``group`` for an instance ``obj`` and given ``user``.
        """
        if getattr(obj, 'pk', None) is None:
            raise ObjectNotPersisted("Object %s needs to be persisted first"
                % obj)
        self.filter(
            group=group,
            user=user,
            object_pk=obj.pk,
            content_type=ContentType.objects.get_for_model(obj))\
            .delete()

    def remove_all_accesses(self, user, obj):
        """
        Removes all groups for an instance ``obj`` and given ``user``.
        """
        if getattr(obj, 'pk', None) is None:
            raise ObjectNotPersisted("Object %s needs to be persisted first"
                % obj)
        self.filter(
            user=user,
            object_pk=obj.pk,
            content_type=ContentType.objects.get_for_model(obj))\
            .delete()


    def get_for_object(self, user, obj):
        if getattr(obj, 'pk', None) is None:
            raise ObjectNotPersisted("Object %s needs to be persisted first"
                % obj)
        ctype = ContentType.objects.get_for_model(obj)
        groups = self.filter(
            content_type = ctype,
            user = user,
            object_pk = obj.pk
        )
        return groups


