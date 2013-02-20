from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_save, pre_delete
from django.contrib.auth.models import Group

from grontextual.models import UserObjectGroup
from utils.misc import remove_orphaned_obj_perms
from utils.models import Entity
from companies.models import Company


class Sensor(Entity):
    sample = models.CharField(_('sample'), max_length=30)
    class Meta:
        verbose_name = _("Sensor")
        verbose_name_plural = _("Sensors")
        permissions = (
            ("browse_sensors", "Can browse sensors"),
            ("view_sensor", "Can view sensor"),
            ("manage_sensor", "Can manage sensor"),
        )

    def __unicode__(self):
        return str(self.pk)

    @models.permalink
    def get_absolute_url(self):
        return ('sensor_edit', [str(self.id)])

