from __future__ import unicode_literals
from django.core.exceptions import NON_FIELD_ERRORS
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_save, pre_delete
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.conf import settings

from grontextual.models import UserObjectGroup
from utils.misc import remove_orphaned_obj_perms
from utils.models import Entity


class Company(Entity):
    name = models.CharField(_('name'), max_length=255)
    contact_name = models.CharField(_('contact name'), max_length=255,
                         blank=True)
    employees = models.ManyToManyField(settings.AUTH_USER_MODEL,
                         blank=True,
                         null=True,
                         verbose_name=_('employees'), 
                         through='CompanyAccess')

    class Meta:
        verbose_name = _("company")
        verbose_name_plural = _("companies")
        permissions = (
            ("browse_companies", "Can browse companies"),
            ("view_company", "Can view company"),
            ("manage_company_access", "Can manage company access"),
        )

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('company_edit', [str(self.id)])

        
class CompanyAccess(models.Model):
    company = models.ForeignKey(Company)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    # if a user is invited then we need to know his email address and group he's
    # been invited to
    invitation = models.BooleanField(_('invitation', default=False))
    email = models.EmailField(_('e-mail'), blank=True, null=True)
    group = models.ForeignKey(Group)

    def __unicode__(self):
        return u'%s | %s | %s' % (
            unicode(self.company),
            unicode(getattr(self, 'user', '---')),
            unicode(getattr(self, 'email', '---')))
    
    @property
    def get_email(self):
        if self.user is not None:
            return self.user.email
        return self.email


@receiver(pre_save, sender=CompanyAccess)
def _revoke_access_for_company_user(sender, instance, *args, **kwargs):
    """
    Assign user to a group in the context of company.
    Assign minimal permissions grouped in Company Employee group to a user.
    """
    if instance and instance.user:
        ca = CompanyAccess.objects.get(id=instance.pk)
        UserObjectGroup.objects.remove_access(group=ca.group,
                                          user=instance.user, 
                                          obj=instance.company)
                                          
@receiver(post_save, sender=CompanyAccess)
def _set_access_for_company_user(sender, instance, *args, **kwargs):
    """
    Assign user to a group in the context of company.
    Assign minimal permissions grouped in Company Employee group to a user.
    """
    if instance and instance.user:
        #print instance.group
        #import pdb;pdb.set_trace()
        company_employee_group = Group.objects.get(name='Company Employee')
        instance.user.groups.add(company_employee_group)
        UserObjectGroup.objects.assign(group=instance.group, 
                                       user=instance.user, 
                                       obj=instance.company)

@receiver(pre_delete, sender=CompanyAccess)
def _clear_groups_for_company_user(sender, instance, *args, **kwargs):
    """
    If user is no longer in any company then remove him from Company Employee 
    group.
    """
    if instance and instance.user:
        if not CompanyAccess.objects.filter(user=instance.user):
            company_employee_group = Group.objects.get(name='Company Employee')
            instance.user.groups.remove(company_employee_group)
        UserObjectGroup.objects.remove_access(instance.group, instance.user, 
                                          instance.company)

#@receiver(post_save, sender=Company)
#def _create_groups_for_company(sender, instance, *args, **kwargs):
#    from guardian.shortcuts import assign
#    dealer = Group.objects.get_or_create(name='%s: Dealer' % instance.name)[0] 
#    technician = Group.objects.get_or_create(\
#            name='%s: Technician' % instance.name)[0] 
#
#    # Dealer assignments
#    assign('companies.browse_companies', dealer)
#    assign('bluusites.browse_bluusites', dealer)
#    assign('view_company', dealer, instance)
#    assign('change_company', dealer, instance)
#    assign('manage_company_access', dealer, instance)
#
#    #Technician assignments
#    assign('companies.browse_companies', technician)
#    assign('bluusites.browse_bluusites', technician)
#    assign('view_company', technician, instance)


pre_delete.connect(remove_orphaned_obj_perms, sender=Company)

