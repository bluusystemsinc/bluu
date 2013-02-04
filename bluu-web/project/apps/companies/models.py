from __future__ import unicode_literals
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import Group
from utils.misc import remove_orphaned_obj_perms
from utils.countries import CountryField


class Entity(models.Model):
    street = models.CharField(_('street'), max_length=50, blank=True)
    city = models.CharField(_('city'), max_length=50, blank=True)
    state = models.CharField(_('state'), max_length=50, blank=True)
    zip_code = models.CharField(_('zip code'), max_length=7, blank=True)
    country = CountryField(_('country'), default='US', blank=True)
    phone = models.CharField(_('phone'), max_length=10, blank=True)
    email = models.EmailField(_('email address'), blank=True)

    class Meta:
        abstract = True


class Company(Entity):
    name = models.CharField(_('name'), max_length=255)
    contact_name = models.CharField(_('contact name'), max_length=255,
                         blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('company_edit', [str(self.id)])

    class Meta:
        verbose_name = _("company")
        verbose_name_plural = _("companies")
        permissions = (
            ("browse_companies", "Can browse companies"),
            ("view_company", "Can view company"),
            ("manage_company_access", "Can manage company access"),
        )


@receiver(post_save, sender=Company)
def _create_groups_for_company(sender, instance, *args, **kwargs):
    from guardian.shortcuts import assign
    dealer = Group.objects.get_or_create(name='%s: Dealer' % instance.name)[0] 
    technician = Group.objects.get_or_create(\
            name='%s: Technician' % instance.name)[0] 

    # Dealer assignments
    assign('companies.browse_companies', dealer)
    assign('bluusites.browse_bluusites', dealer)
    assign('view_company', dealer, instance)
    assign('change_company', dealer, instance)
    assign('manage_company_access', dealer, instance)

    #Technician assignments
    assign('companies.browse_companies', technician)
    assign('bluusites.browse_bluusites', technician)
    assign('view_company', technician, instance)


pre_delete.connect(remove_orphaned_obj_perms, sender=Company)

