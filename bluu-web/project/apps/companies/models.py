from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.contrib.contenttypes import generic
from django.contrib.auth.models import Group
from django.conf import settings

import logging
logger = logging.getLogger('bluu')

from registration import signals
from utils.misc import remove_orphaned_obj_perms
from utils.models import Entity

from accounts.models import BluuUser
from invitations.models import InvitationKey

class Company(Entity):
    code = models.CharField(_('code'), max_length=6, unique=True)
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

    def save(self, *args, **kwargs):
        if self.code == "":
            code = self.generate_code()
            while Company.objects.filter(code=code).exists():
                code = self.generate_code()
            self.code = code
        super(Company, self).save(*args, **kwargs)

    def _get_code(self, name, number):
        return '%s%04d' % (name[:2].upper(), number)

    def generate_code(self):
        """
        Generates unique company code in a form AA1234
        """
        # reverse order by autoincrement field
        # latest object has highest id
        existing_codes = Company.objects.all().\
                filter(code__isnull=False).order_by('-id')

        if existing_codes.count() > 0:
            last_code = existing_codes[0].code[2:]
            if last_code == '' or last_code is None:
                last_code = 0
            new_code = int(last_code) + 1
        else:
            new_code = 1

        code = self._get_code(self.name, new_code)
        while Company.objects.filter(code=code).exists():
            new_code = new_code + 1
            code = self._get_code(self.name, new_code)
        return code

    def assign_user(self, assignee, email, group):
        # add or invite
        try:
            user = BluuUser.objects.get(email__iexact=email)
            email = user.email
        except BluuUser.DoesNotExist:
            user = None

        try:
            CompanyAccess.objects.get(
                (Q(user=user) & Q(user__isnull=False)) | Q(email__iexact=email),
                company=self)
        except CompanyAccess.DoesNotExist:
            # User doesn't have access
            ca = CompanyAccess.objects.create(user=user, email=email,
                                              group=group, company=self)
            if user is None:
                self.invite_user(assignee, obj=ca)
            return True

        return False

    def invite_user(self, inviter, obj):
        invitation = InvitationKey.objects.create_invitation(
                user=inviter,
                content_object=obj
                )
        invitation.send_to(obj.email)


class CompanyAccess(models.Model):
    company = models.ForeignKey(Company)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    # if a user is invited then we need to know his email address and group he's
    # been invited to
    #invitation = models.BooleanField(_('invitation', default=False))
    email = models.EmailField(_('e-mail'), blank=True, null=True)
    group = models.ForeignKey(Group)
    invitations = generic.GenericRelation('invitations.InvitationKey')

    def __unicode__(self):
        return u'%s | %s | %s' % (
            unicode(self.company),
            unicode(getattr(self, 'user', '---')),
            unicode(getattr(self, 'email', '---')))
    
    class Meta:
        verbose_name = _("company access")
        verbose_name_plural = _("company accesses")
        unique_together = (("company", "user"), ("company", "email"))
        permissions = (
            ("browse_companyaccesses", "Can browse company accesses"),
            ("view_companyaccess", "Can view company access"),
        )

    @property
    def get_email(self):
        if self.user is not None:
            return self.user.email
        return self.email


@receiver(pre_save, sender=CompanyAccess)
def _remove_access_for_company_user(sender, instance, *args, **kwargs):
    """
    Before access level is changed remove current accesses from authentication
    backend - UserObjectGroup.
    Access is removed in context of company and its sites.
    """
    if instance.pk and instance.user:
        ca = CompanyAccess.objects.get(pk=instance.pk)
        instance.user.remove_all_accesses(obj=instance.company)
        for site in instance.company.bluusite_set.all():
            instance.user.remove_access(group=ca.group, obj=site)


@receiver(post_save, sender=CompanyAccess)
def _assign_access_for_company_user(sender, instance, *args, **kwargs):
    """
    Assign permissions grouped in DEFAULT_COMPANY_GROUPS group to a user.
    Assign user to a group in the context of company.
    Assign user to a group in the context of sites belonging to company.
    """
    if instance.pk and instance.user:

        # assign a user to a company
        instance.user.assign_group(group=instance.group, obj=instance.company)

        # assign a user to a company's sites
        for site in instance.company.bluusite_set.all():
            instance.user.assign_group(group=instance.group, obj=site)

        # assign default company groups
        for group_name in settings.DEFAULT_COMPANY_GROUPS:
            try:
                default_group = Group.objects.get(name=group_name)
                instance.user.groups.add(default_group)
            except Group.DoesNotExist:
                logger.warning('Cannot assign a user to non existing group {0}"\
                        "defined in settings.DEFAULT_COMPANY_GROUPS'\
                        .format(group_name))


@receiver(pre_delete, sender=CompanyAccess)
def _clear_groups_for_company_user(sender, instance, *args, **kwargs):
    """
    If user is no longer in any company then remove him from default company 
    groups.
    """
    if instance and instance.user:
        if not CompanyAccess.objects.filter(user=instance.user).exists():
            for group_name in settings.DEFAULT_COMPANY_GROUPS:
                default_group = Group.objects.get(name=group_name)
                instance.user.groups.remove(default_group)
        instance.user.remove_all_accesses(instance.company)
        for site in instance.company.bluusite_set.all():
            instance.user.remove_access(group=instance.group, obj=site)


@receiver(signals.user_registered)
def _assign_access_for_newly_registered_user(sender, user, request, *args, **kwargs):
    """
    Sets user object on on access objects with user email (invitations)
    """
    for access in CompanyAccess.objects.filter(email=user.email):
        access.user = user
        access.save()


pre_delete.connect(remove_orphaned_obj_perms, sender=Company)

