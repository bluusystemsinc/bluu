from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
#from companies.models import Company
#from sites.models import Site


class BluuUser(AbstractUser):
    """
    A class representing users of Bluu system.
    """

    cell = models.CharField(_('cell'), max_length=10, blank=True)
    cell_text_email = models.EmailField(_('cell text email address'),
        blank=True)
    companies = models.ManyToManyField("companies.Company", blank=True, null=True,
                         verbose_name=_('companies'))

    sites = models.ManyToManyField("bluusites.BluuSite", blank=True, null=True,
                         verbose_name=_('sites'))

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

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        permissions = (
            ("browse_bluuusers", "Can browse users"),
            ("manage_dealers", "Can manage dealers"),
        )


