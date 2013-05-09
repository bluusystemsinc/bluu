from celery import task
from celery.utils.log import get_task_logger
from django.conf import settings
from datetime import (datetime, timedelta)
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from utils.misc import BluuMessage


logger = get_task_logger(__name__)


@task(name='alerts.call_open')
def alert_open(uad, status):
    user = uad.user
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
    subject = render_to_string('alerts/notifications/notification_title.html',
                               dict(site_name=site_name,
                                    alert_name=_('device open')))

    if uad.email_notification:
        logger.info('Open alert sent to {0} for device {1}'.format(user.email,
                                                                   device_name))
        msg = BluuMessage(subject, body, user.email)
        msg.send()

    if uad.text_notification:
        logger.info('Open alert sent to {0} for device {1}'.\
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
        logger.info('OGT alert sent to {0} for device {1}'.format(user.email,
                                                                  device_name))
        msg = BluuMessage(subject, body, user.email)
        msg.send()

    if uad.text_notification:
        logger.info('OGT alert sent to {0} for device {1}'.\
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
        logger.info('OGTNM alert sent to {0} for device {1}'.\
                    format(user.email, device_name))
        msg = BluuMessage(subject, body, user.email)
        msg.send()

    if uad.text_notification:
        logger.info('OGTNM alert sent to {0} for device {1}'.\
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
        logger.info('CGT alert sent to {0} for device {1}'.\
                    format(user.email, device_name))
        msg = BluuMessage(subject, body, user.email)
        msg.send()

    if uad.text_notification:
        logger.info('CGT alert sent to {0} for device {1}'.\
                    format(user.cell_text_email, device_name))
        msg = BluuMessage(subject, body, user.cell_text_email)
        msg.send()


@task(name="alerts.trigger_runners")
def alert_trigger_runners():
    """
    Periodically check alert runner table and trigger alerts.
    """
    from alerts.models import AlertRunner, Alert
    now = datetime.now()
    # add 5 more seconds to be sure that all alert runners are used
    t = timedelta(seconds=settings.ALERT_RUNNER_TIME + 5)
    ars = AlertRunner.objects.select_related().filter(is_active=True,
                                                      when__gt=now-t,
                                                      when__lte=now
                                                      )
    for ar in ars:
        # trigger action for specific alert runner
        if ar.user_alert_device is not None:
            # if OGT
            if ar.user_alert_device.alert.alert_type == Alert.OPEN_GREATER_THAN:
                alert_open_greater_than.delay(ar)
                ar.is_active = False
                ar.save()
            # if OGTNM
            elif ar.user_alert_device.alert.alert_type ==\
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
        elif ar.user_alert_room is not None:
            print 'uar'


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
