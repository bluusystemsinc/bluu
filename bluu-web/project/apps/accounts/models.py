from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import login
from django.dispatch import receiver
from registration.signals import user_activated
from django.utils.translation import ugettext_lazy as _
from countries import CountryField


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
        )


class Contract(Entity):
    #number = models.CharField(_('number'), max_length=255, blank=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    middle_initial = models.CharField(_('middle initial'), max_length=2,
        blank=True)

    def __unicode__(self):
        return str(self.pk)

    @models.permalink
    def get_absolute_url(self):
        return ('contract-edit', [str(self.id)])

    class Meta:
        verbose_name = _("Contract")
        verbose_name_plural = _("Contracts")
        permissions = (
            ("browse_contracts", "Can browse contracts"),
        )


class BluuUser(AbstractUser):
    """
    A class representing users of Bluu system.
    """

    cell = models.CharField(_('cell'), max_length=10, blank=True)
    cell_text_email = models.EmailField(_('cell text email address'),
        blank=True)
    company = models.ForeignKey(Company, blank=True, null=True,
                         related_name='company_bluuuser',
                         verbose_name=_('company'))

    contract = models.ForeignKey(Contract, blank=True, null=True,
                         related_name='contract_bluuuser',
                         verbose_name=_('contract'))

    def get_name(self):
        if self.get_full_name():
            return self.get_full_name()
        return self.username

    @property
    def get_groups(self):
        ret = u''
        groups = self.groups.all()
        for idx, group in enumerate(groups):
            ret += group.name
            if idx < len(groups) - 1:
                ret += ', '
        if not ret:
            ret = u'---'
        return ret

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        permissions = (
            ("browse_bluuusers", "Can browse users"),
            ("manage_dealers", "Can manage dealers"),
        )

#class UserProfile(models.Model):
#    user = models.ForeignKey(User, unique=True)

#User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

# force emails to be uniqe
#User._meta.get_field_by_name('email')[0]._unique = True

#http://djangosnippets.org/snippets/1960/
#@receiver(user_activated)
#def login_on_activation(sender, user, request, **kwargs):
    """Automatically login a user after activation
    """
#    user.backend='accounts.auth_backends.EmailAuthBackend'
#    login(request, user)

# When model instance is saved, trigger creation of corresponding profile
#@receiver(post_save, sender=User)
#def create_profile(sender, instance, signal, created, **kwargs):
#    """When user is created also create a matching profile."""
#    if created:
#        UserProfile(user = instance).save()
