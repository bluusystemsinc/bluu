from __future__ import unicode_literals
from datetime import datetime, timedelta

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel
from bluusites.models import (BluuSite, Room)
from .signals import data_received


class DeviceType(models.Model):
    name = models.CharField(_('name'), max_length=255)
    icon = models.ImageField(_('icon'), upload_to='resources/devices/icons')

    class Meta:
        verbose_name = _("device type")
        verbose_name_plural = _("device types")
        ordering = ('name',)

    def __unicode__(self):
        return "{}".format(self.name)


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
    #device_type = models.CharField(_('type'), max_length=8, choices=DEVICE_CHOICES)
    device_type = models.ForeignKey(DeviceType)
    bluusite = models.ForeignKey(BluuSite)
    room = models.ForeignKey(Room)
    last_seen = models.DateTimeField(_('last seen'), null=True, blank=True)

    class Meta:
        verbose_name = _("device")
        verbose_name_plural = _("devices")
        permissions = (
            ("browse_devices", "Can browse devices"),
            ("view_device", "Can view device"),
        )
        unique_together = (('bluusite', 'serial'),)

    def __unicode__(self):
        return "{0} | {1}".format(self.serial, self.device_type.name)

    @models.permalink
    def get_absolute_url(self):
        return ('site_devices:device_edit', [str(self.bluusite_id), str(self.id)])

    @property
    def is_online(self):
        if (datetime.now() - self.last_seen) > timedelta(hours = 1):
            return False
        return True


class Status(models.Model):
    created = models.DateTimeField(_('created'),
                                   editable=False,
                                   auto_now_add=True)
    device = models.ForeignKey(Device)
    data = models.IntegerField(_('data'))
    signal = models.IntegerField(_('signal'))
    float_data = models.FloatField(_('float data'), null=True, blank=True)
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

@receiver(post_save, sender=Status)
def set_device_last_seen(sender, instance, *args, **kwargs):
    """
    Sets device's last seen after a status update was received
    """
    instance.device.last_seen = instance.created
    instance.device.save()


@receiver(post_save, sender=Status)
def set_site_last_seen(sender, instance, *args, **kwargs):
    """
    Sets site's last seen after a status update was received
    """
    instance.device.bluusite.last_seen = instance.created
    instance.device.bluusite.save()


@receiver(data_received, sender=Status)
def update_site_ip_address(sender, instance, ip_address, *args, **kwargs):
    """
    Sets site's ip address to ip addres from which last status update was received
    """
    if instance.device.bluusite.ip != ip_address:
        instance.device.bluusite.ip = ip_address
        instance.device.bluusite.save()

