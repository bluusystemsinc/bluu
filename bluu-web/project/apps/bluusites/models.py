from __future__ import unicode_literals
from datetime import datetime, timedelta
import calendar
import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from django.contrib.auth.models import Group
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from autoslug import AutoSlugField
from registration import signals
from grontextual.models import UserObjectGroup
from utils.misc import remove_orphaned_obj_perms
from utils.countries import CountryField
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^utils\.countries\.CountryField"])


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
        devices = self.device_set.filter(device_type__name="Motion")
        try:
            return devices.latest('last_seen')
        except ObjectDoesNotExist:
            return None

    def get_last_weight(self):
        devices = self.device_set.filter(device_type__name="Scale")
        try:
            last_scale = devices.latest('last_seen')
            status = last_scale.status_set.filter(float_data__isnull=False).\
                                                               latest('created')
            return status.float_data
        except ObjectDoesNotExist:
            return None

    def get_last_weights(self, count=7):
        from devices.models import Status
        ret = []
        try:
            scale_statuses = Status.objects.filter(
                    device__bluusite=self,
                    device__device_type__name="Scale",
                    float_data__isnull=False).order_by('-created')[:count]
            for status in scale_statuses:
                dat = calendar.timegm(status.timestamp.timetuple()) * 1000
                ret.append((dat, status.float_data))
            return json.dumps(ret)
        except ObjectDoesNotExist:
            return None

    def get_last_bloodpressures(self, count=7):
        from devices.models import Status
        ret = []
        try:
            scale_statuses = Status.objects.filter(
                    device__bluusite=self,
                    device__device_type__name="Blood pressure",
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


    def get_activity(self):
        devices = self.device_set.filter(device_type__name="Motion")
        try:
            return devices.latest('last_seen')
        except ObjectDoesNotExist:
            return None


class BluuSiteAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    site = models.ForeignKey(BluuSite)
    group = models.ForeignKey(Group)
    email = models.EmailField(_('e-mail'), blank=True, null=True)
    invitations = generic.GenericRelation('invitations.InvitationKey')

    class Meta:
        verbose_name = _("site access")
        verbose_name_plural = _("site accesses")
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
        UserObjectGroup.objects.assign(group=uog.group,
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
        instance.user.assign(group=instance.group, obj=instance.site)


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
