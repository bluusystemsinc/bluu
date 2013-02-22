from django_webtest import WebTest
from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from guardian.shortcuts import assign
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from companies.models import Company
from .models import UserObjectGroup


class GrontextualTestCase(WebTest):

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        run_initialize_script()

        self.company1 = G(Company, name="C1")
        self.company2 = G(Company, name="C2")

        self.user1 = G(get_user_model(), username='test1')
        self.user2 = G(get_user_model(),
                       username='test2',
                       groups=[Group.objects.get(name='Bluu')])
        self.user3 = G(get_user_model(), username='test3')
        
        UserObjectGroup.objects.assign(Group.objects.get(name='Bluu'), self.user3, self.company1)

        company_type = ContentType.objects.get(app_label="companies",
                                               model="company")
        perm = Permission.objects.get(content_type=company_type, codename='browse_companies')
        perm2 = Permission.objects.get(content_type=company_type, codename='view_company')
        self.user3.user_permissions.add(perm, perm2)

    def testUserObjectGroupAssingment(self):
        """
        """
        self.assertTrue(self.user3.has_perm('companies.manage_company_access', self.company1))

    def testUserObjectGroupInViewDecorator(self):
        # change_company permission is checked by company_edit view
        # user assinged to Bluu group passes the test
        self.app.get(reverse('company_edit', args=[self.company1.pk]),
                user='test3', status=200)

        # user not assinged to Bluu group doesn't pass the test
        res = self.app.get(reverse('company_edit', args=[self.company1.pk]),
                user='test1', status=302)
        target = res.follow()
        self.assertEqual(target.status, '200 OK')

    def testUserObjectGroupTemplateTag(self):
        # change_company permission is checked by company_edit view
        # user assinged to Bluu group passes the test
        res = self.app.get(reverse('company_list'), user='test3', status=200)
        self.assertContains(res, '<a href="/companies/2/edit/">Edit</a>')


