from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import (Group, AbstractUser, UserManager)
from django.utils.translation import ugettext_lazy as _

from rest_framework.authtoken.models import Token

from grontextual.models import UserObjectGroup


class AppBluuUserManager(models.Manager):
    def get_query_set(self):
        return super(AppBluuUserManager, self).get_query_set().\
                     exclude(pk=-1).filter(is_staff=False, is_superuser=False)


class BluuUser(AbstractUser):
    """
    A class representing users of Bluu system.
    """
    cell = models.CharField(_('cell'), max_length=10, blank=True)
    cell_text_email = models.EmailField(_('cell text email address'),
                                        blank=True)

    # objects = UserManager() is required to have it treated as default manager
    objects = UserManager()
    app_users = AppBluuUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        permissions = (
            ("browse_bluuusers", "Can browse users"),
            ("manage_dealers", "Can manage dealers"),
        )

    def save(self, *args, **kwargs):
        """
        Override save to make sure that every BluuUser is assigned Base User 
        group.
        """
        super(BluuUser, self).save(*args, **kwargs) # Call the "real" save() method.
        try:
            base_user_group = Group.objects.get(name='Base User')
            self.groups.add(base_user_group)
        except Group.DoesNotExist:
            pass

    def get_absolute_url(self):
        return reverse('bluuuser_edit', args=(),
                       kwargs={"username": self.username})

    @property
    def get_name(self):
        if self.get_full_name():
            return self.get_full_name()
        return self.username

    @property
    def get_groups(self):
        ret = ''
        groups = self.groups.all()
        for idx, group in enumerate(groups):
            ret += group.name
            if idx < len(groups) - 1:
                ret += ', '
        if not ret:
            ret = '---'
        return ret

    def get_companies(self, perm='companies.view_company'):
        from companies.models import Company
        from grontextual.shortcuts import get_objects_for_user
        if self.has_perm(perm):
            return Company.objects.all()
        return get_objects_for_user(self, perm)

    def can_see_companies(self, perm='companies.view_company'):
        companies = self.get_companies(perm)
        ccount = companies.count()
        if (self.has_perm('companies.browse_companies') and
            self.has_perm('companies.add_company')) or \
           (ccount > 1):
            return {'companies': True, 'company': None}
        elif (ccount == 1) and \
            self.has_perm(perm, companies[0]):
            return {'companies': False, 'company': companies[0]}
        return {'companies': False, 'company': None}

    def get_sites(self, perm='bluusites.view_bluusite'):
        from bluusites.models import BluuSite
        from grontextual.shortcuts import get_objects_for_user
        if self.has_perm(perm):
            return BluuSite.objects.all()
        return get_objects_for_user(self, perm)

    def can_add_sites(self):
        """
        If there is a company or companies a user has permission to
        add bluusites to them then return true.
        """
        if self.get_sites(perm='bluusites.add_bluusite').count() > 0:
            return True
        return False

    def assign_group(self, obj, group):
        UserObjectGroup.objects.assign_group(group=group, 
                                            user=self, 
                                            obj=obj)

    def remove_access(self, obj, group):
        UserObjectGroup.objects.remove_access(group=group, 
                                       user=self, 
                                       obj=obj)

    def remove_all_accesses(self, obj):
        UserObjectGroup.objects.remove_all_accesses(user=self, 
                                                    obj=obj)

    def is_site_dealer(self, bluusite):
        perm = 'companies.view_company'
        if bluusite.company in self.get_companies(perm):
            return True
        return False

    def is_site_user(self, bluusite):
        perm = 'bluusites.view_bluusite'
        if bluusite in self.get_sites(perm):
            return True
        return False

    def is_site_masteruser(self, bluusite):
        perm = 'bluusites.change_bluusite'
        if bluusite in self.get_sites(perm):
            return True
        return False


@receiver(post_save, sender=BluuUser)
def _set_default_groups(sender, instance, *args, **kwargs):
    """
    Assign user to a groups.
    """
    for group_name in settings.DEFAULT_GROUPS:
        try:
            default_group = Group.objects.get(name=group_name)
            instance.groups.add(default_group)
        except Group.DoesNotExist:
            pass


@receiver(post_save, sender=BluuUser)
def _set_accesses(sender, instance, created, *args, **kwargs):
    """
    Assign user to a groups.
    """
    for group_name in settings.DEFAULT_GROUPS:
        try:
            default_group = Group.objects.get(name=group_name)
            instance.groups.add(default_group)
        except Group.DoesNotExist:
            pass


@receiver(post_save, sender=BluuUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        if instance.username.startswith(settings.WEBSERVICE_USERNAME_PREFIX):
            Token.objects.create(user=instance)
