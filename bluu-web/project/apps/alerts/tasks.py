from celery import task
from celery.utils.log import get_task_logger
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from mailer import send_mail

from alerts.models import UserAlertDevice

logger = get_task_logger(__name__)


@task()
def alert_open(uad, status):
    user = uad.user
    device_name = uad.device.name
    room = uad.device.room.name
    timestamp = status.timestamp
    site_name = uad.device.bluusite.get_name

    body = render_to_string('alerts/notifications/open.html', {
        'user': user,
        'device_name': device_name,
        'room': room,
        'site_name': site_name,
        'timestamp': timestamp
    })

    msg_title = _(u'%(site_name)s alert - %(alert_name)s') % \
                {'site_name': site_name,
                 'alert_name': _('open')}

    msg = EmailMessage(unicode(msg_title),
                       body,
                       to=(user.email,))
    msg.content_subtype = 'html'
    return msg.send()


@task()
def alert_open_greater_than(uad, status):
    user = uad.user
    device_name = uad.device.name
    room = uad.device.room.name
    timestamp = status.timestamp
    site_name = uad.device.bluusite.get_name

    body = render_to_string('alerts/notifications/open_gt.html', {
        'user': user,
        'device_name': device_name,
        'room': room,
        'site_name': site_name,
        'timestamp': timestamp
    })

    msg_title = _(u'%(site_name)s alert - %(alert_name)s') % \
                {'site_name': site_name,
                 'alert_name': _('open')}

    msg = EmailMessage(unicode(msg_title),
                       body,
                       to=(user.email,))
    msg.content_subtype = 'html'
    return msg.send()


@task()
def alert_closed_longer_than():
    pass
