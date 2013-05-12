from __future__ import unicode_literals
from datetime import datetime, timedelta
import calendar
from devices.models import Status, DeviceType, Device
from devices.signals import data_received_and_stored

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.db.models import F
from django.dispatch import receiver
from django.db.models.signals import (post_save, pre_save, pre_delete)
from django.db.models.signals import post_save

from alerts.tasks import (alert_open, alert_mir)


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
                                         unicode(self.room.name))


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


TIME_UNITS = {Alert.SECONDS: 'seconds',
              Alert.MINUTES: 'minutes',
              Alert.HOURS: 'hours',
              Alert.DAYS: 'days'}


def get_alert_time(timestamp, alert):
    duration = alert.duration
    unit = alert.unit

    params = {TIME_UNITS.get(alert.unit, ''): duration}
    delta = timedelta(**params)
    return timestamp + delta


def set_runners(uad, status, timestamp=None):
    """
    Sets runners for specific uad and last status
    If alert is of type:
        - OPEN_GREATER_THAN
        - OPEN_GREATER_THAN_NO_MOTION
        - CLOSED_GREATER_THAN
      and
        - duration is set
    then:
        - add configured duration to status timestamp
        - set alert runner
    """
    # Delete all alert runners for user alert device
    AlertRunner.objects.filter(is_active=True, user_alert_device=uad).delete()

    # if duration is set
    if uad.duration > 0:

        if status.action is status.device.active and\
                uad.alert.alert_type in\
                [Alert.OPEN_GREATER_THAN,
                 Alert.OPEN_GREATER_THAN_NO_MOTION]:
            alert_time = get_alert_time(timestamp, uad)
            AlertRunner.objects.create(when=alert_time,
                                       user_alert_device=uad,
                                       since=timestamp)
        elif status.action is status.device.inactive and\
                uad.alert.alert_type == Alert.CLOSED_GREATER_THAN:
            alert_time = get_alert_time(timestamp, uad)
            AlertRunner.objects.create(when=alert_time,
                                       user_alert_device=uad,
                                       since=timestamp)


def update_alert_runners(uad, status=None, timestamp=None):
    """
    Updates alert runners when:
    1. new status for a specific monitored device arrived
    2. alert settings were changed
    3. new status for motion device arrived - it's possible that "open greater
    than no motion" type of alert is set so it has to be updated. This is also
    why arbitrary timestamp is passed into this function - it might be
    timestamp for motion event, and not for the last status for device.
    """
    try:
        if not status:
            status = Status.objects.filter(device=uad.device).latest('created')
    except Status.DoesNotExist:
        status = None
    else:
        if timestamp is None:
            timestamp = status.timestamp
        set_runners(uad, status, timestamp)


def set_motion_runners(uar, status, timestamp=None):
    """
    Sets motion runners for specific room.

    1. "status" param of this function is last active motion status in the room
    2. Set runners for specific uar and last active motion status
    If alert is of type:
        - NO_MOTION_GREATER_THAN
        and
        - duration is set
      then:
        - add configured duration to status timestamp
        - set alert runner
    Else If alert is of type:
        - MOTION_GREATER_THAN (in 24h)
        - MOTION_LESS_THAN (in 24h)
        and
        - duration is set
      then
        -...
    """
    # Delete all alert runners for user room
    AlertRunner.objects.filter(is_active=True, user_alert_room=uar).delete()

    # all devices in the room
    motion_devices = Device.objects.filter(room=uar.room,
                                           device_type__name=DeviceType.MOTION)

    # if duration is set
    if uar.duration > 0:
        if timestamp is None:
            timestamp = status.timestamp
        if status.action is status.device.active and\
                uar.alert.alert_type == Alert.NOMOTION_IN_ROOM_GREATER_THAN:
            alert_time = get_alert_time(timestamp, uar)
            AlertRunner.objects.create(when=alert_time,
                                       user_alert_room=uar,
                                       since=timestamp)
        #elif status.action is status.device.inactive and\
        #        uar.alert.alert_type == Alert.CLOSED_GREATER_THAN:
        #    alert_time = get_alert_time(timestamp, uad)
        #    AlertRunner.objects.create(when=alert_time,
        #                               user_alert_device=uad,
        #                               since=timestamp)


def update_motion_alert_runners(uar, status=None, timestamp=None):
    """
    Updates motion alert runners when:
    1. new status for a specific monitored room arrived
    2. alert settings were changed
    """
    try:
        if not status:
            status = Status.objects.filter(
                device__room=uar.room,
                device__device_type__name=DeviceType.MOTION).latest('created')
    except Status.DoesNotExist:
        status = None
    else:
        if not timestamp:
            timestamp = status.timestamp
        set_motion_runners(uar, status, timestamp)


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
        elif instance.device_type.name == DeviceType.SCALE:
            print "NO scale support yet"
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
    """
    If useralertdevice has been updated (alerts configuration change) then
    alert runners should be reconfigured
    """
    update_alert_runners(instance)


@receiver(post_save, sender=UserAlertRoom)
def _update_alert_motions(sender, instance, created, *args, **kwargs):
    """
    If useralertroom has been updated then
    alert runners should be reconfigured
    """
    update_motion_alert_runners(instance)


@receiver(data_received_and_stored, sender=Status)
def check_alerts(sender, status, *args, **kwargs):
    """
    Checks what alerts should be set for status that has just been
    saved.
    """

    previous_action = None
    if status.device_type.name == DeviceType.MOTION:
        # get previous status in the current room to check if there's a state
        # change
        statuses = Status.objects.filter(
            device__room=status.device.room).order_by('-created')[:2]
        if statuses and len(statuses) == 2:
            # Set previous action to active value
            previous_action = statuses[1].action == statuses[1].device.active

        action = status.action == status.device.active
        if action != previous_action:
            # Each motion device sends "open" and then "closed" after some time
            # set motion alerts
            # if motion come then it is required to set alerts per room
            if status.action is status.device.active:
                # Get alerts defined for this room
                uars = UserAlertRoom.objects.select_related('alert').\
                    filter(room=status.device.room)
                for uar in uars:
                    # If alert is: Motion in room then send alert immediately
                    if uar.alert.alert_type == Alert.MOTION_IN_ROOM:
                        alert_mir.delay(uar, status)
                    elif uar.alert.alert_type ==\
                            Alert.NOMOTION_IN_ROOM_GREATER_THAN:
                        update_motion_alert_runners(uar, status,
                                                    status.timestamp)

                # Reset "NO_MOTION" alerts
                # get all userdevicealerts in the site where motion has just
                # occured that have NOMOTION alerts configured
                uads = UserAlertDevice.objects.filter(
                        device__bluusite=status.device.bluusite,
                        alert__alert_type=Alert.OPEN_GREATER_THAN_NO_MOTION)
                # reset runners
                for uad in uads:
                    # nomotion runners are set again, starting with current
                    # motion's status timestamp
                    update_alert_runners(uad, status, status.timestamp)
    elif status.device_type.name == DeviceType.SCALE:
        pass
    elif status.device_type.name == DeviceType.BLOOD_PRESSURE:
        pass
    else:
        statuses = Status.objects.filter(
            device=status.device).order_by('-created')[:2]
        if statuses and len(statuses) == 2:
            previous_action = statuses[1].action

        if status.action != previous_action:
            """
            If status' "action" is different than the previous status' "action",
            then this is a state change
            """
            # get all alerts configured for this device
            uads = UserAlertDevice.objects.select_related('alert').\
                filter(device=status.device)
            for uad in uads:
                # If alert is: open or closed
                # Send alert immediately
                if uad.alert.alert_type == Alert.OPEN:
                    alert_open.delay(uad, status)
                else:
                    set_runners(uad, status)
