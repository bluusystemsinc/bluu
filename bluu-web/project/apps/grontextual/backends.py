from django.contrib.auth.backends import ModelBackend
from django.contrib.contenttypes.models import ContentType
from .models import UserObjectGroup


def get_uog_permissions(user_obj, obj=None):
    """Return User Object Group mapped perms"""
    ctype = ContentType.objects.get_for_model(obj)
    groups = UserObjectGroup.objects.filter(
                        content_type=ctype,
                        user=user_obj,
                        object_pk=obj.pk)
    perms = set()
    for group in groups:
        perms.update(set(['%s.%s' % (p.content_type.app_label, p.codename)\
                          for p in group.group.permissions.all()]))
    return perms
 

class UserObjectGroupBackend(ModelBackend):

   
    def get_all_permissions(self, user_obj, obj=None):
        if user_obj.is_anonymous():
            return set()

        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = set(["%s.%s" % (p.content_type.app_label,\
                        p.codename) for p in \
                            user_obj.user_permissions.select_related()])
            user_obj._perm_cache.update(self.get_group_permissions(user_obj))
            if obj is not None:
                user_obj._perm_cache.update(\
                            get_uog_permissions(user_obj, obj))
        return user_obj._perm_cache

