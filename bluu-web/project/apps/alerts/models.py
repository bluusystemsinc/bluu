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

    ALERT_CHOICES = (
             (OPEN, _('open')),
             (OPEN_GREATER_THAN, _('open')),
             (OPEN_GREATER_THAN_NO_MOTION, _('open greater than (no motion)')),
             (CLOSED_GREATER_THAN, _('closed greater than')),
             (ACTIVE_IN_PERIOD_GREATER_THAN, _('active in period greater than')),
             (INACTIVE_IN_PERIOD_GREATER_THAN, _('inactive in period greater than')),
             (MOTION_IN_ROOM, _('motion in room')),
             (MOTION_IN_ROOM_GREATER_THAN, _('motion in room greater than')),
             (MOTION_IN_ROOM_LESS_THAN, _('motion in room less than')),
             (NOMOTION_IN_ROOM_GREATER_THAN, _('no motion in room greater than')),
            )
    alert_type = models.CharField(_('alert'), max_length=50, choices=ALERT_CHOICES)
    device_types = models.ManyToManyField(DeviceType)

    class Meta:
        verbose_name = _("alert")
        verbose_name_plural = _("alerts")

    def __unicode__(self):
        return u'{0} | {1}'.format(unicode(self.pk),
                                   unicode(self.get_alert_display()))


class UserAlert(models.Model):
    user = models.ForeignKey(
                settings.AUTH_USER_MODEL,
                verbose_name=_('user'))
    alert = models.ForeignKey(
                Alert,
                verbose_name=_('alert'))
    duration = models.IntegerField(_('duration', blank=True, null=True))
    email_notification = models.BooleanField(_('email notification'),
                                             default=True)
    text_notification = models.BooleanField(_('text notification'),
                                            default=False)

    class Meta:
        verbose_name = _("user alert")
        verbose_name_plural = _("user alerts")

    def __unicode__(self):
        return u'{0} | {1}'.format(unicode(self.user.get_full_name()),
                                   unicode(self.alert.get_alert_type_display()))

