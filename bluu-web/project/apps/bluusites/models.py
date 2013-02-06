from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import Group

from utils.misc import remove_orphaned_obj_perms
from companies.models import Company, Entity


class BluuSite(Entity):
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    middle_initial = models.CharField(_('middle initial'), max_length=2, 
                        blank=True)
    company = models.ForeignKey(Company, verbose_name=_('company'))
    users = models.ManyToManyField(settings.AUTH_USER_MODEL,
                        blank=True,
                        null=True,
                        verbose_name=_('users'),
                        through='SiteAccess')

    class Meta:
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")
        permissions = (
            ("browse_bluusites", "Can browse sites"),
            ("view_bluusite", "Can view site"),
            ("manage_bluusite", "Can manage site"),
        )

    def __unicode__(self):
        return str(self.pk)

    @models.permalink
    def get_absolute_url(self):
        return ('site_edit', [str(self.id)])


class SiteAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    site = models.ForeignKey(BluuSite)


@receiver(post_save, sender=BluuSite)
def _create_groups_for_site(sender, instance, *args, **kwargs):
    from guardian.shortcuts import assign
    from guardian.shortcuts import get_groups_with_perms
    master = Group.objects.get_or_create(name='%s (%d): Master User' % \
            (instance.last_name, instance.pk))[0] 
    user = Group.objects.get_or_create(name='%s (%d): User' % \
            (instance.last_name, instance.pk))[0] 

    company_groups = get_groups_with_perms(instance.company)
    for group in company_groups:
        assign('browse_bluusites', group, instance)
        assign('view_bluusite', group, instance)
        assign('change_bluusite', group, instance)

    # Master assignments
    assign('browse_bluusites', master, instance)
    assign('view_bluusite', master, instance)
    assign('change_bluusite', master, instance)

    #Technician assignments
    assign('browse_bluusites', user, instance)
    assign('view_bluusite', user, instance)


pre_delete.connect(remove_orphaned_obj_perms, sender=BluuSite)

