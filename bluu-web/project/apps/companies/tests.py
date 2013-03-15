import base64
import json
from django.core import mail
from django_webtest import WebTest
from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from grontextual.models import UserObjectGroup
from invitations.models import InvitationKey
from accounts.models import BluuUser
from .models import Company, CompanyAccess

class CompaniesTestCase(WebTest):

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        run_initialize_script()

        self.company1 = G(Company, name="C1")
        self.company2 = G(Company, name="C2")

        self.user1 = G(BluuUser, username='test1')
        self.user2 = G(BluuUser, username='test2',
                       groups=[Group.objects.get(name='Bluu')])
        self.user3 = G(BluuUser, username='test3')

        assign_perm('companies.browse_companies', self.user3)
        assign_perm('companies.view_company', self.user3, self.company1)


    def testCompanyCodeGenerated(self):
        """
        Test unique company code generation
        """
        company, created = Company.objects.get_or_create(name="nazwa")
        self.assertEqual(company.code, u'NA0001')

    def testCompanyListDenyAccess(self):
        """
        User with no `companies.browse_companies` permission can't access
        a company list.
        """
        self.app.get(reverse('company_list'), user='test1', status=302)

    def testCompanyListApproveAccess(self):
        """
        User with companies.browse_companies permission can access 
        a company list.
        """
        self.app.get(reverse('company_list'), user='test2', status=200)

    def testCompanyListGlobalPermissionAllowsUserToSeeAllCompanies(self):
        """
        User with a global permission companies.view_company
        can see all companies.
        """
        res = self.app.get(reverse('company_list'), user='test2')
        assert "C1" in res
        assert "C2" in res

    def testCompanyListObjectPermissionAllowsUserToSeeOnlyAssignedCompany(self):
        """
        User with a per object permission companies.view_company
        can see only assigned companies.
        """
        res = self.app.get(reverse('company_list'), user='test3')
        assert "C1" in res
        assert "C2" not in res

    def testCompanyUpdateOnlyAssignedCompany(self):
        """
        User can update only companies that are assigned to him."""
        self.app.get(reverse('company_edit', args=[self.company1.pk]),
                user='test2', status=200)
        res = self.app.get(reverse('company_edit', args=[self.company1.pk]),
                user='test1', status=302).follow()
        assert "Sign in" in res

    def testCompanyDeleteOnlyAssignedCompany(self):
        """
        User can delete only companies that are assigned to him."""
        res = self.app.get(reverse('company_delete', args=[self.company1.pk]),
                user='test2').follow()
        assert "Company deleted" in res

    def testCompanyDontDeleteUnassignedCompany(self):
        """
        User can't delete companies that aren't assigned to him."""
        res = self.app.get(reverse('company_delete', kwargs={'pk': self.company1.pk}),
                user='test1', status=302).follow()
        assert "Sign in" in res

    def testAccessCreateCompany(self):
        """
        User assigned companies.add_company can create new companies.
        User test1 isn't assigned companies.add_company.
        User test2 is assigned companies.add_company.
        """
        self.app.get(reverse('company_add'), user='test1', status=302)
        res = self.app.get(reverse('company_add'), user='test2', status=200)
        form = res.form
        form['name'] = 'Company1'
        form['street'] = 'street'
        form['city'] = 'city'
        form['state'] = 'alaska'
        form['zip_code'] = '345 23'
        form['country'] = 'US'
        form['phone'] = '+34 32 4 3'
        form['email'] = 'test@example.com'
        form['contact_name'] = 'Ian Shimmy'
        form_res = form.submit().follow()

        assert "Company added" in form_res
        

class CompaniesAccessTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        run_initialize_script()

        self.company1 = G(Company, name="C1")
        self.company2 = G(Company, name="C2")

        self.bluu = G(BluuUser, username='bluu',
                       groups=[Group.objects.get(name='Bluu')])

        self.user = G(BluuUser, username='user', email='user@example.com',
                       groups=[Group.objects.get(name='Dealer')])

        self.dealer_group = Group.objects.get(name='Dealer')
        self.technician_group = Group.objects.get(name='Technician')

    def testInviteToCompany(self):
        """
        After an invitation is sent there should be:
            - CompanyAccess object connecting Company, Group and e-mail address
            - InvitationKey object that will allow a user to register
            - sent invitation in an outbox
        """
        form_data = {'email':'a@example.com', 'group':self.dealer_group.pk}
        resp = self.app.post(
                reverse('companies:api_company_access', 
                        kwargs={'company_pk':self.company1.pk}),
                json.dumps(form_data),
                content_type='application/json;charset=utf-8',
                user='bluu',
                status=201)

        # company access exists
        ca = CompanyAccess.objects.filter(
                            email='a@example.com',
                            group=self.dealer_group,
                            company=self.company1)
        self.assertTrue(ca.exists())

        # invitation exists
        ctype = ContentType.objects.get_for_model(ca[0])
        key = InvitationKey.objects.filter(
                                from_user=self.bluu,
                                content_type=ctype,
                                object_id=ca[0].pk
                            )[0]
        self.assertTrue(key)

        # Invitation sent
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject,
                         'Invitation from bluu to join example.com')
        assert key.key in mail.outbox[0].body

    def testInviteToCompanyEmailCaseInsensitive(self):
        """
        After an invitation is sent there should be a case insensitive check
        of the user's email
        """
        form_data = {'email':'User@example.com', 'group':self.dealer_group.pk}
        resp = self.app.post(
                reverse('companies:api_company_access', 
                        kwargs={'company_pk':self.company1.pk}),
                json.dumps(form_data),
                content_type='application/json;charset=utf-8',
                user='bluu',
                status=201)

        # new company access shouldn't be created
        ca = CompanyAccess.objects.filter(
                            email='User@example.com',
                            group=self.dealer_group,
                            company=self.company1)
        self.assertFalse(ca.exists())

        # Invitation shouldn't be sent
        self.assertEqual(len(mail.outbox), 0)


class CompaniesAccessRegisterTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        run_initialize_script()

        self.company1 = G(Company, name="C1")
        self.company2 = G(Company, name="C2")

        self.bluu = G(BluuUser, username='bluu',
                      groups=[Group.objects.get(name='Bluu')])

        self.dealer_group = Group.objects.get(name='Dealer')
        self.technician_group = Group.objects.get(name='Technician')

        self.company1_access = G(CompanyAccess,
                                 company=self.company1,
                                 email='a@example.com',
                                 group=self.dealer_group,
                                 user=None)

        self.ca_ctype = ContentType.objects.get_for_model(CompanyAccess)
        self.key = InvitationKey.objects.create_invitation(
                        user=self.bluu,
                        content_object=self.company1_access)

    def testAccessRegisterToCompany(self):
        """
        Only Invited user access can register page
        """

        resp = self.app.get(
                reverse('invited_register', 
                        kwargs={'invitation_key': self.key.key}),
                status=200)
        assert not 'Invalid invitation key!' in resp.body

        resp = self.app.get(
                reverse('invited_register', 
                        kwargs={'invitation_key': 'wrong_key'}),
                status=200)
        assert 'Invalid invitation key!' in resp.body


    def testRegisterToCompany(self):
        """
        Only Invited user access can register page
        """

        resp = self.app.get(
                reverse('invited_register', 
                        kwargs={'invitation_key': self.key.key}),
                status=200)

        form = resp.form
        form['username'] = 'a'
        form['first_name'] = 'abcd'
        form['last_name'] = 'efgh'
        form['password1'] = 'test'
        form['password2'] = 'test'
        fresp = form.submit().follow()

        self.assertContains(fresp, "You&#39;ve been registered and logged in.")

        # invitation marked as used
        key = InvitationKey.objects.get_key(self.key.key)
        self.assertFalse(key.is_usable())

        # user assigned to company access
        ca = CompanyAccess.objects.get(
                                  company=self.company1,
                                  email='a@example.com',
                                  group=self.dealer_group
                )
        self.assertIsNotNone(ca.user)

        # user granted group rights in context of a company (UOG)
        user = get_user_model().objects.get(username='a')
        groups = UserObjectGroup.objects.get_for_object(user, self.company1).\
                    values_list('group', flat=True)
        assert self.dealer_group.pk in groups

    # test multiple invited has multiple accessess


class CompaniesAccessChangesTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        run_initialize_script()

        self.company1 = G(Company, name="C1")
        self.company2 = G(Company, name="C2")

        self.bluu = G(BluuUser, username='bluu',
                      groups=[Group.objects.get(name='Bluu')])

        self.dealer = G(BluuUser, username='dealer', email='dealer@example.com',
                      groups=[Group.objects.get(name='Company Employee')])



        self.dealer_group = Group.objects.get(name='Dealer')
        self.technician_group = Group.objects.get(name='Technician')

        self.company1_access = G(CompanyAccess,
                                 company=self.company1,
                                 group=self.dealer_group,
                                 user=self.dealer)

        self.ca_ctype = ContentType.objects.get_for_model(CompanyAccess)

    def testAccessChangedByOther(self):
        """
        Checks whether access change works
        """
        assigned_groups = []
        for uog in UserObjectGroup.objects.get_for_object(self.dealer, self.company1):
            assigned_groups.append(uog.group.name)
        self.assertTrue('Dealer' in assigned_groups)
        self.assertFalse('Technician' in assigned_groups)

        form_data = {'id':self.company1_access.pk,
                     'group':self.technician_group.pk}
        resp = self.app.put(
                reverse('companies:api_company_access_json', 
                        kwargs={'company_pk':self.company1.pk,
                                'pk':self.company1_access.pk}),
                json.dumps(form_data),
                content_type='application/json;charset=utf-8',
                user='bluu',
                status=200)
        assigned_groups = []
        for uog in UserObjectGroup.objects.get_for_object(self.dealer, self.company1):
            assigned_groups.append(uog.group.name)
        self.assertTrue('Technician' in assigned_groups)
        self.assertFalse('Dealer' in assigned_groups)


    def testAccessRemoval(self):
        """
        Checks whether access removal works
        """
        assigned_groups = []
        for uog in UserObjectGroup.objects.get_for_object(self.dealer, self.company1):
            assigned_groups.append(uog.group.name)
        self.assertTrue('Dealer' in assigned_groups)
        self.assertFalse('Technician' in assigned_groups)

        form_data = {'id':self.company1_access.pk,
                     'group':self.technician_group.pk}
        resp = self.app.delete(
                reverse('companies:api_company_access_json', 
                        kwargs={'company_pk':self.company1.pk,
                                'pk':self.company1_access.pk}),
                content_type='application/json;charset=utf-8',
                user='bluu',
                status=204)
        assigned_groups = []
        for uog in UserObjectGroup.objects.get_for_object(self.dealer, self.company1):
            assigned_groups.append(uog.group.name)
        self.assertFalse(assigned_groups)


