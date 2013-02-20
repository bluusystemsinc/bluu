from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (Group, AbstractUser, UserManager)
from django.utils.translation import ugettext_lazy as _


class AppBluuUserManager(models.Manager):
    def get_query_set(self):
        return super(AppBluuUserManager, self).get_query_set().\
                     exclude(pk=-1).filter(is_staff=False, is_superuser=False)


class BluuUser(AbstractUser):
    """
    A class representing users of Bluu system.
    """
    #email = models.EmailField(_('email address'))
    cell = models.CharField(_('cell'), max_length=10, blank=True)
    cell_text_email = models.EmailField(_('cell text email address'),
            blank=True
            )

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

    @models.permalink
    def get_absolute_url(self):
        return ('bluuuser_edit', (), {"username": self.username})

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

    def get_companies(self):
        from companies.models import Company
        from grontextual.shortcuts import get_objects_for_user
        if self.has_perm('companies.view_company'):
            return Company.objects.all()
        return get_objects_for_user(self, 'companies.view_company')

    def get_sites(self):
        from bluusites.models import BluuSite
        from grontextual.shortcuts import get_objects_for_user
        if self.has_perm('bluusites.view_bluusite'):
            return BluuSite.objects.all()
        return get_objects_for_user(self, 'bluusites.view_bluusite')

