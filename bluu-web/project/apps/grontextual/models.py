from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group 
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from .managers import UserObjectGroupManager


class UserObjectGroup(models.Model):
    """
    This is universal model that is used to check wheter a 'user' has a specific
    'group' assigned to him in a context of an 'content_object'
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    group = models.ForeignKey(Group)
    content_type = models.ForeignKey(ContentType)
    object_pk = models.CharField(_('object ID'), max_length=255)
    content_object = generic.GenericForeignKey(fk_field='object_pk')

    objects = UserObjectGroupManager()

    def __unicode__(self):
        return u'%s | %s | %s' % (
            unicode(self.content_object),
            unicode(getattr(self, 'user', '---')),
            unicode(getattr(self, 'group', '---')))
