from celery import task
from celery.utils.log import get_task_logger
from django.conf import settings
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from utils.misc import BluuMessage


logger = get_task_logger(__name__)


def alerts_allowed(user, bluusite):
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
    if (alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        device_name = uad.device.name
        room = uad.device.room.name
        site_name = uad.device.bluusite.get_name
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
    site_name = uad.device.bluusite.get_name
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
    site_name = uad.device.bluusite.get_name
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
    site_name = uad.device.bluusite.get_name
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
    if (alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        device_name = status.device.name
        room = uar.room.name
        site_name = status.device.bluusite.get_name
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
    site_name = uar.room.bluusite.get_name
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
    site_name = uad.device.bluusite.get_name
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
    site_name = uad.device.bluusite.get_name
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
    user = uas.user
    site = uas.device.bluusite
    if (alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        device_name = uas.device.name
        room = uas.device.room.name
        site_name = uas.device.bluusite.get_name
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
    user = uas.user
    site = uas.device.bluusite
    if (alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        device_name = uas.device.name
        room = uas.device.room.name
        site_name = uas.device.bluusite.get_name
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
    user = uas.user
    site = uas.device.bluusite
    if (alerts_allowed(user, site) or
            dealer_alerts_allowed(user, site)):
        device_name = uas.device.name
        room = uas.device.room.name
        site_name = uas.device.bluusite.get_name
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
            if (alerts_allowed(user, site) or
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
            if (alerts_allowed(user, site) or
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
