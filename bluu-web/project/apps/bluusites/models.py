from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_save, pre_delete
from django.contrib.auth.models import Group

from grontextual.models import UserObjectGroup
from utils.misc import remove_orphaned_obj_perms
from utils.models import Entity
from companies.models import Company


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
                        through='BluuSiteAccess')

    class Meta:
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")
        permissions = (
            ("browse_bluusites", "Can browse sites"),
            ("view_bluusite", "Can view site"),
        )

    def __unicode__(self):
        return str(self.pk)

    @models.permalink
    def get_absolute_url(self):
        return ('site_edit', [str(self.id)])


class BluuSiteAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    site = models.ForeignKey(BluuSite)
    invitation = models.BooleanField(_('invitation', default=False))
    email = models.EmailField(_('e-mail'), blank=True, null=True)
    group = models.ForeignKey(Group)

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
def _revoke_access_for_site_user(sender, instance, *args, **kwargs):
    """
    Before access level is changed remove current accesses from authentication
    backend - UserObjectGroup.
    """
    if instance.pk and instance.user:
        try:
            access = BluuSiteAccess.objects.get(id=instance.pk)
            UserObjectGroup.objects.remove_access(group=access.group,
                                              user=instance.user, 
                                              obj=instance.site)
        except BluuSiteAccess.DoesNotExist:
            pass
        

@receiver(post_save, sender=BluuSiteAccess)
def _set_access_for_site_user(sender, instance, *args, **kwargs):
    """
    Assign user to a group in the context of site.
    """
    if instance.pk and instance.user:
        UserObjectGroup.objects.assign(group=instance.group, 
                                       user=instance.user, 
                                       obj=instance.site)


@receiver(pre_save, sender=BluuSite)
def _remove_access_for_company_users_on_new_site(sender, instance, *args, **kwargs):
    """
    On site reassignment (company change)
    remove perms
    """
    old_site = BluuSite.objects.get(pk=instance.pk)
    if old_site.company != instance.company:
        """
        if company changed then remove access for users from old company
        """
        for uog in UserObjectGroup.objects.filter(obj=old_site.company):
            print uog.group
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
    company = instance.company 
    #if company changed then remove access for users from old company:
    for uog in UserObjectGroup.objects.filter(obj=company):
        print uog.group
        UserObjectGroup.objects.assign(group=uog.group,
                                       user=uog.user,
                                       obj=instance)




pre_delete.connect(remove_orphaned_obj_perms, sender=BluuSite)

