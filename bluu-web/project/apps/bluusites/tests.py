from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django_webtest import WebTest
from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Group

from accounts.models import BluuUser
from companies.models import Company
from bluusites.models import BluuSite, BluuSiteAccess
from grontextual.models import UserObjectGroup


class SitesTestCase(WebTest):

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        run_initialize_script()

        self.company1 = G(Company, name="C1")
        self.company2 = G(Company, name="C2")

        self.user1 = G(BluuUser, username='test1')
        
        self.user2 = G(BluuUser, username='test2',
                       groups=[Group.objects.get(name='Bluu')])

        self.user3 = G(BluuUser, username='test3')
        assign_perm('accounts.browse_companies', self.user3)
        assign_perm('accounts.view_company', self.user3, self.company1)


class SitesAccessChangesTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        run_initialize_script()

        self.dealer_group = Group.objects.get(name='Dealer')
        self.technician_group = Group.objects.get(name='Technician')

        self.company1 = G(Company, name="C1")
        
        #self.site1 = G(BluuSite, slug="site1", company=self.company1)
        #self.site2 = G(BluuSite, slug="site2", company=self.company1)

        self.bluu = G(BluuUser, username='bluu',
                      groups=[Group.objects.get(name='Bluu')])

        self.dealer = G(BluuUser, username='dealer', email='dealer@example.com')
                      #groups=[Group.objects.get(name='Company Employee')])

       #self.company1_access = G(CompanyAccess,
       #                          company=self.company1,
       #                          group=self.dealer_group,
       #                          user=self.dealer)

       # self.ca_ctype = ContentType.objects.get_for_model(CompanyAccess)

    def testAccessToCompanySiteGranted(self):
        """
        Tests if company user is automatically assigned to a site added to company
        """
        self.company1.assign_user(self.bluu, 'dealer@example.com', 
                                  self.dealer_group)

        self.site1 = BluuSite.objects.create(slug="site1", company=self.company1)
        
        dealer = BluuUser.objects.get(username='dealer')
        self.assertTrue(dealer.has_perm('bluusites.change_bluusite', self.site1))
        try:
            ac = BluuSiteAccess.objects.get(user=self.dealer1,
                                                     group=self.dealer_group)
        except BluuSiteAccess.DoesNotExist:
            ac = None
        # for company users assigned to sites there is no BluuSiteAccess record
        self.assertTrue(ac is None)

    def testAccessToCompanySiteGrantedForNewUser(self):
        """
        Tests if company user is automatically assigned to a site when added
        to company after site exists
        """
        self.site1 = BluuSite.objects.create(slug="site1", company=self.company1)
        
        self.company1.assign_user(self.bluu, 'dealer@example.com', 
                                  self.dealer_group)

        dealer = BluuUser.objects.get(username='dealer')
        self.assertTrue(dealer.has_perm('bluusites.change_bluusite', self.site1))

    def testAccessToCompanySiteGrantedForNewUser(self):
        """
        Tests if company user is automatically assigned to a site when added
        to company after site exists
        """
        self.site1 = BluuSite.objects.create(slug="site1", company=self.company1)
        
        self.company1.assign_user(self.bluu, 'dealer@example.com', 
                                  self.dealer_group)

        dealer = BluuUser.objects.get(username='dealer')
        self.assertTrue(dealer.has_perm('bluusites.change_bluusite', self.site1))



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


