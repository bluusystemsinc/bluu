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

    alert_type = models.CharField(_('alert'), max_length=50,
                                  choices=ALERT_CHOICES)
    device_types = models.ManyToManyField("devices.DeviceType")

    class Meta:
        verbose_name = _("alert")
        verbose_name_plural = _("alerts")

    def __unicode__(self):
        return u'{0} | {1}'.format(unicode(self.pk),
                                   unicode(self.get_alert_type_display()))


class UserAlertConfig(models.Model):
    bluusite = models.ForeignKey("bluusites.BluuSite")
    device_type = models.ForeignKey("devices.DeviceType")
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


class UserAlertWeightConfig(models.Model):
    bluusite = models.ForeignKey("bluusites.BluuSite")
    device_type = models.ForeignKey("devices.DeviceType")
    user = models.ForeignKey(
                settings.AUTH_USER_MODEL,
                verbose_name=_('user'))
    alert = models.ForeignKey(
                Alert,
                verbose_name=_('alert'))
    weight = models.IntegerField(_('weight'), blank=True, null=True)
    email_notification = models.BooleanField(_('email notification'),
                                             default=True)
    text_notification = models.BooleanField(_('text notification'),
                                            default=False)

    class Meta:
        verbose_name = _("user alert weight configuration")
        verbose_name_plural = _("user alert weight configurations")
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
                "devices.Device",
                verbose_name=_('device'), db_index=True)
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
    room = models.ForeignKey("bluusites.Room", verbose_name=_('room'))
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


class AlertRunner(models.Model):
    """
    Set alerts to be run.
    """
    when = models.DateTimeField(_('when'), db_index=True)
    user_alert_device = models.ForeignKey(UserAlertDevice, null=True,
                                          blank=True)
    user_alert_room = models.ForeignKey(UserAlertRoom, null=True, blank=True)

    # last signal that triggered this alert was seen at
    since = models.DateTimeField(_('since'))
    is_active = models.BooleanField(_('active'), default=True)


    class Meta:
        verbose_name = _("alert runner")
        verbose_name_plural = _("alert runners")

    #def __unicode__(self):
    #    return u'{0} | {1} | {2}'.format(unicode(self.when),
    #                                    )


@receiver(post_save, sender=UserAlertConfig)
def _update_alert_settings(sender, instance, created, *args, **kwargs):
    """
    If alert settings, for specific device_type were changed then
    update all related set alerts
    """
    from devices.models import DeviceType
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


@receiver(post_save, sender=UserAlertDevice)
def _update_alert_device(sender, instance, created, *args, **kwargs):
    print "after useralertdevice has been updated alert runners should be reconfigured"


@receiver(post_save, sender=UserAlertRoom)
def _update_alert_room(sender, instance, created, *args, **kwargs):
    print "after useralertroom has been updated alert runners should be reconfigured"