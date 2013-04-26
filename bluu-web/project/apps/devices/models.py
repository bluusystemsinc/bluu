from __future__ import unicode_literals
from datetime import datetime, timedelta
from alerts.models import UserAlertDevice

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from autoslug import AutoSlugField
from model_utils.models import TimeStampedModel
from .signals import data_received, data_received_and_stored


class DeviceType(models.Model):
    BED = 'Bed'
    BLOOD_PRESSURE = 'Blood pressure'
    DOOR = 'Door'
    EMERGENCY = 'Emergency'
    MOTION = 'Motion'
    REFRIGERATOR = 'Refrigerator'
    SCALE = 'Scale'
    SEAT = 'Seat'
    WINDOW = 'Window'
    DEVICE_TYPE_CHOICES = (
        (BED, _('Bed')),
        (BLOOD_PRESSURE, _('Blood Pressure')),
        (DOOR, _('Door')),
        (EMERGENCY, _('Emergency')),
        (MOTION, _('Motion')),
        (REFRIGERATOR, _('Refrigerator')),
        (SCALE, _('Scale')),
        (SEAT, _('Seat')),
        (WINDOW, _('Window')),
    )

    #name = models.CharField(_('name'), max_length=255)
    name = models.CharField(_('name'), max_length=15,
                            choices=DEVICE_TYPE_CHOICES)
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
    slug = AutoSlugField(populate_from='serial')
    #device_type = models.CharField(_('type'), max_length=8, choices=DEVICE_CHOICES)
    device_type = models.ForeignKey(DeviceType)
    bluusite = models.ForeignKey('bluusites.BluuSite')
    room = models.ForeignKey('bluusites.Room')
    last_seen = models.DateTimeField(_('last seen'), null=True, blank=True)
    active = models.BooleanField(_('check this if device active state is when action bit\'s value equals to "ON"'), default=True)

    @property
    def inactive(self):
        return not self.active

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
    bluusite = models.ForeignKey('bluusites.BluuSite', db_index=True)
    device_type = models.ForeignKey(DeviceType, db_index=True)
    room = models.ForeignKey('bluusites.Room', db_index=True)

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
    timestamp = models.DateTimeField(_('timestamp'), db_index=True)

    class Meta:
        verbose_name = _("status")
        verbose_name_plural = _("statuses")

    def __unicode__(self):
        return "{0} | {1} | {2}".format(self.timestamp,
                                        self.device.name,
                                        self.data)

    @property
    def is_active(self):
        if self.device.device_type.name == DeviceType.MOTION:
            if self.action:
                return True
        return False


@receiver(data_received, sender=Status)
def set_device_last_seen(sender, device, data, timestamp, *args, **kwargs):
    """
    Sets device's last seen after a status update was received
    """
    device.last_seen = timestamp
    device.save()


@receiver(data_received, sender=Status)
def set_site_last_seen(sender, device, data, timestamp, *args, **kwargs):
    """
    Sets site's last seen after a status update was received
    """
    device.bluusite.last_seen = timestamp
    device.bluusite.save()


@receiver(data_received, sender=Status)
def update_site_ip_address(sender, device, data, timestamp, ip_address,
                           *args, **kwargs):
    """
    Sets site's ip address to ip address from which last status update was received
    """
    if device.bluusite.ip != ip_address:
        device.bluusite.ip = ip_address
        device.bluusite.save()


@receiver(data_received_and_stored, sender=Status)
def check_alerts(sender, status, *args, **kwargs):
    if status.device_type == DeviceType.MOTION:
        pass
    else:
        alerts = UserAlertDevice.objects.filter(device=status.device)
        alert_types = alerts.values('alert')
        for alert_type in alert_types:
            print alert_type
