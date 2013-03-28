from __future__ import unicode_literals
from datetime import datetime, timedelta
import calendar
import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from django.contrib.auth.models import Group
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db.models import F

from autoslug import AutoSlugField
from registration import signals
from grontextual.models import UserObjectGroup
from utils.misc import remove_orphaned_obj_perms
from utils.countries import CountryField
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^utils\.countries\.CountryField"])

from utils.misc import DateTimeEncoder
from accounts.models import BluuUser
from invitations.models import InvitationKey
from devices.models import (Device, Status, DeviceType)


def get_site_slug(instance):
    fmt = "{}{}".format(instance.first_name[:2], instance.last_name[:2])
    return fmt


class BluuSite(models.Model):
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    slug = AutoSlugField(populate_from=get_site_slug, unique=True)
    middle_initial = models.CharField(
                _('middle initial'), max_length=2, 
                blank=True)
    company = models.ForeignKey(
                "companies.Company", verbose_name=_('company'),
                on_delete=models.PROTECT)
    users = models.ManyToManyField(
                settings.AUTH_USER_MODEL,
                blank=True,
                null=True,
                verbose_name=_('users'),
                through='BluuSiteAccess')
    street = models.CharField(_('street'), max_length=50)
    city = models.CharField(_('city'), max_length=50)
    state = models.CharField(_('state'), max_length=50)
    zip_code = models.CharField(_('zip code'), max_length=7)
    country = CountryField(_('country'), default='US')
    phone = models.CharField(_('phone'), max_length=10, blank=True)
    last_seen = models.DateTimeField(_('last seen'), null=True, blank=True)
    ip = models.IPAddressField(_('ip address'), null=True, blank=True)
    many_inhabitants = models.BooleanField(
                   _('more than one person living in this house'),
                   default=False)

    class Meta:
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")
        permissions = (
            ("browse_bluusites", "Can browse sites"),
            ("view_bluusite", "Can view site"),
            ("browse_devices", "Can browse devices"),
            ("add_device", "Can add device"),
            ("change_device", "Can change device"),
            ("delete_device", "Can delete device"),
            ("browse_rooms", "Can browse rooms"),
            ("add_room", "Can add room"),
            ("change_room", "Can change room"),
            ("delete_room", "Can delete room"),
        )

    def __unicode__(self):
        return u'%s | %s | %s' % (
            unicode(self.pk),
            unicode(getattr(self, 'first_name', '---')),
            unicode(getattr(self, 'last_name', '---')))

    @models.permalink
    def get_absolute_url(self):
        return ('site_edit', [str(self.id)])

    @property
    def get_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    @property
    def is_online(self):
        if (datetime.now() - self.last_seen) > timedelta(hours = 1):
            return False
        return True

    def get_last_activity(self):
        devices = self.device_set.filter(device_type__name=DeviceType.MOTION)
        try:
            return devices.latest('last_seen')
        except ObjectDoesNotExist:
            return None

    def get_last_weight(self):
        devices = self.device_set.filter(device_type__name=DeviceType.SCALE)
        try:
            last_scale = devices.latest('last_seen')
            status = last_scale.status_set.filter(float_data__isnull=False).\
                                                               latest('created')
            return status.float_data
        except ObjectDoesNotExist:
            return None

    def get_last_weights(self, count=7):
        ret = []
        try:
            scale_statuses = Status.objects.filter(
                    device__bluusite=self,
                    device__device_type__name=DeviceType.SCALE,
                    float_data__isnull=False).order_by('-created')[:count]
            for status in scale_statuses:
                dat = calendar.timegm(status.timestamp.timetuple()) * 1000
                ret.append((dat, status.float_data))
            return json.dumps(ret)
        except ObjectDoesNotExist:
            return None

    def get_last_bloodpressures(self, count=7):
        ret = []
        try:
            scale_statuses = Status.objects.filter(
                    device__bluusite=self,
                    device__device_type__name=DeviceType.BLOOD_PRESSURE,
                    float_data__isnull=False).order_by('-created')[:count]
            for status in scale_statuses:
                dat = calendar.timegm(status.timestamp.timetuple()) * 1000
                ret.append((dat, status.float_data))
            return json.dumps(ret)
        except ObjectDoesNotExist:
            return None

    def get_battery_statuses(self):
        low_counter = -1
        if self.device_set.exists():
            low_counter = 0

        for device in self.device_set.all():
            try:
                status = device.status_set.latest('created')
                if status.battery:
                    low_counter += 1
            except ObjectDoesNotExist:
                pass
        return low_counter

    @property
    def has_activities(self):
        return Status.objects.filter(
                device__bluusite=self,
                device__device_type__name=DeviceType.MOTION,
                ).exists()

    def get_activity(self):
        rooms = {}
        for room in Room.objects.filter(bluusite=self):
            rooms[room.pk]=0

        last_activity = None
        last_room_activity = {}
        timegap = timedelta(minutes=settings.MOTION_TIME_GAP)

        activities = Status.objects.filter(
                device__bluusite=self,
                device__device_type__name=DeviceType.MOTION,
                action=F('device__active')
                ).order_by('timestamp')
        for activity in activities:
            if self.many_inhabitants:
                # there is more than one inhabitant in a house so
                # the timers should overlap and not cancel each other
                # check current room
                room = activity.device.room
                # get last activity in this room
                last_activity = last_room_activity.get(room.pk, None)

            if last_activity:
                room = last_activity.device.room
                # store time since last activity
                # but no more than time gap
                last_time = last_activity.timestamp 
                new_time = activity.timestamp
                diff = new_time - last_time

                # if there is no activity for a time longer than timegap
                # then only count timegap as activity time
                if diff > timegap:
                    diff = timegap
                rooms[room.pk] += diff.total_seconds()

            last_room_activity[room.pk] = activity
            last_activity = activity

        # add time for latest activities to the total
        if self.many_inhabitants:
            for activity in last_room_activity.values():
                diff = datetime.now() - activity.timestamp
                if diff > timegap:
                    diff = timegap
                rooms[activity.device.room.pk] += diff.total_seconds()
        else:
            diff = datetime.now() - last_activity.timestamp
            if diff > timegap:
                diff = timegap
            rooms[last_activity.device.room.pk] += diff.total_seconds()

        ret = []
        for room_pk in rooms.keys():
            room = Room.objects.get(pk=room_pk)
            ret.append({'label': room.name, 'data': rooms[room_pk]})
        json_ret = json.dumps(ret);
        return mark_safe(json_ret)

    def get_sleeps(self, bed_pk=None):
        """
        Returns sleep data calculated per bed. Data looks like:
        {1: [
              {u'timestamp': datetime.datetime(2013, 3, 27, 19, 17, 0, 827098),
               u'length': 22200.0
              },
              {u'timestamp': datetime.datetime(2013, 3, 27, 21, 37, 0, 827098),
               u'length': 7200.0}], 2: [{u'timestamp': None, u'length': 0
              }
            ]
        }
        """
        beds = {}
        sleep_duration = timedelta(minutes=settings.SLEEP_DURATION) 
        sleep_duration_seconds = sleep_duration.total_seconds() 
        timegap = timedelta(minutes=settings.SLEEP_TIME_GAP)
        if bed_pk:
            bed_list = self.device_set.filter(pk=bed_pk)
        else:
            bed_list = self.device_set.filter(device_type__name=DeviceType.BED)

        for bed in bed_list:
            beds[bed.pk]={'sleeps': [0]}
            beds[bed.pk]=[{'length': 0, 'timestamp': None}]

            last_activity = None
            last_sleep = 0
            activities = Status.objects.filter(
                    device__bluusite=self,
                    device=bed,
                    ).order_by('timestamp')
            for activity in activities:
                if last_activity:
                    if last_activity.action == bed.active and \
                            activity.action == bed.inactive:
                        # someone was lying in a bed and has just stand up
                        diff = activity.timestamp - last_activity.timestamp
                        beds[bed.pk][-1]['length'] += diff.total_seconds()
                        beds[bed.pk][-1]['timestamp'] = activity.timestamp
                    elif last_activity.action == bed.inactive and \
                            activity.action == bed.active:
                        # someone was absent in a bed and has just laid into it
                        # we have to check whether the gap between last
                        # activity timestamp and current action timestamp
                        # is less or equal to SLEEP_TIME_GAP
                        # if it is then we count this time to 
                        # total sleep length
                        diff = activity.timestamp - last_activity.timestamp
                        if diff <= timegap:
                            beds[bed.pk][-1]['length'] += diff.total_seconds()
                            beds[bed.pk][-1]['timestamp'] = activity.timestamp
                        else:
                            # break took more than SLEEP_TIME_GAP -> start new sleep
                            if beds[bed.pk][-1]['length'] > sleep_duration_seconds:
                                last_sleep = beds[bed.pk][-1]['length']
                            beds[bed.pk].append({'length': 0, 'timestamp': None})
                    elif last_activity.action == bed.active and \
                            activity.action == bed.active:
                        # dobule active action - this shouldn't happend
                        # but is not impossible - fe. lost close message
                        diff = activity.timestamp - last_activity.timestamp
                        beds[bed.pk][-1]['length'] += diff.total_seconds()
                        beds[bed.pk][-1]['timestamp'] = activity.timestamp
                    #elif last_activity.action == bed.inactive and \
                        #    activity.action == bed.inactive:
                        # dobule inactive action - this shouldn't happend
                        # but is not impossible - fe. lost active message
                        # We can assume here that in fact active was lost
                        # however its better to just do nothing because we're
                        # not sure if the assumption is correct
                last_activity = activity

            # count also time since last action if it's not a close
            if last_activity and (last_activity.action == bed.active):
                diff = datetime.now() - last_activity.timestamp
                if diff <= timegap:
                    beds[bed.pk][-1]['length'] += diff.total_seconds()
                    beds[bed.pk][-1]['timestamp'] = activity.timestamp
                else:
                    # break took more than SLEEP_TIME_GAP -> start new sleep
                    if beds[bed.pk][-1]['length'] > sleep_duration_seconds:
                        last_sleep = beds[bed.pk][-1]['length']
                    beds[bed.pk].append({'length': 0, 'timestamp': None})

            # if calculated sleep is shorter than SLEEP_DURATION then use
            # last_sleep value
            if beds[bed.pk][-1]['length'] <= sleep_duration_seconds and \
                                       last_sleep > beds[bed.pk][-1]['length']:
                del(beds[bed.pk][-1])
        return beds

    def get_last_sleep(self):
        """
        Returns duration of last sleep in seconds
        """
        beds = self.get_sleeps()
        last = None
        for bed_key in beds.keys():
            bed = beds[bed_key]
            if last is None:
                last = bed
            else:
                bed_stamp = bed[-1].get('timestamp')
                last_stamp = last[-1].get('timestamp')
                if (bed_stamp is not None and last_stamp is not None) and\
                    bed_stamp > last_stamp:
                    last = bed
        return last[-1]['length']

    def assign_user(self, assignee, email, group):
        """
        Assigns or invites a user to a site
        """
        try:
            user = BluuUser.objects.get(email__iexact=email)
        except BluuUser.DoesNotExist:
            user = None

        try:
            BluuSiteAccess.objects.get(
                (Q(user=user) & Q(user__isnull=False)) | Q(email__iexact=email),
                site=self)
        except BluuSiteAccess.DoesNotExist:
            # User doesn't have access
            ca = BluuSiteAccess.objects.create(user=user, email=email,
                                               group=group, site=self)
            if user is None:
                self.invite_user(assignee, obj=ca)
            return True

        return False

    def add_user(self, user, group):
        BluuSiteAccess.objects.create(user=user, email=user.email,
                                           group=group, site=self)

    def invite_user(self, inviter, obj):
        invitation = InvitationKey.objects.create_invitation(
                user=inviter,
                content_object=obj
                )
        invitation.send_to(obj.email)


class BluuSiteAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    site = models.ForeignKey(BluuSite)
    group = models.ForeignKey(Group)
    email = models.EmailField(_('e-mail'), blank=True, null=True)
    invitations = generic.GenericRelation('invitations.InvitationKey')

    class Meta:
        verbose_name = _("site access")
        verbose_name_plural = _("site accesses")
        unique_together = (("site", "user"), ("site", "email"))
        permissions = (
            ("browse_bluusiteaccesses", "Can browse bluusite accesses"),
            ("view_bluusiteaccess", "Can view bluusite access"),
        )

    def __unicode__(self):
        return u'%s | %s | %s' % (
            unicode(self.site),
            unicode(getattr(self, 'user', '---')),
            unicode(getattr(self, 'email', '---')))
    
    @property
    def get_email(self):
        if self.user is not None:
            return self.user.email
        return self.email


class Room(models.Model):
    bluusite = models.ForeignKey(BluuSite)
    name = models.CharField(_('name'), max_length=255)

    def __unicode__(self):
        return u'%s' % unicode(self.name)
 
    @models.permalink
    def get_absolute_url(self):
        return ('room_edit', [str(self.bluusite_id), str(self.id)])


@receiver(pre_save, sender=BluuSite)
def _remove_access_for_company_users_on_new_site(sender, instance, *args, **kwargs):
    """
    When site is reassigned (assigned to other company) then
    remove perms.
    """
    if instance.pk:
        old_site = BluuSite.objects.get(pk=instance.pk)
        if old_site.company != instance.company:
            """
            If company is going to be changed then remove access to the site
            for all users from old company
            """
            ctype = ContentType.objects.get(app_label="companies",
                                            model="company")
            for uog in UserObjectGroup.objects.filter(object_pk=old_site.company.pk,
                    content_type=ctype):
                UserObjectGroup.objects.remove_access(group=uog.group,
                                                      user=uog.user,
                                                      obj=old_site)


@receiver(post_save, sender=BluuSite)
def _set_access_for_company_users_on_new_site(sender, instance, *args, **kwargs):
    """
    Assign user to a group in the context of company.
    Assign user to a group in the context of sites belonging to company.
    Assign minimal permissions grouped in Company Employee group to a user.
    """
    ctype = ContentType.objects.get(app_label="companies",
                                    model="company")
    company = instance.company 
    # Assign users the same permissions to a site 
    # as they have for company the site is
    # assigned to
    for uog in UserObjectGroup.objects.filter(object_pk=company.pk,
                                              content_type=ctype):
        UserObjectGroup.objects.assign_group(group=uog.group,
                                             user=uog.user,
                                             obj=instance)


@receiver(post_save, sender=BluuSite)
def _create_webservice_user_for_site(sender, instance, created, *args, **kwargs):
    if created:
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create_user(
                            username='{0}_{1}'.format(
                                            settings.WEBSERVICE_USERNAME_PREFIX,
                                            instance.slug),
                            email='',
                            password=instance.slug,
                            first_name=instance.first_name,
                            last_name=instance.last_name)
        group = Group.objects.get(name='WebService')
        # create siteaccess
        BluuSiteAccess.objects.create(site=instance, group=group, user=user)
        # UOG permissions are assigned automatically by another signal


@receiver(pre_save, sender=BluuSiteAccess)
def _remove_access_for_site_user(sender, instance, *args, **kwargs):
    """
    Removes current accesses to a site.
    """
    if instance.pk and instance.user:
        ba = BluuSiteAccess.objects.get(pk=instance.pk)
        instance.user.remove_access(group=ba.group, obj=instance.site)
        

@receiver(post_save, sender=BluuSiteAccess)
def _assign_access_for_site_user(sender, instance, created, *args, **kwargs):
    """
    Assigns user to a group in the context of a site.
    """
    if instance.pk and instance.user:
        instance.user.assign_group(group=instance.group, obj=instance.site)


@receiver(signals.user_registered)
def _assign_access_for_newly_registered_user(sender, user, request, *args, **kwargs):
    """
    Sets user object on on access objects with user email (invitations)
    """
    for access in BluuSiteAccess.objects.filter(email=user.email):
        access.user = user
        access.save()


@receiver(pre_delete, sender=BluuSiteAccess)
def _clear_groups_for_site_user(sender, instance, *args, **kwargs):
    """
    If user is no longer in a site then remove his contextual group perms.
    """
    if instance and instance.user:
        instance.user.remove_access(group=instance.group, obj=instance.site)


# guardian
pre_delete.connect(remove_orphaned_obj_perms, sender=BluuSite)
