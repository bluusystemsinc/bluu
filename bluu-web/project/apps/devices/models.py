from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_save, pre_delete
from django.contrib.auth.models import Group

from model_utils.models import TimeStampedModel

from bluusites.models import (BluuSite, Room)
from grontextual.models import UserObjectGroup
from utils.misc import remove_orphaned_obj_perms


class Device(TimeStampedModel):
    RECEIVER = 'receiver'
    DW1 = 'dw1'
    DW2 = 'dw2'
    DW3 = 'dw3'
    SHOCK = 'shock'
    TILT = 'tilt'
    FLOOD = 'flood'
    CO = 'co'
    SMOKE = 'smoke'
    PIR ='pir'
    GLASS = 'glass'
    TAKEOVER = 'takeover'
    KEY = 'key'
    PANIC = 'panic'
    DEVICE_CHOICES = (
        (RECEIVER, _('receiver')),
        (DW1, _('dw1')),
        (DW2, _('dw2')),
        (DW3, _('dw3')),
        (SHOCK, _('shock')),
        (TILT, _('tilt')),
        (FLOOD, _('flood')),
        (CO, _('co')),
        (SMOKE, _('smoke')),
        (PIR, _('pir')),
        (GLASS, _('glass')),
        (TAKEOVER, _('takeover')),
        (KEY, _('key')),
        (PANIC, _('panic'))
    )

    name = models.CharField(_('name'), max_length=255)
    serial = models.CharField(_('serial'), max_length=6)
    device_type = models.CharField(_('type'), max_length=8, choices=DEVICE_CHOICES)
    bluusite = models.ForeignKey(BluuSite)
    room = models.ForeignKey(Room)

    class Meta:
        verbose_name = _("device")
        verbose_name_plural = _("devices")
        permissions = (
            ("browse_devices", "Can browse devices"),
            ("view_device", "Can view device"),
        )

    def __unicode__(self):
        return "{0} | {1}".format(self.serial, self.get_device_type_display())

    @models.permalink
    def get_absolute_url(self):
        return ('devices:device_edit', [str(self.bluusite_id), str(self.id)])


class Status(models.Model):
    created = models.DateTimeField(_('created'),
                                   editable=False,
                                   auto_now_add=True)
    device = models.ForeignKey(Device)
    data = models.IntegerField(_('data'))
    signal = models.IntegerField(_('signal'))
    action = models.BooleanField(_('action'))
    battery = models.BooleanField(_('battery'))
    input1 = models.BooleanField(_('input1'))
    input2 = models.BooleanField(_('input2'))
    input3 = models.BooleanField(_('input3'))
    input4 = models.BooleanField(_('input4'))
    supervisory = models.BooleanField(_('supervisory'))
    tamper = models.BooleanField(_('tamper'))
    timestamp = models.DateTimeField(_('timestamp'))

    class Meta:
        verbose_name = _("status")
        verbose_name_plural = _("statuses")

    def __unicode__(self):
        return "{0} | {1} | {2}".format(self.timestamp,
                                        self.device.name,
                                        self.data)
