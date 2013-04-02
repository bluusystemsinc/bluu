from __future__ import unicode_literals
from datetime import datetime, timedelta
import calendar

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.db.models import F

from devices.models import (Status, DeviceType)


class UserAlerts(models.Model):
    WINDOW_OPEN = 'wo'
    WINDOW_OPEN_LONGER_THAN = 'wolt'
    DOOR_OPEN = 'do'
    DOOR_OPEN_LONGER_THAN = 'dolt'
    DOOR_OPEN_LONGER_THAN_NO_MOTION = 'doltnm'


    ALERT_CHOICES = (
            (WINDOW_OPEN, _('window open'),
             WINDOW_OPEN_LONGER_THAN, _('window open longer than'),
             DOOR_OPEN, _('door open longer than'),
             DOOR_OPEN_LONGER_THAN, _('door open longer than'),
             DOOR_OPEN_LONGER_THAN_NO_MOTION, _('door open longer than'),
            ))
    users = models.ForeignKeyField(
                settings.AUTH_USER_MODEL,
                verbose_name=_('users'))
    email_notification = models.BooleanField(_('email notification'),
                                             default=True)
    text_notification = models.BooleanField(_('text notification'),
                                            default=False)
    duration = models.IntegerField(_('duration', blank=True, null=True))
    alert = models.CharField(_('alert'), choices=ALERT_CHOICES)

    class Meta:
        verbose_name = _("user alert")
        verbose_name_plural = _("user alerts")

    def __unicode__(self):
        return u'{0} | {1}'.format(unicode(self.pk),
                                   unicode(self.get_alert_display()))

    #@models.permalink
    #def get_absolute_url(self):
    #    return ('site_edit', [str(self.id)])

