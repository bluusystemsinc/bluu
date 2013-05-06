from celery import task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from datetime import (datetime, timedelta)
from django.utils.translation import ugettext_lazy as _
from mailer import send_mail

from alerts.models import UserAlertDevice, AlertRunner, Alert

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
    msg_title = render_to_string('alerts/notifications/notification_title.html',
                                 dict(site_name=site_name,
                                      alert_name=_('device open')))

    msg = EmailMessage(msg_title,
                       body,
                       to=(user.email,))
    msg.content_subtype = 'html'
    logger.info('Open alert sent to {0} for device {1}'.format(user.email,
                                                               device_name))
    return msg.send()


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

    msg_title = _(u'%(site_name)s alert - %(alert_name)s') % \
                {'site_name': site_name,
                 'alert_name': _('device open too long')}

    msg = EmailMessage(unicode(msg_title),
                       body,
                       to=(user.email,))
    msg.content_subtype = 'html'
    return msg.send()


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

    msg_title = _(u'%(site_name)s alert - %(alert_name)s') % \
                {'site_name': site_name,
                 'alert_name': _('device closed too long')}

    msg = EmailMessage(unicode(msg_title),
                       body,
                       to=(user.email,))
    msg.content_subtype = 'html'
    return msg.send()


@task(name="alerts.periodic_runner")
def alert_periodic_runner():
    """
    Periodically check alert runner table and trigger alerts.
    """
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
            # if CGT
            elif ar.user_alert_device.alert.alert_type \
                    == Alert.CLOSED_GREATER_THAN:
                alert_closed_greater_than.delay(ar)
        elif ar.user_alert_room is not None:
            print 'uar'