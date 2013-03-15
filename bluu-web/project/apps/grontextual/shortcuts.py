from __future__ import unicode_literals

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.shortcuts import _get_queryset
from itertools import groupby

from guardian.compat import get_user_model
from guardian.compat import basestring
from guardian.core import ObjectPermissionChecker
from guardian.exceptions import MixedContentTypeError
from guardian.exceptions import WrongAppError
from guardian.utils import get_identity
from guardian.utils import get_user_obj_perms_model
from guardian.utils import get_group_obj_perms_model
import warnings
from .models import UserObjectGroup


def get_objects_for_user(user, perms, klass=None, use_groups=True, any_perm=False):
    """
    Returns queryset of objects for which a given ``user`` has *all*
    permissions present at ``perms``.

    :param user: ``User`` instance for which objects would be returned
    :param perms: single permission string, or sequence of permission strings 
      which should be checked.
      If ``klass`` parameter is not given, those should be full permission
      names rather than only codenames (i.e. ``auth.change_user``). If more than
      one permission is present within sequence, their content type **must** be
      the same or ``MixedContentTypeError`` exception would be raised.
    :param klass: may be a Model, Manager or QuerySet object. If not given
      this parameter would be computed based on given ``params``.
    :param use_groups: if ``False``, wouldn't check user's groups object
      permissions. Default is ``True``.
    :param any_perm: if True, any of permission in sequence is accepted

    :raises MixedContentTypeError: when computed content type for ``perms``
      and/or ``klass`` clashes.
    :raises WrongAppError: if cannot compute app label for given ``perms``/
      ``klass``.

    Example::

        >>> from guardian.shortcuts import get_objects_for_user
        >>> joe = User.objects.get(username='joe')
        >>> get_objects_for_user(joe, 'auth.change_group')
        []
        >>> from guardian.shortcuts import assign_perm
        >>> group = Group.objects.create('some group')
        >>> assign_perm('auth.change_group', joe, group)
        >>> get_objects_for_user(joe, 'auth.change_group')
        [<Group some group>]
        
    The permission string can also be an iterable. Continuing with the previous example:
      
        >>> get_objects_for_user(joe, ['auth.change_group', 'auth.delete_group'])
        []
        >>> get_objects_for_user(joe, ['auth.change_group', 'auth.delete_group'], any_perm=True)
        [<Group some group>]
        >>> assign_perm('auth.delete_group', joe, group)
        >>> get_objects_for_user(joe, ['auth.change_group', 'auth.delete_group'])
        [<Group some group>]        

    """
    if isinstance(perms, basestring):
        perms = [perms]
    ctype = None
    app_label = None
    codenames = set()

    # Compute codenames set and ctype if possible
    for perm in perms:
        if '.' in perm:
            new_app_label, codename = perm.split('.', 1)
            if app_label is not None and app_label != new_app_label:
                raise MixedContentTypeError("Given perms must have same app "
                    "label (%s != %s)" % (app_label, new_app_label))
            else:
                app_label = new_app_label
        else:
            codename = perm
        codenames.add(codename)
        if app_label is not None:
            new_ctype = ContentType.objects.get(app_label=app_label,
                permission__codename=codename)
            if ctype is not None and ctype != new_ctype:
                raise MixedContentTypeError("ContentType was once computed "
                    "to be %s and another one %s" % (ctype, new_ctype))
            else:
                ctype = new_ctype

    # Compute queryset and ctype if still missing
    if ctype is None and klass is None:
        raise WrongAppError("Cannot determine content type")
    elif ctype is None and klass is not None:
        queryset = _get_queryset(klass)
        ctype = ContentType.objects.get_for_model(queryset.model)
    elif ctype is not None and klass is None:
        queryset = _get_queryset(ctype.model_class())
    else:
        queryset = _get_queryset(klass)
        if ctype.model_class() != queryset.model:
            raise MixedContentTypeError("Content type for given perms and "
                "klass differs")

    # At this point, we should have both ctype and queryset and they should
    # match which means: ctype.model_class() == queryset.model
    # we should also have ``codenames`` list

    # First check if user is superuser and if so, return queryset immediately
    if user.is_superuser:
        return queryset

    # Now we should extract list of pk values for which we would filter queryset
    user_model = get_user_obj_perms_model(queryset.model)
    user_obj_perms_queryset = (user_model.objects
        .filter(user=user)
        .filter(permission__content_type=ctype)
        .filter(permission__codename__in=codenames))
    if user_model.objects.is_generic():
        fields = ['object_pk', 'permission__codename']
    else:
        fields = ['content_object__pk', 'permission__codename']
    user_obj_perms = user_obj_perms_queryset.values_list(*fields)
    data = list(user_obj_perms)
    if use_groups:
        group_model = get_group_obj_perms_model(queryset.model)
        group_filters = {
            'permission__content_type': ctype,
            'permission__codename__in': codenames,
            'group__%s' % get_user_model()._meta.module_name: user,
        }
        groups_obj_perms_queryset = group_model.objects.filter(**group_filters)
        if group_model.objects.is_generic():
            fields = ['object_pk', 'permission__codename']
        else:
            fields = ['content_object__pk', 'permission__codename']
        groups_obj_perms = groups_obj_perms_queryset.values_list(*fields)
        data += list(groups_obj_perms)

    # Here we search for groups assigned to a user
    # that have specific permissions
    uogroup_kwargs = {'user': user,
                      'content_type': ctype}
    uogroups_obj_perms = UserObjectGroup.objects\
        .filter(**uogroup_kwargs)\
        .filter(group__permissions__content_type=ctype,\
                group__permissions__codename__in=codenames)\
        .values_list('object_pk', 'group__permissions__codename')
    data += list(uogroups_obj_perms)

    keyfunc = lambda t: t[0] # sorting/grouping by pk (first in result tuple)
    data = sorted(data, key=keyfunc)
    pk_list = []
    for pk, group in groupby(data, keyfunc):
        obj_codenames = set((e[1] for e in group))
        if any_perm or codenames.issubset(obj_codenames):
            pk_list.append(pk)

    objects = queryset.filter(pk__in=pk_list)
    return objects

