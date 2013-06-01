from datetime import datetime, timedelta
from bluusites.models import Room
from celery import task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from utils.misc import BluuMessage


logger = get_task_logger(__name__)


def alerts_allowed(bluusite):
    return bluusite.user_alerts


def user_alerts_allowed(user, bluusite):
    """
    Checks if current user is allowed to receive alert
    notifications:
    - he is assigned to a site with a "bluusites.view_bluusite" permission
    - user_alerts parameter of bluusite is set to True
    """
    if user.is_site_user(bluusite):
        return bluusite.user_alerts
    return False


def dealer_alerts_allowed(user, bluusite):
    """
    Checks if current user is allowed to receive alert
    notifications:
    - he is assigned to a dealer company of current site
      with a "bluusites.view_bluusite" permission
    - dealer_alerts parameter of bluusite is set to True
    """
    if user.is_site_dealer(bluusite):
        return bluusite.user_alerts
    return False


@task(name='alerts.call_open')
def alert_open(uad, status):
    user = uad.user
    site = uad.device.bluusite
    # check here because this alert isn't called via alert runner
    if (user_alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        device_name = uad.device.name
        room = uad.device.room.name
        site_name = uad.device.bluusite.name
        timestamp = status.timestamp

        body = render_to_string('alerts/notifications/open.html', {
            'user': user,
            'device_name': device_name,
            'room': room,
            'site_name': site_name,
            'timestamp': timestamp
        })
        subject = render_to_string(
            'alerts/notifications/notification_title.html',
            dict(site_name=site_name,
                 alert_name=_('device open')))

        if uad.email_notification:
            logger.info(
                'Open alert sent to {0} for device {1}'.format(user.email,
                                                               device_name))
            msg = BluuMessage(subject, body, user.email)
            msg.send()

        if uad.text_notification:
            logger.info('Open text alert sent to {0} for device {1}'.
            format(user.cell_text_email, device_name))
            msg = BluuMessage(subject, body, user.cell_text_email)
            msg.send()


@task(name='alerts.call_ogt')
def alert_open_greater_than(runner):
    uad = runner.user_alert_device
    user = uad.user
    device_name = uad.device.name
    room = uad.device.room.name
    site_name = uad.device.bluusite.name
    duration = uad.duration
    unit = uad.get_unit_display()
    timestamp = runner.since

    body = render_to_string('alerts/notifications/open_gt.html', {
        'user': user,
        'device_name': device_name,
        'room': room,
        'site_name': site_name,
        'timestamp': timestamp,
        'duration': duration,
        'unit': unit
    })

    subject = _(u'%(site_name)s alert - %(alert_name)s') % \
              {'site_name': site_name,
               'alert_name': _('device open too long')}

    if uad.email_notification:
        logger.info(
            'OGT alert sent to {0} for device {1}'.format(user.email,
                                                          device_name))
        msg = BluuMessage(subject, body, user.email)
        msg.send()

    if uad.text_notification:
        logger.info('OGT text alert sent to {0} for device {1}'. \
            format(user.cell_text_email, device_name))
        msg = BluuMessage(subject, body, user.cell_text_email)
        msg.send()


@task(name='alerts.call_ogtnm')
def alert_open_greater_than_no_motion(runner):
    uad = runner.user_alert_device
    user = uad.user
    device_name = uad.device.name
    room = uad.device.room.name
    site_name = uad.device.bluusite.name
    duration = uad.duration
    unit = uad.get_unit_display()
    timestamp = runner.since

    body = render_to_string('alerts/notifications/open_gtnm.html', {
        'user': user,
        'device_name': device_name,
        'room': room,
        'site_name': site_name,
        'timestamp': timestamp,
        'duration': duration,
        'unit': unit
    })

    subject = _(u'%(site_name)s alert - %(alert_name)s') % \
              {'site_name': site_name,
               'alert_name': _('device open too long with no motion')}

    if uad.email_notification:
        logger.info('OGTNM alert sent to {0} for device {1}'. \
            format(user.email, device_name))
        msg = BluuMessage(subject, body, user.email)
        msg.send()

    if uad.text_notification:
        logger.info('OGTNM text alert sent to {0} for device {1}'. \
            format(user.cell_text_email, device_name))
        msg = BluuMessage(subject, body, user.cell_text_email)
        msg.send()


@task(name='alerts.call_cgt')
def alert_closed_greater_than(runner):
    uad = runner.user_alert_device
    user = uad.user
    device_name = uad.device.name
    room = uad.device.room.name
    site_name = uad.device.bluusite.name
    duration = uad.duration
    unit = uad.get_unit_display()
    timestamp = runner.since

    body = render_to_string('alerts/notifications/closed_gt.html', {
        'user': user,
        'device_name': device_name,
        'room': room,
        'site_name': site_name,
        'timestamp': timestamp,
        'duration': duration,
        'unit': unit
    })

    subject = _(u'%(site_name)s alert - %(alert_name)s') % \
              {'site_name': site_name,
               'alert_name': _('device closed too long')}

    if uad.email_notification:
        logger.info('CGT alert sent to {0} for device {1}'. \
            format(user.email, device_name))
        msg = BluuMessage(subject, body, user.email)
        msg.send()

    if uad.text_notification:
        logger.info('CGT text alert sent to {0} for device {1}'. \
            format(user.cell_text_email, device_name))
        msg = BluuMessage(subject, body, user.cell_text_email)
        msg.send()


@task(name='alerts.call_mir')
def alert_mir(uar, status):
    """
    Sends MOTION IN ROOM alert.
    This one is send immediately after a motion status arrives
    """
    user = uar.user
    site = status.device.bluusite
    # check here because this alert isn't called via alert runner
    if (user_alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        device_name = status.device.name
        room = uar.room.name
        site_name = status.device.bluusite.name
        timestamp = status.timestamp

        body = render_to_string('alerts/notifications/mir.html', {
            'user': user,
            'device_name': device_name,
            'room': room,
            'site_name': site_name,
            'timestamp': timestamp
        })
        subject = render_to_string('alerts/notifications/notification_title.html',
                                   dict(site_name=site_name,
                                        alert_name=_('motion in room')))

        if uar.email_notification:
            logger.info('Motion in room {0} alert sent to {1} for device {2}'.
            format(room, user.email, device_name))
            msg = BluuMessage(subject, body, user.email)
            msg.send()

        if uar.text_notification:
            logger.info('Motion in room {0} text alert sent to {1} for device {2}'.
            format(room, user.cell_text_email, device_name))
            msg = BluuMessage(subject, body, user.cell_text_email)
            msg.send()


@task(name='alerts.call_nmirgt')
def alert_nomotion_greater_than(runner):
    uar = runner.user_alert_room
    user = uar.user
    room = uar.room.name
    site_name = uar.room.bluusite.name
    duration = uar.duration
    unit = uar.get_unit_display()
    timestamp = runner.since

    body = render_to_string('alerts/notifications/motion_nmirgt.html', {
        'user': user,
        'room': room,
        'site_name': site_name,
        'timestamp': timestamp,
        'duration': duration,
        'unit': unit
    })

    subject = _(u'%(site_name)s alert - %(alert_name)s') % \
              {'site_name': site_name,
               'alert_name': _('no motion in room for too much time')}

    if uar.email_notification:
        logger.info('NMIRGT alert sent to {0} for room {1}'.format(
            user.email,
            room))
        msg = BluuMessage(subject, body, user.email)
        msg.send()

    if uar.text_notification:
        logger.info('NMIRGT text alert sent to {0} for room {1}'.format(
            user.cell_text_email,
            room))
        msg = BluuMessage(subject, body, user.cell_text_email)
        msg.send()


@task(name='alerts.call_aiplt')
def alert_active_in_period_less_than(runner):
    uad = runner.user_alert_device
    user = uad.user
    device_name = uad.device.name
    room = uad.device.room.name
    site_name = uad.device.bluusite.name
    duration = uad.duration
    unit = uad.get_unit_display()
    timestamp = runner.since

    body = render_to_string('alerts/notifications/open_aiplt.html', {
        'user': user,
        'device_name': device_name,
        'room': room,
        'site_name': site_name,
        'timestamp': timestamp,
        'duration': duration,
        'unit': unit,
        'period': settings.ALERT_PERIOD / 60
    })

    subject = _(u'%(site_name)s alert - %(alert_name)s') % \
              {'site_name': site_name,
               'alert_name': _('active less than expected in a period')}

    if uad.email_notification:
        logger.info('AIPLT alert sent to {0} for device {1}'.format(user.email,
                                                                    device_name))
        msg = BluuMessage(subject, body, user.email)
        msg.send()

    if uad.text_notification:
        logger.info('AIPLT text alert sent to {0} for device {1}'.
        format(user.cell_text_email, device_name))
        msg = BluuMessage(subject, body, user.cell_text_email)
        msg.send()


@task(name='alerts.call_aipgt')
def alert_active_in_period_greater_than(runner):
    uad = runner.user_alert_device
    user = uad.user
    device_name = uad.device.name
    room = uad.device.room.name
    site_name = uad.device.bluusite.name
    duration = uad.duration
    unit = uad.get_unit_display()
    timestamp = runner.since

    body = render_to_string('alerts/notifications/open_aipgt.html', {
        'user': user,
        'device_name': device_name,
        'room': room,
        'site_name': site_name,
        'timestamp': timestamp,
        'duration': duration,
        'unit': unit,
        'period': settings.ALERT_PERIOD / 60
    })

    subject = _(u'%(site_name)s alert - %(alert_name)s') % \
              {'site_name': site_name,
               'alert_name': _('active greater than expected in a period')}

    if uad.email_notification:
        logger.info('AIPGT alert sent to {0} for device {1}'.format(user.email,
                                                                    device_name))
        msg = BluuMessage(subject, body, user.email)
        msg.send()

    if uad.text_notification:
        logger.info('AIPGT text alert sent to {0} for device {1}'.
        format(user.cell_text_email, device_name))
        msg = BluuMessage(subject, body, user.cell_text_email)
        msg.send()


@task(name='alerts.call_wgt')
def alert_wgt(uas, status):
    """
    Sends notification that weight is greater than
    """
    user = uas.user
    site = uas.device.bluusite
    if (user_alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        device_name = uas.device.name
        room = uas.device.room.name
        site_name = uas.device.bluusite.name
        timestamp = status.timestamp
        weight = '{:.2f}'.format(status.float_data)
        weight_guard = uas.weight

        body = render_to_string('alerts/notifications/wgt.html', {
            'user': user,
            'device_name': device_name,
            'room': room,
            'site_name': site_name,
            'timestamp': timestamp,
            'weight': weight,
            'weight_guard': weight_guard
        })
        subject = render_to_string('alerts/notifications/notification_title.html',
                                   dict(site_name=site_name,
                                        alert_name=_(
                                            'weight greater than expected')))

        if uas.email_notification:
            logger.info('WGT alert sent to {0} for device {1}'.format(user.email,
                                                                      device_name))
            msg = BluuMessage(subject, body, user.email)
            msg.send()

        if uas.text_notification:
            logger.info('WGT text alert sent to {0} for device {1}'.format(
                user.cell_text_email, device_name))
            msg = BluuMessage(subject, body, user.cell_text_email)
            msg.send()


@task(name='alerts.call_wlt')
def alert_wlt(uas, status):
    """
    Sends notification that weight is less than
    """
    user = uas.user
    site = uas.device.bluusite
    if (user_alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        device_name = uas.device.name
        room = uas.device.room.name
        site_name = uas.device.bluusite.name
        timestamp = status.timestamp
        weight = '{:.2f}'.format(status.float_data)
        weight_guard = uas.weight

        body = render_to_string('alerts/notifications/wlt.html', {
            'user': user,
            'device_name': device_name,
            'room': room,
            'site_name': site_name,
            'timestamp': timestamp,
            'weight': weight,
            'weight_guard': weight_guard
        })
        subject = render_to_string('alerts/notifications/notification_title.html',
                                   dict(site_name=site_name,
                                        alert_name=_('weight less than expected')))

        if uas.email_notification:
            logger.info('WLT alert sent to {0} for device {1}'.format(user.email,
                                                                      device_name))
            msg = BluuMessage(subject, body, user.email)
            msg.send()

        if uas.text_notification:
            logger.info('WLT text alert sent to {0} for device {1}'.format(
                user.cell_text_email, device_name))
            msg = BluuMessage(subject, body, user.cell_text_email)
            msg.send()


@task(name='alerts.call_su')
def alert_su(uas, status):
    """
    Sends notification that scale has been used
    """
    user = uas.user
    site = uas.device.bluusite
    if (user_alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        device_name = uas.device.name
        room = uas.device.room.name
        site_name = uas.device.bluusite.name
        timestamp = status.timestamp

        body = render_to_string('alerts/notifications/su.html', {
            'user': user,
            'device_name': device_name,
            'room': room,
            'site_name': site_name,
            'timestamp': timestamp,
        })
        subject = render_to_string('alerts/notifications/notification_title.html',
                                   dict(site_name=site_name,
                                        alert_name=_('scale used')))

        if uas.email_notification:
            logger.info('SU alert sent to {0} for device {1}'.format(user.email,
                                                                     device_name))
            msg = BluuMessage(subject, body, user.email)
            msg.send()

        if uas.text_notification:
            logger.info('SU text alert sent to {0} for device {1}'.format(
                user.cell_text_email, device_name))
            msg = BluuMessage(subject, body, user.cell_text_email)
            msg.send()


@task(name='alerts.call_sys_battery_low')
def alert_sys_battery_low(user, device, timestamp, period=None):
    """
    Sends notification about battery low
    """
    site = device.bluusite
    if (user_alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        device_name = device.name
        room = device.room
        site_name = site.name
        timestamp = timestamp

        body = render_to_string('alerts/notifications/sys_battery_low.html', {
            'user': user,
            'device_name': device_name,
            'room': room,
            'site_name': site_name,
            'timestamp': timestamp,
            'period': period
        })
        subject = render_to_string('alerts/notifications/notification_title.html',
                                   dict(site_name=site_name,
                                        alert_name=_('battery low')))

        if user.email:
            logger.info('Sys battery low alert sent to {0} for device {1}'.format(user.email,
                                                                     device_name))
            msg = BluuMessage(subject, body, user.email)
            msg.send()

        if user.cell_text_email:
            logger.info('Sys battery low text alert sent to {0} for device {1}'.format(
                user.cell_text_email, device_name))
            msg = BluuMessage(subject, body, user.cell_text_email)
            msg.send()


@task(name='alerts.call_sys_device_offline')
def alert_sys_device_offline(user, device, timestamp, period=None):
    """
    Sends notification about device offline
    """
    site = device.bluusite
    if (user_alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        device_name = device.name
        room = device.room
        site_name = site.name
        timestamp = timestamp

        body = render_to_string('alerts/notifications/sys_device_offline.html', {
            'user': user,
            'device_name': device_name,
            'room': room,
            'site_name': site_name,
            'timestamp': timestamp,
            'period': period
        })
        subject = render_to_string('alerts/notifications/notification_title.html',
                                   dict(site_name=site_name,
                                        alert_name=_('device offline')))

        if user.email:
            logger.info('Sys device offline alert'
                        ' sent to {0} for device {1}'.format(user.email,
                                                             device_name))
            msg = BluuMessage(subject, body, user.email)
            msg.send()

        if user.cell_text_email:
            logger.info('Sys device offline text alert sent to {0} for'
                        ' device {1}'.format(user.cell_text_email, device_name))
            msg = BluuMessage(subject, body, user.cell_text_email)
            msg.send()


@task(name='alerts.call_sys_bluusite_offline')
def alert_sys_bluusite_offline(user, bluusite, timestamp, period=None):
    """
    Sends notification about device offline
    """
    site = bluusite
    if (user_alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        site_name = site.name
        timestamp = timestamp

        body = render_to_string('alerts/notifications/sys_bluusite_offline.html', {
            'user': user,
            'site_name': site_name,
            'timestamp': timestamp,
            'period': period
        })
        subject = render_to_string('alerts/notifications/notification_title.html',
                                   dict(site_name=site_name,
                                        alert_name=_('site offline')))

        if user.email:
            logger.info('Sys bluusite offline alert'
                        ' sent to {0} for device {1}'.format(
                user.email, bluusite.name))
            msg = BluuMessage(subject, body, user.email)
            msg.send()

        if user.cell_text_email:
            logger.info('Sys bluusite offline text alert sent to {0} for'
                        ' device {1}'.format(
                user.cell_text_email, bluusite.name))
            msg = BluuMessage(subject, body, user.cell_text_email)
            msg.send()


@task(name='alerts.call_sys_tamper')
def alert_sys_tamper(user, device, timestamp):
    """
    Sends notification about tamper
    """
    site = device.bluusite
    if (user_alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        device_name = device.name
        room = device.room
        site_name = site.name
        timestamp = timestamp

        body = render_to_string('alerts/notifications/sys_tamper.html', {
            'user': user,
            'device_name': device_name,
            'room': room,
            'site_name': site_name,
            'timestamp': timestamp,
        })
        subject = render_to_string('alerts/notifications/notification_title.html',
                                   dict(site_name=site_name,
                                        alert_name=_('tamper')))

        if user.email:
            logger.info('Sys tamper alert sent to {0} for device {1}'.format(user.email,
                                                                     device_name))
            msg = BluuMessage(subject, body, user.email)
            msg.send()

        if user.cell_text_email:
            logger.info('Sys tamper text alert sent to {0} for device {1}'.format(
                user.cell_text_email, device_name))
            msg = BluuMessage(subject, body, user.cell_text_email)
            msg.send()


@task(name="alerts.trigger_runners")
def alert_trigger_runners():
    """
    Periodically check alert runner table and trigger alerts.
    """
    from alerts.models import AlertRunner, Alert

    now = datetime.now()
    ars = AlertRunner.objects.select_related().filter(is_active=True,
                                                      when__lte=now)
    for ar in ars:
        # trigger action for specific alert runner
        if ar.user_alert_device is not None:
            # check if user alerts or dealer alerts are allowed
            # for this bluusite
            user = ar.user_alert_device.user
            site = ar.user_alert_device.device.bluusite
            if (user_alerts_allowed(user, site) or
                    dealer_alerts_allowed(user, site)):
                # if OGT
                if ar.user_alert_device.alert.alert_type == Alert.OPEN_GREATER_THAN:
                    alert_open_greater_than.delay(ar)
                    ar.is_active = False
                    ar.save()
                # if OGTNM
                elif ar.user_alert_device.alert.alert_type == \
                        Alert.OPEN_GREATER_THAN_NO_MOTION:
                    alert_open_greater_than_no_motion.delay(ar)
                    ar.is_active = False
                    ar.save()
                # if CGT
                elif ar.user_alert_device.alert.alert_type \
                        == Alert.CLOSED_GREATER_THAN:
                    alert_closed_greater_than.delay(ar)
                    ar.is_active = False
                    ar.save()
                # if AIPLT
                elif ar.user_alert_device.alert.alert_type \
                        == Alert.ACTIVE_IN_PERIOD_LESS_THAN:
                    alert_active_in_period_less_than.delay(ar)
                    ar.is_active = False
                    ar.save()
                # if AIPGT
                elif ar.user_alert_device.alert.alert_type \
                        == Alert.ACTIVE_IN_PERIOD_GREATER_THAN:
                    alert_active_in_period_greater_than.delay(ar)
                    ar.is_active = False
                    ar.save()
            else:
                # alerts are not active for current site or
                # user is no longer allowed to receive them
                # so mark alert runner as inactive
                ar.is_active = False
                ar.save()
        elif ar.user_alert_room is not None:
            # if NoMotionGreaterThan
            user = ar.user_alert_room.user
            site = ar.user_alert_room.room.bluusite
            if (user_alerts_allowed(user, site) or
                    dealer_alerts_allowed(user, site)):
                if ar.user_alert_room.alert.alert_type \
                        == Alert.NOMOTION_IN_ROOM_GREATER_THAN:
                    alert_nomotion_greater_than.delay(ar)
                    ar.is_active = False
                    ar.save()
            else:
                ar.is_active = False
                ar.save()


@task(name="alerts.clean_runners")
def alert_clear_runners():
    """
    Removes alert runners that were run and are older than one day.
    """
    from alerts.models import AlertRunner, Alert

    now = datetime.now()
    t = timedelta(days=1)
    AlertRunner.objects.select_related().filter(is_active=False,
                                                when__lt=now - t).delete()
    logger.info('Cleaned inactive alert runners')



@task(name="alerts.trigger_system_runners")
def alert_trigger_system_runners():
    """
    Periodically check system alert runner table and trigger alerts.
    """
    from alerts.models import SystemAlertRunner, Alert

    now = datetime.now()
    # if there is site offline alert to be run then delete all device offline
    # alerts for this site
    ars = SystemAlertRunner.objects.select_related('bluusite').filter(
        is_active=True,
        when__lte=now,
        alert__alert_type=Alert.SYSTEM_SITE_OFFLINE)

    for ar in ars:
        SystemAlertRunner.objects.filter(
            bluusite=ar.bluusite,
            is_active=True,
            when__lte=now,
            alert__alert_type=Alert.SYSTEM_DEVICE_OFFLINE,
            device__isnull=False).delete()

    ars = SystemAlertRunner.objects.select_related().filter(is_active=True,
                                                            when__lte=now)
    for ar in ars:
        # trigger action for specific alert runner

        # check if user alerts or dealer alerts are allowed
        # for this bluusite
        bluusite = ar.bluusite
        if alerts_allowed(bluusite):
            # if battery
            if ar.alert.alert_type == Alert.SYSTEM_BATTERY:
                SystemAlertRunner.objects.send_battery_alerts(ar.device, now,
                                                              ar.period)
                ar.is_active = False
                ar.save()
            if ar.alert.alert_type == Alert.SYSTEM_SITE_OFFLINE:
                SystemAlertRunner.objects.send_bluusite_offline_alerts(
                    ar.bluusite, now, ar.period)
                ar.is_active = False
                ar.save()
            if ar.alert.alert_type == Alert.SYSTEM_DEVICE_OFFLINE:
                SystemAlertRunner.objects.send_device_offline_alerts(
                    ar.device, now, ar.period)
                ar.is_active = False
                ar.save()
        else:
            # alerts are not active for current site
            # so mark alert runner as inactive
            ar.is_active = False
            ar.save()


@task(name="alerts.clean_system_runners")
def sys_alert_clear_runners():
    """
    Removes system alert runners that were run and are older than one day.
    """
    from alerts.models import SystemAlertRunner, Alert

    now = datetime.now()
    t = timedelta(days=1)
    SystemAlertRunner.objects.select_related().filter(is_active=False,
                                                when__lt=now - t).delete()
    logger.info('Cleaned inactive system alert runners')


@task(name='alerts.call_mirgt')
def alert_mirgt(uar, timestamp):
    """
    Sends notification about motion in room greater than
    """
    site = uar.room.bluusite
    user = uar.user
    if (user_alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        room = uar.room.name
        site_name = site.name
        duration = uar.duration
        unit = uar.get_unit_display()
        period = settings.ALERT_PERIOD / 60

        body = render_to_string('alerts/notifications/motion_mirgt.html', {
            'user': user,
            'room': room,
            'site_name': site_name,
            'timestamp': timestamp,
            'duration': duration,
            'unit': unit,
            'period': period,
            'period_unit': _('hours')
        })

        subject = render_to_string('alerts/notifications/notification_title.html',
                                   dict(site_name=site_name,
                                        alert_name=_('to much motion in room')))

        if user.email:
            logger.info('MIRGT alert sent to {0} for device {1}'.format(
                user.email, room))
            msg = BluuMessage(subject, body, user.email)
            msg.send()

        if user.cell_text_email:
            logger.info('MIRGT text alert sent to {0} for device {1}'.format(
                user.cell_text_email, room))
            msg = BluuMessage(subject, body, user.cell_text_email)
            msg.send()



@task(name='alerts.call_mirlt')
def alert_mirlt(uar, timestamp):
    """
    Sends notification about motion in room less than
    """
    site = uar.room.bluusite
    user = uar.user
    if (user_alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        room = uar.room.name
        site_name = site.name
        duration = uar.duration
        unit = uar.get_unit_display()
        period = settings.ALERT_PERIOD / 60

        body = render_to_string('alerts/notifications/motion_mirlt.html', {
            'user': user,
            'room': room,
            'site_name': site_name,
            'timestamp': timestamp,
            'duration': duration,
            'unit': unit,
            'period': period,
            'period_unit': _('hours')
        })

        subject = render_to_string('alerts/notifications/notification_title.html',
                                   dict(site_name=site_name,
                                        alert_name=_('to much motion in room')))

        if user.email:
            logger.info('MIRLT alert sent to {0} for device {1}'.format(
                user.email, room))
            msg = BluuMessage(subject, body, user.email)
            msg.send()

        if user.cell_text_email:
            logger.info('MIRLT text alert sent to {0} for device {1}'.format(
                user.cell_text_email, room))
            msg = BluuMessage(subject, body, user.cell_text_email)
            msg.send()


@task(name="alerts.trigger_motion_in_room_checks")
def alert_trigger_motion_in_room_checks():
    """
    Periodically check if motion in rooms is gt or lt.
    """
    from alerts.models import AlertRunner, Alert, TIME_UNITS
    period = settings.ALERT_PERIOD
    period = timedelta(minutes=period)

    now = datetime.now()

    for room in Room.objects.filter(device__isnull=False).distinct():
        activity = room.get_motion_activity_time(till=datetime.now())
        for uar in room.useralertroom_set.select_related('alert'):
            kwargs = {TIME_UNITS[uar.unit]: uar.duration}
            duration = timedelta(**kwargs)

            if uar.alert.alert_type == Alert.MOTION_IN_ROOM_GREATER_THAN:
                if activity > duration:
                    alert_mirgt.delay(uar, now)
            elif uar.alert.alert_type == Alert.MOTION_IN_ROOM_LESS_THAN:
                if activity < duration:
                    alert_mirlt.delay(uar, now)
