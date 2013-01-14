from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django_webtest import WebTest
from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from guardian.shortcuts import assign
from django.contrib.auth.models import Group

from accounts.models import BluuUser, Company

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
        assign('accounts.browse_companies', self.user3)
        assign('accounts.view_company', self.user3, self.company1)


    def testCompanyListDenyAccess(self):
        """User with no accounts.browse_companies permission can't access
        a company list.
        """
        self.app.get(reverse('company-list'), user='test1', status=302)

    def testCompanyListApproveAccess(self):
        """User with accounts.browse_companies permission can access 
        a company list.
        """
        self.app.get(reverse('company-list'), user='test2', status=200)

    def testCompanyListGlobalPermissionAllowsUserToSeeAllCompanies(self):
        """User with a global permission accounts.view_company
        can see all companies.
        """
        res = self.app.get(reverse('company-list'), user='test2')
        assert "C1" in res
        assert "C2" in res

    def testCompanyListObjectPermissionAllowsUserToSeeOnlyAssignedCompany(self):
        """User with a per object permission accounts.view_company
        can see only assigned companies.
        """
        res = self.app.get(reverse('company-list'), user='test3')
        assert "C1" in res
        assert "C2" not in res

    def testCompanyUpdateOnlyAssignedCompany(self):
        """User can update only companies that are assigned to him."""
        self.app.get(reverse('company-edit', args=[self.company1.pk]),
                user='test2', status=200)
        self.app.get(reverse('company-edit', args=[self.company1.pk]),
                user='test1', status=403)

    def testCompanyDeleteOnlyAssignedCompany(self):
        """User can delete only companies that are assigned to him."""
        res = self.app.get(reverse('company-delete', args=[self.company1.pk]),
                user='test2').follow()
        assert "Company deleted" in res

    def testCompanyDontDeleteUnassignedCompany(self):
        """User can't delete companies that aren't assigned to him."""
        res = self.app.get(reverse('company-delete', args=[self.company1.pk]),
                user='test1', status=403)

    def testAccessCreateCompany(self):
        """User assigned accounts.add_company can create new companies.
        User test1 isn't assigned accounts.add_company.
        User test2 is assigned accounts.add_company.
        """
        self.app.get(reverse('company-add'), user='test1', status=302)
        res = self.app.get(reverse('company-add'), user='test2', status=200)
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
        self.assertTrue(Group.objects.filter(name='Company1: Dealer').exists())
        self.assertTrue(Group.objects.filter(name='Company1: Technician').exists())
        


