from __future__ import unicode_literals
from datetime import datetime, timedelta
import calendar

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.db.models import F
from django.dispatch import receiver
from django.db.models.signals import (post_save, pre_save, pre_delete)

from bluusites.models import (BluuSite, Room)
from devices.models import (Device, DeviceType)


class Alert(models.Model):
    OPEN = 'o'
    OPEN_GREATER_THAN = 'ogt'
    OPEN_GREATER_THAN_NO_MOTION = 'ogtnm'
    CLOSED_GREATER_THAN = 'cgt'
    ACTIVE_IN_PERIOD_GREATER_THAN = 'aipgt'
    INACTIVE_IN_PERIOD_GREATER_THAN = 'iipgt'
    MOTION_IN_ROOM = 'mir'
    MOTION_IN_ROOM_GREATER_THAN = 'mirgt'
    MOTION_IN_ROOM_LESS_THAN = 'mirlt'
    NOMOTION_IN_ROOM_GREATER_THAN = 'nmirgt'
    WEIGHT_GREATER_THAN = 'wgt'
    WEIGHT_LESS_THAN = 'wlt'
    SCALE_USED = 'su'

    ALERT_CHOICES = (
             (OPEN, _('open')),
             (OPEN_GREATER_THAN, _('open greater than')),
             (OPEN_GREATER_THAN_NO_MOTION, _('open greater than (no motion)')),
             (CLOSED_GREATER_THAN, _('closed greater than')),
             (ACTIVE_IN_PERIOD_GREATER_THAN, _('active in period greater than')),
             (INACTIVE_IN_PERIOD_GREATER_THAN, _('inactive in period greater than')),
             (MOTION_IN_ROOM, _('motion in room')),
             (MOTION_IN_ROOM_GREATER_THAN, _('motion in room greater than')),
             (MOTION_IN_ROOM_LESS_THAN, _('motion in room less than')),
             (NOMOTION_IN_ROOM_GREATER_THAN, _('no motion in room greater than')),
             (WEIGHT_GREATER_THAN, _('weight greater than')),
             (WEIGHT_LESS_THAN, _('weight less than')),
             (SCALE_USED, _('scale used')),
            )

    SECONDS = 's'
    MINUTES = 'm'
    HOURS = 'h'
    DAYS = 'd'
    UNITS = (
        (SECONDS, _('seconds')),
        (MINUTES, _('minutes')),
        (HOURS, _('hours')),
        (DAYS, _('days')),
    )

    alert_type = models.CharField(_('alert'), max_length=50, choices=ALERT_CHOICES)
    device_types = models.ManyToManyField(DeviceType)

    class Meta:
        verbose_name = _("alert")
        verbose_name_plural = _("alerts")

    def __unicode__(self):
        return u'{0} | {1}'.format(unicode(self.pk),
                                   unicode(self.get_alert_type_display()))


class UserAlertConfig(models.Model):
    bluusite = models.ForeignKey(BluuSite)
    device_type = models.ForeignKey(DeviceType)
    user = models.ForeignKey(
                settings.AUTH_USER_MODEL,
                verbose_name=_('user'))
    alert = models.ForeignKey(
                Alert,
                verbose_name=_('alert'))
    duration = models.IntegerField(_('duration'), blank=True, null=True)
    unit = models.CharField(_('unit'), blank=True, null=True, choices=Alert.UNITS,
                            max_length=2)
    email_notification = models.BooleanField(_('email notification'),
                                             default=True)
    text_notification = models.BooleanField(_('text notification'),
                                            default=False)

    class Meta:
        verbose_name = _("user alert configuration")
        verbose_name_plural = _("user alert configurations")
        unique_together = ('bluusite', 'device_type', 'user', 'alert')

    def __unicode__(self):
        return u'{0} | {1}'.format(unicode(self.user.get_full_name() or \
                                           self.user.username),
                                   unicode(self.alert.get_alert_type_display()))


class UserAlertDevice(models.Model):
    """
    Set alerts for specific device's
    """
    user = models.ForeignKey(
                settings.AUTH_USER_MODEL,
                verbose_name=_('user'))
    alert = models.ForeignKey(
                Alert,
                verbose_name=_('alert'))
    device = models.ForeignKey(
                Device,
                verbose_name=_('device'))
    duration = models.IntegerField(_('duration'), blank=True, null=True)
    unit = models.CharField(_('unit'), blank=True, null=True, choices=Alert.UNITS,
                            max_length=2)
    email_notification = models.BooleanField(_('email notification'),
                                             default=True)
    text_notification = models.BooleanField(_('text notification'),
                                            default=False)

    class Meta:
        verbose_name = _("user alert")
        verbose_name_plural = _("user alerts")
        unique_together = ('user', 'device', 'alert')

    def __unicode__(self):
        return u'{0} | {1} | {2}'.format(
            unicode(self.user.get_full_name() or self.user.username),
            unicode(self.alert.get_alert_type_display()),
            unicode(self.device.name))


class UserAlertRoom(models.Model):
    """
    Set alerts for specific rooms. This is only for motion detection.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))
    alert = models.ForeignKey(Alert, verbose_name=_('alert'))
    room = models.ForeignKey(Room, verbose_name=_('room'))
    duration = models.IntegerField(_('duration'), blank=True, null=True)
    unit = models.CharField(_('unit'), blank=True, null=True,
                            choices=Alert.UNITS, max_length=2)
    email_notification = models.BooleanField(_('email notification'),
                                             default=True)
    text_notification = models.BooleanField(_('text notification'),
                                            default=False)

    class Meta:
        verbose_name = _("user room alert")
        verbose_name_plural = _("user room alerts")
        unique_together = ('user', 'room', 'alert')

    def __unicode__(self):
        return u'{0} | {1} | {2}'.format(unicode(self.user.get_full_name() or\
                                                 self.user.username),
                                         unicode(self.alert.get_alert_type_display()),
                                         unicode(self.room.name),
                                        )


@receiver(post_save, sender=UserAlertConfig)
def _update_alert_settings(sender, instance, created, *args, **kwargs):
    """
    If alert settings, for specific device_type were changed then
    update all related set alerts
    """
    if instance.pk:
        if instance.device_type.name == DeviceType.MOTION:
            for uar in UserAlertRoom.objects.filter(
                    user=instance.user,
                    alert=instance.alert,
                    room__device__device_type=instance.device_type):
                uar.duration = instance.duration
                uar.unit = instance.unit
                uar.email_notification = instance.email_notification
                uar.text_notification = instance.text_notification
                uar.save()
        else:
            for uad in UserAlertDevice.objects.filter(
                    user=instance.user,
                    alert=instance.alert,
                    device__device_type=instance.device_type):
                uad.duration = instance.duration
                uad.unit = instance.unit
                uad.email_notification = instance.email_notification
                uad.text_notification = instance.text_notification
                uad.save()


