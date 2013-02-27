from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_save, pre_delete
from django.contrib.auth.models import Group
from django.contrib.contenttypes import generic

from registration import signals
from grontextual.models import UserObjectGroup
from utils.misc import remove_orphaned_obj_perms
from utils.countries import CountryField
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^utils\.countries\.CountryField"])


class BluuSite(models.Model):
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
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


class BluuSiteAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    site = models.ForeignKey(BluuSite)
    group = models.ForeignKey(Group)
    email = models.EmailField(_('e-mail'), blank=True, null=True)
    #invitation = models.BooleanField(_('invitation', default=False))
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


@receiver(pre_save, sender=BluuSiteAccess)
def _remove_access_for_site_user(sender, instance, *args, **kwargs):
    """
    Removes current accesses to a site.
    """
    if instance.pk and instance.user:
        instance.user.remove_all_accesses(obj=instance.site)
        

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

pre_delete.connect(remove_orphaned_obj_perms, sender=BluuSite)

