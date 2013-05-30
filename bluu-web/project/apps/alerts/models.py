from __future__ import unicode_literals
from datetime import datetime, timedelta
from bluusites.models import BluuSite

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.db.models import F
from django.dispatch import receiver
from django.db.models.signals import post_save

from devices.models import Status, DeviceType, Device
from devices.signals import (data_received, data_received_and_stored,
                             controller_heartbeat_received)
from alerts.tasks import (alert_open, alert_mir, alert_wgt, alert_wlt, alert_su,
                          alert_sys_battery_low, alert_sys_device_offline,
                          alert_sys_bluusite_offline)
from utils.misc import add_one_month


class Alert(models.Model):
    OPEN = 'o'
    OPEN_GREATER_THAN = 'ogt'
    OPEN_GREATER_THAN_NO_MOTION = 'ogtnm'
    CLOSED_GREATER_THAN = 'cgt'
    ACTIVE_IN_PERIOD_GREATER_THAN = 'aipgt'
    ACTIVE_IN_PERIOD_LESS_THAN = 'aiplt'
    MOTION_IN_ROOM = 'mir'
    MOTION_IN_ROOM_GREATER_THAN = 'mirgt'
    MOTION_IN_ROOM_LESS_THAN = 'mirlt'
    NOMOTION_IN_ROOM_GREATER_THAN = 'nmirgt'
    WEIGHT_GREATER_THAN = 'wgt'
    WEIGHT_LESS_THAN = 'wlt'
    SCALE_USED = 'su'
    SYSTEM_BATTERY = 'sysb'
    SYSTEM_TAMPER = 'syst'
    SYSTEM_DEVICE_OFFLINE = 'sysdo'
    SYSTEM_SITE_OFFLINE = 'sysso'

    ALERT_CHOICES = (
        (OPEN, _('open')),
        (OPEN_GREATER_THAN, _('open greater than')),
        (OPEN_GREATER_THAN_NO_MOTION, _('open greater than (no motion)')),
        (CLOSED_GREATER_THAN, _('closed greater than')),
        (ACTIVE_IN_PERIOD_GREATER_THAN, _('active in period greater than')),
        (ACTIVE_IN_PERIOD_LESS_THAN, _('active in period less than')),
        (MOTION_IN_ROOM, _('motion in room')),
        (MOTION_IN_ROOM_GREATER_THAN, _('motion in room greater than')),
        (MOTION_IN_ROOM_LESS_THAN, _('motion in room less than')),
        (NOMOTION_IN_ROOM_GREATER_THAN, _('no motion in room greater than')),
        (WEIGHT_GREATER_THAN, _('weight greater than')),
        (WEIGHT_LESS_THAN, _('weight less than')),
        (SCALE_USED, _('scale used')),
        (SYSTEM_BATTERY, _('battery low')),
        (SYSTEM_TAMPER, _('tamper')),
        (SYSTEM_DEVICE_OFFLINE, _('device offline')),
        (SYSTEM_SITE_OFFLINE, _('site offline')),
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


TIME_UNITS = {Alert.SECONDS: 'seconds',
              Alert.MINUTES: 'minutes',
              Alert.HOURS: 'hours',
              Alert.DAYS: 'days'}


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


class UserAlertScaleConfig(models.Model):
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
        return u'{0} | {1} | {2}'.format(unicode(self.user.get_full_name() or
                                                 self.user.username),
                                         unicode(self.alert.get_alert_type_display()),
                                         unicode(self.room.name))


class UserAlertScale(models.Model):
    """
    Set alerts for specific scales
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
    weight = models.IntegerField(_('weight'), blank=True, null=True)
    email_notification = models.BooleanField(_('email notification'),
                                             default=True)
    text_notification = models.BooleanField(_('text notification'),
                                            default=False)

    class Meta:
        verbose_name = _("user weight alert")
        verbose_name_plural = _("user weight alerts")
        unique_together = ('user', 'device', 'alert')

    def __unicode__(self):
        return u'{0} | {1} | {2}'.format(
            unicode(self.user.get_full_name() or self.user.username),
            unicode(self.alert.get_alert_type_display()),
            unicode(self.device.name))


class AlertRunnerManager(models.Manager):
    def get_alert_time(self, timestamp, alert):
        duration = alert.duration
        unit = alert.unit

        params = {TIME_UNITS.get(alert.unit, ''): duration}
        delta = timedelta(**params)
        return timestamp + delta

    def set_runners(self, uad, status=None, timestamp=None):
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
        try:
            # If there's no status then this is probably because
            # config of alert has been changed. So use latest status to
            # recalculate runner.
            if not status:
                status = Status.objects.filter(device=uad.device).latest(
                    'created')
        except Status.DoesNotExist:
            status = None
        else:
            if timestamp is None:
                timestamp = status.timestamp

            # Delete all alert runners for user alert device
            self.filter(is_active=True, user_alert_device=uad).delete()

            # if duration is set
            if uad.duration > 0:
                if status.is_active:
                    if uad.alert.alert_type in \
                            [Alert.OPEN_GREATER_THAN,
                             Alert.OPEN_GREATER_THAN_NO_MOTION]:
                        alert_time = self.get_alert_time(timestamp, uad)
                        self.create(when=alert_time, user_alert_device=uad,
                                    since=timestamp)
                    elif uad.alert.alert_type == \
                            Alert.ACTIVE_IN_PERIOD_GREATER_THAN:
                        kwargs = {TIME_UNITS[uad.unit]: uad.duration}
                        duration = timedelta(**kwargs)
                        activity_time = uad.device.get_activity_time(
                            till=timestamp)
                        target_date = timestamp
                        while activity_time < duration:
                            target_date = target_date + (duration -
                                                         activity_time)
                            activity_time = uad.device.get_activity_time(
                                till=target_date)
                        # don't set alert in past - this might happen when alert
                        # configuration has been changed and device  turns to be
                        # immediately active greater than
                        now = datetime.now()
                        if target_date < now:
                            target_date = now
                        self.create(when=target_date, user_alert_device=uad,
                                    since=timestamp)
                else:
                    if uad.alert.alert_type == Alert.CLOSED_GREATER_THAN:
                        alert_time = self.get_alert_time(timestamp, uad)
                        self.create(when=alert_time, user_alert_device=uad,
                                    since=timestamp)
                    elif uad.alert.alert_type == \
                            Alert.ACTIVE_IN_PERIOD_LESS_THAN:
                        kwargs = {TIME_UNITS[uad.unit]: uad.duration}
                        duration = timedelta(**kwargs)
                        activity_time = uad.device.get_activity_time(
                            till=timestamp)
                        target_date = timestamp
                        # If activity is longer or equal than expected duration
                        # then find out when it would be less (assuming that
                        # inactivity period has just started).
                        # Else schedule alert to be send immediately
                        while activity_time > duration:
                            target_date = target_date + activity_time - duration
                            activity_time = uad.device.get_activity_time(
                                till=target_date)
                        # don't set alert in past - this might happen when alert
                        # configuration has been changed and device turns out to
                        # be immediately active less than
                        now = datetime.now()
                        if target_date < now:
                            target_date = now
                        self.create(when=target_date, user_alert_device=uad,
                                    since=timestamp)

    def set_motion_runners(self, uar, status=None, timestamp=None):
        """
        Sets motion runners for specific room.

        1. "status" param of this function is last active motion status in the
            room
        2. Set runners for specific uar and last active motion status
         Motion is "Active" then:
          - NO_MOTION_GREATER_THAN - remove old and set again including timegap
          - MOTION_GREATER_THAN in a period - remove old and set again
            assuming activity time equal to the timegap
          - MOTION_LESS_THAN in a period - remove and set again starting at
            timegap end
         Motion is "Inactive" then:
           because activity is calculated in a way where a predefined timegap
           plays role then "inactive/close" signal is not relevant here.
        """
        try:
            if not status:
                status = Status.objects.filter(
                    device__room=uar.room,
                    device__device_type__name=DeviceType.MOTION).latest(
                        'created')
        except Status.DoesNotExist:
            status = None
        else:
            if not timestamp:
                timestamp = status.timestamp

            self.filter(is_active=True, user_alert_room=uar).delete()

            # if duration is set
            if uar.duration > 0:
                if timestamp is None:
                    timestamp = status.timestamp
                if status.action is status.device.active and\
                        uar.alert.alert_type ==\
                                Alert.NOMOTION_IN_ROOM_GREATER_THAN:
                    # Activity has just been started so nomotion has to be
                    # started after MOTION_TIME_GAP time has passed
                    timegap = timedelta(minutes=settings.MOTION_TIME_GAP)
                    alert_time = self.get_alert_time(timestamp + timegap, uar)
                    self.create(when=alert_time, user_alert_room=uar,
                                since=timestamp)


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

    objects = AlertRunnerManager()

    class Meta:
        verbose_name = _("alert runner")
        verbose_name_plural = _("alert runners")


class SystemAlertRunnerManager(models.Manager):
    def get_alert_time(self, timestamp, alert):
        duration = alert.duration
        unit = alert.unit

        params = {TIME_UNITS.get(alert.unit, ''): duration}
        delta = timedelta(**params)
        return timestamp + delta

    def send_battery_alerts(self, device, timestamp=None, period=None):
        """
        Sends battery system alerts to all dealer/technicians and
        masterusers.
        """
        bluusite = device.bluusite
        # get all dealers and masterusers for bluusite
        users = bluusite.get_site_managers()
        for user in users:
            # send immediately
            alert_sys_battery_low.delay(user, device, timestamp, period)

    def set_battery_runners(self, device, timestamp=None):
        """
        Sets runners for battery related system alerts.
        Alert has to:
         1. set to be sent in 24 hours
         2. set to be sent in a week
         3. set to be sent in a month
        """
        alert = Alert.objects.get(alert_type=Alert.SYSTEM_BATTERY)

        delta = timedelta(hours=24)
        when = timestamp + delta
        self.create(bluusite=device.bluusite, device=device, alert=alert,
                    when=when, period=_('24h'), since=timestamp)

        delta = timedelta(days=7)
        when = timestamp + delta
        self.create(bluusite=device.bluusite, device=device, alert=alert,
                    when=when, period=_('week'), since=timestamp)

        when = add_one_month(timestamp)
        self.create(bluusite=device.bluusite, device=device, alert=alert,
                    when=when, period=_('month'), since=timestamp)

    def reset_battery_runners(self, device, timestamp=None, alert_type=None):
        alert = Alert.objects.get(alert_type=Alert.SYSTEM_BATTERY)
        self.filter(device=device, alert=alert, is_active=True).delete()

    def set_device_offline_runners(self, device, timestamp=None):
        """
        Sets runners for device offline system alerts.
        Alert has to:
         1. set to be sent in 15 minutes
         2. set to be sent in 24 hours
         3. set to be sent in a week
         4. set to be sent in a month
        """
        alert = Alert.objects.get(alert_type=Alert.SYSTEM_DEVICE_OFFLINE)

        # delete old offline runners
        self.filter(device=device, alert=alert, is_active=True).delete()
        bluusite = device.bluusite

        delta = timedelta(minutes=15)
        when = timestamp + delta
        self.create(bluusite=bluusite, device=device, alert=alert, when=when,
                    period=_('15 minutes'), since=timestamp)

        delta = timedelta(hours=24)
        when = timestamp + delta
        self.create(bluusite=bluusite, device=device, alert=alert, when=when,
                    period=_('24h'), since=timestamp)

        delta = timedelta(days=7)
        when = timestamp + delta
        self.create(bluusite=bluusite, device=device, alert=alert, when=when,
                    period=_('week'), since=timestamp)

        when = add_one_month(timestamp)
        self.create(bluusite=bluusite, device=device, alert=alert, when=when,
                    period=_('month'), since=timestamp)

    def send_device_offline_alerts(self, device, timestamp=None, period=None):
        """
        Sends device offline system alerts to all dealer/technicians and
        masterusers.
        """
        bluusite = device.bluusite
        # get all dealers and masterusers for bluusite
        users = bluusite.get_site_managers()
        for user in users:
            alert_sys_device_offline.delay(user, device, timestamp, period)

    def set_bluusite_offline_runners(self, bluusite, timestamp=None):
        """
        Sets runners for offline related system alerts.
        Alert has to:
         1. set to be sent in 15 minutes
         2. set to be sent in 24 hours
         3. set to be sent in a week
         4. set to be sent in a month
        """
        alert = Alert.objects.get(alert_type=Alert.SYSTEM_SITE_OFFLINE)

        # delete old offline runners
        self.filter(bluusite=bluusite, alert=alert, is_active=True).delete()

        delta = timedelta(minutes=15)
        when = timestamp + delta
        self.create(bluusite=bluusite, alert=alert, when=when,
                    period=_('15 minutes'), since=timestamp)

        delta = timedelta(hours=24)
        when = timestamp + delta
        self.create(bluusite=bluusite, alert=alert, when=when,
                    period=_('24h'), since=timestamp)

        delta = timedelta(days=7)
        when = timestamp + delta
        self.create(bluusite=bluusite, alert=alert, when=when,
                    period=_('week'), since=timestamp)

        when = add_one_month(timestamp)
        self.create(bluusite=bluusite, alert=alert, when=when,
                    period=_('month'), since=timestamp)

    def send_bluusite_offline_alerts(self, bluusite, timestamp=None,
                                     period=None):
        """
        Sends bluusite offline system alerts to all dealer/technicians and
        masterusers.
        """
        # get all dealers and masterusers for bluusite
        users = bluusite.get_site_managers()
        for user in users:
            alert_sys_bluusite_offline.delay(user, bluusite, timestamp, period)

    def send_tamper_alerts(self, device, timestamp=None):
        """
        Sends tamper system alerts to all dealer/technicians and
        masterusers.
        """
        bluusite = device.bluusite
        # get all dealers and masterusers for bluusite
        users = bluusite.get_site_managers()
        for user in users:
            # send immediately
            alert_sys_tamper.delay(user, device, timestamp)


class SystemAlertRunner(models.Model):
    """
    Set system alerts to be run.
    """
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    PERIODS = (
        (DAY, _('day')),
        (WEEK, _('week')),
        (MONTH, _('month')),
    )

    device = models.ForeignKey(Device, null=True, blank=True)
    bluusite = models.ForeignKey(BluuSite)
    alert = models.ForeignKey(Alert, null=True, blank=True)

    when = models.DateTimeField(_('when'), db_index=True)
    period = models.CharField(_('period'), max_length=50,
                              choices=PERIODS)

    # last signal that triggered this alert was seen at
    since = models.DateTimeField(_('since'))
    is_active = models.BooleanField(_('active'), default=True)

    objects = SystemAlertRunnerManager()

    class Meta:
        verbose_name = _("system alert runner")
        verbose_name_plural = _("system alert runners")


"""
Alert configuration changes
"""
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


@receiver(post_save, sender=UserAlertScaleConfig)
def _update_alert_scale_settings(sender, instance, created, *args, **kwargs):
    """
    If alert settings, for specific scale alert were changed then
    update all related set alerts
    """
    from devices.models import DeviceType
    if instance.pk:
        if instance.device_type.name == DeviceType.SCALE:
            for uas in UserAlertScale.objects.filter(
                    user=instance.user,
                    alert=instance.alert,
                    device__device_type=instance.device_type):
                uas.weight = instance.weight
                uas.email_notification = instance.email_notification
                uas.text_notification = instance.text_notification
                uas.save()


"""
Update runners after alert has been enabled/disabled by specific user
"""
@receiver(post_save, sender=UserAlertDevice)
def _update_alert_device_runners(sender, instance, created, *args, **kwargs):
    """
    If useralertdevice has been updated (alert configuration change) then
    alert runners should be reconfigured
    """
    AlertRunner.objects.set_runners(uad=instance)


@receiver(post_save, sender=UserAlertRoom)
def _update_alert_motion_runners(sender, instance, created, *args, **kwargs):
    """
    If useralertroom has been updated (alert configuration change) then
    alert runners should be reconfigured
    """
    AlertRunner.objects.set_motion_runners(uar=instance)


"""
Dispatch alerts to specific tasks (send immediately or set runners)
"""
@receiver(data_received, sender=Status)
def dispatch_system_device_alerts(sender, data, device, timestamp,
                               *args, **kwargs):
    """
    Checks which system alerts should be set for status that has just been
    saved.
    """
    if data['battery']:
        # send alerts
        SystemAlertRunner.objects.send_battery_alerts(device, timestamp)
        # set alerts for battery
        SystemAlertRunner.objects.set_battery_runners(device, timestamp)
    else:
        # reset alerts for battery if such alerts were set
        SystemAlertRunner.objects.reset_battery_runners(device)

    if data['tamper']:
        SystemAlertRunner.objects.send_tamper_alerts(device, timestamp)

    # set runner for offline
    SystemAlertRunner.objects.set_device_offline_runners(device, timestamp)
    SystemAlertRunner.objects.set_bluusite_offline_runners(device.bluusite,
                                                           timestamp)


@receiver(controller_heartbeat_received, sender=BluuSite)
def dispatch_system_site_alerts(sender, bluusite, timestamp, *args, **kwargs):
    # set runner for offline for site controller
    # remove old runners
    # set new one
    SystemAlertRunner.objects.set_bluusite_offline_runners(bluusite, timestamp)


@receiver(data_received_and_stored, sender=Status)
def dispatch_alerts(sender, status, *args, **kwargs):
    """
    Checks which alerts should be set for status that has just been
    saved.
    """
    previous_action = None
    if status.device_type.name == DeviceType.MOTION:
        # get previous status in the current room to check if there's a state
        # change
        statuses = Status.objects.filter(
            device__room=status.device.room).order_by('-timestamp')[:2]
        if statuses and len(statuses) == 2:
            # Set previous action to active value
            previous_action = statuses[1].action == statuses[1].device.active

        action = status.action == status.device.active
        if action != previous_action:
            # Each motion device sends "open" and then "closed" after some time.
            # Set motion alerts
            # If motion comes then it is required to set alerts per room
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
                        AlertRunner.objects.set_motion_runners(
                            uar, status, status.timestamp)

                # Reset "NO_MOTION" alerts
                # get all UserDeviceAlerts in the site where motion has just
                # occurred that have NOMOTION alerts configured
                uads = UserAlertDevice.objects.filter(
                    device__bluusite=status.device.bluusite,
                    alert__alert_type=Alert.OPEN_GREATER_THAN_NO_MOTION)
                # reset runners
                for uad in uads:
                    # nomotion runners are set again, starting with current
                    # motion's status timestamp
                    AlertRunner.objects.set_runners(uad, status,
                                                    status.timestamp)
    elif status.device_type.name == DeviceType.SCALE:
        # if there's a weight
        if status.float_data:
            # get all alerts configured for this scale
            uass = UserAlertScale.objects.select_related('alert').\
                filter(device=status.device)
            for uas in uass:
                # Send alert immediately
                if uas.alert.alert_type == Alert.WEIGHT_GREATER_THAN:
                    alert_wgt.delay(uas, status)
                if uas.alert.alert_type == Alert.WEIGHT_LESS_THAN:
                    alert_wlt.delay(uas, status)
                if uas.alert.alert_type == Alert.SCALE_USED:
                    alert_su.delay(uas, status)
    elif status.device_type.name == DeviceType.BLOOD_PRESSURE:
        pass
    else:
        statuses = Status.objects.filter(
            device=status.device).order_by('-timestamp')[:2]
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
                    AlertRunner.objects.set_runners(uad, status)
