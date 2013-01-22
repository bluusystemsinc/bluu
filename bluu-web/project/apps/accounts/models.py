from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import login
from django.dispatch import receiver
from registration.signals import user_activated
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from .countries import CountryField
from south.modelsinspector import add_introspection_rules
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import Group
from django.dispatch import receiver

add_introspection_rules([], ["^accounts\.countries\.CountryField"])


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
    name = models.CharField(_('name'), max_length=255, blank=True)
    contact_name = models.CharField(_('contact name'), max_length=255,
                         blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('company-edit', [str(self.id)])

    class Meta:
        verbose_name = _("company")
        verbose_name_plural = _("companies")
        permissions = (
            ("browse_companies", "Can browse companies"),
            ("view_company", "Can view company"),
            ("manage_company_access", "Can manage company access"),
        )


class Site(Entity):
    #number = models.CharField(_('number'), max_length=255, blank=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    middle_initial = models.CharField(_('middle initial'), max_length=2,
        blank=True)
    company = models.ForeignKey(Company, verbose_name=_('company'))

    def __unicode__(self):
        return str(self.pk)

    @models.permalink
    def get_absolute_url(self):
        return ('site-edit', [str(self.id)])

    class Meta:
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")
        permissions = (
            ("browse_sites", "Can browse sites"),
            ("view_site", "Can view site"),
            ("manage_site", "Can manage site"),
        )


class BluuUser(AbstractUser):
    """
    A class representing users of Bluu system.
    """

    cell = models.CharField(_('cell'), max_length=10, blank=True)
    cell_text_email = models.EmailField(_('cell text email address'),
        blank=True)
    companies = models.ManyToManyField(Company, blank=True, null=True,
                         verbose_name=_('companies'))

    sites = models.ManyToManyField(Site, blank=True, null=True,
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


@receiver(post_save, sender=Company)
def _create_groups_for_company(sender, instance, *args, **kwargs):
    from guardian.shortcuts import assign
    dealer = Group.objects.get_or_create(name='%s: Dealer' % instance.name)[0] 
    technician = Group.objects.get_or_create(\
            name='%s: Technician' % instance.name)[0] 

    # Dealer assignments
    assign('accounts.browse_companies', dealer)
    assign('accounts.browse_sites', dealer)
    assign('view_company', dealer, instance)
    assign('change_company', dealer, instance)
    assign('manage_company_access', dealer, instance)

    #Technician assignments
    assign('accounts.browse_companies', technician)
    assign('accounts.browse_sites', technician)
    assign('view_company', technician, instance)

@receiver(post_save, sender=Site)
def _create_groups_for_site(sender, instance, *args, **kwargs):
    from guardian.shortcuts import assign
    from guardian.shortcuts import get_groups_with_perms
    master = Group.objects.get_or_create(name='%s (%d): Master User' % (instance.last_name, instance.pk))[0] 
    user = Group.objects.get_or_create(name='%s (%d): User' % (instance.last_name, instance.pk))[0] 

    company_groups = get_groups_with_perms(instance.company)
    for group in company_groups:
        print group.name
        assign('browse_sites', group, instance)
        assign('view_site', group, instance)
        assign('change_site', group, instance)

    # Master assignments
    assign('browse_sites', master, instance)
    assign('view_site', master, instance)
    assign('change_site', master, instance)

    #Technician assignments
    assign('browse_sites', user, instance)
    assign('view_site', user, instance)


@receiver(pre_delete, sender=Company)
@receiver(pre_delete, sender=Site)
def remove_orphaned_obj_perms(sender, instance, **kwargs):
    from guardian.models import UserObjectPermission
    from guardian.models import GroupObjectPermission

    filters = Q(content_type=ContentType.objects.get_for_model(instance),
        object_pk=instance.pk)
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()

#pre_delete.connect(remove_orphaned_obj_perms, sender=Company)
#pre_delete.connect(remove_orphaned_obj_perms, sender=Site)

