import json
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django_webtest import WebTest
from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Group

from accounts.models import BluuUser
from companies.models import Company, CompanyAccess
from bluusites.models import BluuSite, BluuSiteAccess, Room
from devices.models import Device, DeviceType, Status
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


class SitesAccessTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        run_initialize_script()

        self.dealer_group = Group.objects.get(name='Dealer')
        self.technician_group = Group.objects.get(name='Technician')
        self.masteruser_group = Group.objects.get(name='Master User')
        self.user_group = Group.objects.get(name='User')

        self.company1 = G(Company, name="C1")
        self.site1 = G(BluuSite, slug="site1", company=self.company1)

        #self.site2 = G(BluuSite, slug="site2", company=self.company1)

        self.bluu = G(BluuUser, username='bluu',
                      groups=[Group.objects.get(name='Bluu')])

        self.dealer = G(BluuUser, username='dealer', email='dealer@example.com')
                      #groups=[Group.objects.get(name='Company Employee')])

        self.masteruser = G(BluuUser, username='masteruser',
                            email='masteruser@example.com')


       #self.company1_access = G(CompanyAccess,
       #                          company=self.company1,
       #                          group=self.dealer_group,
       #                          user=self.dealer)

       # self.ca_ctype = ContentType.objects.get_for_model(CompanyAccess)

    def testAccessToCompanySiteGrantedAfterSiteAdded(self):
        """
        Tests if company user is automatically assigned to a site after
        the site is added
        """
        self.company1.assign_user(self.bluu, 'dealer@example.com', 
                                  self.dealer_group)

        self.site1 = BluuSite.objects.create(slug="site1",
                                             company=self.company1)
        
        dealer = BluuUser.objects.get(username='dealer')
        self.assertTrue(dealer.has_perm('bluusites.change_bluusite',
                                        self.site1))

        # for company users assigned to sites there is no BluuSiteAccess record
        try:
            ac = BluuSiteAccess.objects.get(user=self.dealer,
                                                     group=self.dealer_group)
        except BluuSiteAccess.DoesNotExist:
            ac = None
        self.assertTrue(ac is None)

    def testAccessToCompanySiteGrantedAfterNewCompanyUserAdded(self):
        """
        Tests if company user is automatically assigned to a site when the user
        is added to a company after a site had been added
        """
        self.site1 = BluuSite.objects.create(slug="site1",
                                             company=self.company1)
        
        self.company1.assign_user(self.bluu, 'dealer@example.com', 
                                  self.dealer_group)

        dealer = BluuUser.objects.get(username='dealer')
        self.assertTrue(dealer.has_perm('bluusites.change_bluusite',
                                        self.site1))

        # for company users assigned to sites there is no BluuSiteAccess record
        try:
            ac = BluuSiteAccess.objects.get(user=self.dealer,
                                            site=self.site1,
                                            group=self.dealer_group)
        except BluuSiteAccess.DoesNotExist:
            ac = None
        self.assertTrue(ac is None)

    def testAccessToCompanySiteChangedOnCompanyAccessChange(self):
        """
        Checks whether access change in company changes access in site 
        """
        # Assign delaer user to company
        self.company1.assign_user(self.bluu, 'dealer@example.com', 
                                  self.dealer_group)
        # Add site to company
        self.site1 = BluuSite.objects.create(slug="site1",
                                             company=self.company1)

        # Check if dealer user has correct perms to access site and company
        dealer = BluuUser.objects.get(username='dealer')
        self.assertTrue(dealer.has_perm('bluusites.change_bluusite',
                                        self.site1))
        self.assertTrue(dealer.has_perm('companies.change_company',
                                        self.company1))

        # Check if dealer user has correct assignments for site
        assigned_groups = []
        for uog in UserObjectGroup.objects.get_for_object(self.dealer,
                                                          self.site1):
            assigned_groups.append(uog.group.name)
        self.assertTrue('Dealer' in assigned_groups)

        # Change dealer assignment on company level to Technician
        ac = CompanyAccess.objects.get(user=self.dealer,
                                       company=self.company1,
                                       group=self.dealer_group)
        form_data = {'id':ac.pk,
                     'group':self.technician_group.pk}
        resp = self.app.put(
                reverse('api_company_access_json', 
                        kwargs={'company_pk':self.company1.pk,
                                'pk':ac.pk}),
                json.dumps(form_data),
                content_type='application/json;charset=utf-8',
                user='bluu',
                status=200)

        # Check if dealer user is a Technician (and not dealer)
        # in context of site
        dealer = BluuUser.objects.get(username='dealer')
        assigned_groups = []
        for uog in UserObjectGroup.objects.get_for_object(self.dealer,
                                                          self.site1):
            assigned_groups.append(uog.group.name)
        self.assertTrue('Technician' in assigned_groups)
        self.assertFalse('Dealer' in assigned_groups)

        self.assertTrue(dealer.has_perm('bluusites.change_bluusite',
                                        self.site1))
        self.assertFalse(dealer.has_perm('companies.change_company',
                                        self.company1))

    def testAccessRemovalForCompanyRemovesSiteAccess(self):
        """
        Checks whether site access is removed after company access was removed 
        """
        # Assign delaer user to company
        self.company1.assign_user(self.bluu, 'dealer@example.com', 
                                  self.dealer_group)
        # Add site to company
        self.site1 = BluuSite.objects.create(slug="site1",
                                             company=self.company1)

        # Check if dealer user has correct perms to access site and company
        dealer = BluuUser.objects.get(username='dealer')
        self.assertTrue(dealer.has_perm('bluusites.change_bluusite',
                                        self.site1))
        self.assertTrue(dealer.has_perm('companies.change_company',
                                        self.company1))

        # Check if dealer user has correct assignments for site
        assigned_groups = []
        for uog in UserObjectGroup.objects.get_for_object(self.dealer,
                                                          self.site1):
            assigned_groups.append(uog.group.name)
        self.assertTrue('Dealer' in assigned_groups)

        # Remove dealer assignment on company level
        ac = CompanyAccess.objects.get(user=self.dealer,
                                       company=self.company1,
                                       group=self.dealer_group)

        resp = self.app.delete(
                reverse('api_company_access_json', 
                        kwargs={'company_pk':self.company1.pk,
                                'pk':ac.pk}),
                user='bluu',
                status=204)

        # Check if dealer user is a Technician (and not dealer)
        # in context of site
        dealer = BluuUser.objects.get(username='dealer')
        assigned_groups = []
        for uog in UserObjectGroup.objects.get_for_object(self.dealer,
                                                          self.site1):
            assigned_groups.append(uog.group.name)
        self.assertFalse('Dealer' in assigned_groups)

        self.assertFalse(dealer.has_perm('bluusites.change_bluusite',
                                        self.site1))
        self.assertFalse(dealer.has_perm('companies.change_company',
                                        self.company1))


    def testAccessToSiteGranted(self):
        """
        Tests if a user is correctly assigned to a site
        """

        form_data = {'email':self.masteruser.email,
                     'group':self.masteruser_group.pk}
        resp = self.app.post(
                reverse('api_site_access', 
                        kwargs={'pk':self.site1.pk}),
                json.dumps(form_data),
                content_type='application/json;charset=utf-8',
                user='bluu',
                status=201)

        assigned_groups = []
        for uog in UserObjectGroup.objects.get_for_object(self.masteruser, 
                                                          self.site1):
            assigned_groups.append(uog.group.name)
        self.assertTrue('Master User' in assigned_groups)
        self.assertTrue(self.masteruser.has_perm('bluusites.change_bluusite',
                                                 self.site1))

        try:
            ac = BluuSiteAccess.objects.get(user=self.masteruser,
                                            site=self.site1,
                                            group=self.masteruser_group)
        except BluuSiteAccess.DoesNotExist:
            ac = None
        self.assertTrue(ac is not None)


    def testAccessToSiteChanged(self):
        """
        Checks whether access change works
        """
        self.site1.add_user(self.masteruser, self.masteruser_group)
        assigned_groups = []
        for uog in UserObjectGroup.objects.get_for_object(self.masteruser,
                                                          self.site1):
            assigned_groups.append(uog.group.name)
        self.assertFalse('User' in assigned_groups)
        self.assertTrue('Master User' in assigned_groups)

        ac = BluuSiteAccess.objects.get(user=self.masteruser,
                                        site=self.site1,
                                        group=self.masteruser_group)

        form_data = {'id':ac.pk,
                     'group':self.user_group.pk}
        resp = self.app.put(
                reverse('api_site_access_json', 
                        kwargs={'site_pk':self.site1.pk,
                                'pk':ac.pk}),
                json.dumps(form_data),
                content_type='application/json;charset=utf-8',
                user='bluu',
                status=200)

        assigned_groups = []
        for uog in UserObjectGroup.objects.get_for_object(self.masteruser,
                                                          self.site1):
            assigned_groups.append(uog.group.name)
        self.assertTrue('User' in assigned_groups)
        self.assertFalse('Master User' in assigned_groups)


    def testAccessRemoval(self):
        """
        Checks whether access removal works
        """
        self.site1.add_user(self.masteruser, self.masteruser_group)
        assigned_groups = []
        for uog in UserObjectGroup.objects.get_for_object(self.masteruser,
                                                          self.site1):
            assigned_groups.append(uog.group.name)
        self.assertTrue('Master User' in assigned_groups)

        ac = BluuSiteAccess.objects.get(user=self.masteruser,
                                        site=self.site1,
                                        group=self.masteruser_group)
        resp = self.app.delete(
                reverse('api_site_access_json', 
                        kwargs={'site_pk':self.site1.pk,
                                'pk':ac.pk}),
                user='bluu',
                status=204)
        assigned_groups = []
        for uog in UserObjectGroup.objects.get_for_object(self.masteruser,
                                                          self.company1):
            assigned_groups.append(uog.group.name)
        self.assertFalse(assigned_groups)


class MotionTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script
        run_initialize_script()
        run_initialize_dicts_script()

        self.dealer_group = Group.objects.get(name='Dealer')
        self.technician_group = Group.objects.get(name='Technician')
        self.masteruser_group = Group.objects.get(name='Master User')
        self.user_group = Group.objects.get(name='User')

        motion = DeviceType.objects.get(name=DeviceType.MOTION)

        self.company1 = G(Company, name="C1")
        self.site1 = G(BluuSite, slug="site1", company=self.company1,
                       many_inhabitants=False)
        self.room1 = G(Room, name='Room 1', bluusite=self.site1)
        self.room2 = G(Room, name='Room 2', bluusite=self.site1)
        self.device1 = G(Device, bluusite=self.site1, company=self.company1,
                         device_type=motion, room=self.room1)
        self.device2 = G(Device, bluusite=self.site1, company=self.company1,
                         device_type=motion, room=self.room2)


        self.site2 = G(BluuSite, slug="site2", company=self.company1,
                       many_inhabitants=True)
        self.s2room1 = G(Room, name='S2 Room 1', bluusite=self.site2)
        self.s2room2 = G(Room, name='S2 Room 2', bluusite=self.site2)
        self.s2device1 = G(Device, bluusite=self.site2, company=self.company1,
                           device_type=motion, room=self.s2room1)
        self.s2device2 = G(Device, bluusite=self.site2, company=self.company1,
                           device_type=motion, room=self.s2room2)

        self.bluu = G(BluuUser, username='bluu',
                      groups=[Group.objects.get(name='Bluu')])

        self.dealer = G(BluuUser, username='dealer', email='dealer@example.com')

        self.masteruser = G(BluuUser, username='masteruser',
                            email='masteruser@example.com')


    def testMotionSingleInhabitant(self):
        """
        Tests if a motion algorithm works as expected
        """
        day = timedelta(days=1)
        three_minutes = timedelta(minutes=3)
        ten_minutes = timedelta(minutes=10)
        today = datetime.today()
        yesterday = today - day

        G(Status, device=self.device1, action=True, timestamp=yesterday)
        G(Status, device=self.device1, action=True, timestamp=yesterday + three_minutes)
        G(Status, device=self.device1, action=True, timestamp=yesterday + three_minutes +\
                three_minutes)
        G(Status, device=self.device1, action=True, timestamp=yesterday + three_minutes +\
                three_minutes + ten_minutes)
        G(Status, device=self.device1, action=True, timestamp=yesterday + three_minutes +\
                three_minutes + ten_minutes + ten_minutes)
        site = BluuSite.objects.get(pk=self.site1.pk)
        json_data = site.get_activity()
        data = json.loads(json_data)
        # total of 21 minutes should be counted
        nineten_minutes = timedelta(minutes=21)
        result = nineten_minutes.total_seconds()
        self.assertEquals(data[0]['data'], result)

    def testMotionInManyRooms(self):
        """
        Tests if a motion algorithm works as expected, when there is
        many_inhabitants set to False, and data is from sensors in different
        rooms
        """
        day = timedelta(days=1)
        two_minutes = timedelta(minutes=2)
        three_minutes = timedelta(minutes=3)
        five_minutes = timedelta(minutes=5)
        ten_minutes = timedelta(minutes=10)
        today = datetime.today()
        yesterday = today - day

        G(Status, device=self.device1, action=True, timestamp=yesterday)
        G(Status, device=self.device1, action=True, timestamp=yesterday + three_minutes)
        G(Status, device=self.device1, action=True, timestamp=yesterday + three_minutes +\
                three_minutes)
        G(Status, device=self.device1, action=True, timestamp=yesterday + three_minutes +\
                three_minutes + ten_minutes)
        G(Status, device=self.device1, action=True, timestamp=yesterday + three_minutes +\
                three_minutes + ten_minutes + ten_minutes)

        G(Status, device=self.device2, action=True, timestamp=yesterday)
        G(Status, device=self.device2, action=True, timestamp=yesterday + two_minutes)
        G(Status, device=self.device2, action=True, timestamp=yesterday + two_minutes +\
                two_minutes)
        G(Status, device=self.device2, action=True, timestamp=yesterday + two_minutes +\
                two_minutes + five_minutes)
        G(Status, device=self.device2, action=True, timestamp=yesterday + two_minutes +\
                two_minutes + five_minutes + ten_minutes)


        site = BluuSite.objects.get(pk=self.site1.pk)
        json_data = site.get_activity()
        data = json.loads(json_data)
        room1_result = 720.0
        room2_result = 900.0

        for room in ('Room 1', 'Room 2'):
            for obj in data:
                if obj['label'] == 'Room 1':
                    self.assertEquals(obj['data'], room1_result)
                elif obj['label'] == 'Room 2':
                    self.assertEquals(obj['data'], room2_result)

    def testMotionManyInhabitants(self):
        """
        Tests if a motion algorithm works as expected, when there is 
        many_inhabitants set to True
        """
        day = timedelta(days=1)
        three_minutes = timedelta(minutes=3)
        ten_minutes = timedelta(minutes=10)
        today = datetime.today()
        yesterday = today - day

        G(Status, device=self.s2device1, action=True, timestamp=yesterday)
        G(Status, device=self.s2device1, action=True, timestamp=yesterday + three_minutes)
        G(Status, device=self.s2device1, action=True, timestamp=yesterday + three_minutes +\
                three_minutes)
        G(Status, device=self.s2device1, action=True, timestamp=yesterday + three_minutes +\
                three_minutes + ten_minutes)
        G(Status, device=self.s2device1, action=True, timestamp=yesterday + three_minutes +\
                three_minutes + ten_minutes + ten_minutes)

        site = BluuSite.objects.get(pk=self.site2.pk)
        json_data = site.get_activity()
        data = json.loads(json_data)
        # total of 21 minutes should be counted
        nineten_minutes = timedelta(minutes=21)
        result = nineten_minutes.total_seconds()
        room = self.s2device1.room.name
        for obj in data:
            if obj['label'] == room:
                self.assertEquals(obj['data'], result)


    def testMotionManyInhabitantsInManyRooms(self):
        """
        Tests if a motion algorithm works as expected, when there is
        many_inhabitants set to True, and data is from sensors in different
        rooms
        """
        day = timedelta(days=1)
        two_minutes = timedelta(minutes=2)
        three_minutes = timedelta(minutes=3)
        five_minutes = timedelta(minutes=5)
        ten_minutes = timedelta(minutes=10)
        today = datetime.today()
        yesterday = today - day

        G(Status, device=self.s2device1, action=True, timestamp=yesterday)
        G(Status, device=self.s2device1, action=True, timestamp=yesterday + three_minutes)
        G(Status, device=self.s2device1, action=True, timestamp=yesterday + three_minutes +\
                three_minutes)
        G(Status, device=self.s2device1, action=True, timestamp=yesterday + three_minutes +\
                three_minutes + ten_minutes)
        G(Status, device=self.s2device1, action=True, timestamp=yesterday + three_minutes +\
                three_minutes + ten_minutes + ten_minutes)

        G(Status, device=self.s2device2, action=True, timestamp=yesterday)
        G(Status, device=self.s2device2, action=True, timestamp=yesterday + two_minutes)
        G(Status, device=self.s2device2, action=True, timestamp=yesterday + two_minutes +\
                two_minutes)
        G(Status, device=self.s2device2, action=True, timestamp=yesterday + two_minutes +\
                two_minutes + five_minutes)
        G(Status, device=self.s2device2, action=True, timestamp=yesterday + two_minutes +\
                two_minutes + five_minutes + ten_minutes)


        site = BluuSite.objects.get(pk=self.site2.pk)
        json_data = site.get_activity()
        data = json.loads(json_data)

        room1_result = 1260.0
        room2_result = 1140.0

        for room in ('S2 Room 1', 'S2 Room 2'):
            for obj in data:
                if obj['label'] == 'S2 Room 1':
                    self.assertEquals(obj['data'], room1_result)
                elif obj['label'] == 'S2 Room 2':
                    self.assertEquals(obj['data'], room2_result)


class SleepTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script
        run_initialize_script()
        run_initialize_dicts_script()

        self.dealer_group = Group.objects.get(name='Dealer')
        self.technician_group = Group.objects.get(name='Technician')
        self.masteruser_group = Group.objects.get(name='Master User')
        self.user_group = Group.objects.get(name='User')

        bed = DeviceType.objects.get(name=DeviceType.BED)

        self.company1 = G(Company, name="C1")
        self.site1 = G(BluuSite, slug="site1", company=self.company1,
                       many_inhabitants=False)
        self.room1 = G(Room, name='Room 1', bluusite=self.site1)
        self.room2 = G(Room, name='Room 2', bluusite=self.site1)
        self.device1 = G(Device, bluusite=self.site1, company=self.company1,
                         device_type=bed, room=self.room1)
        self.device2 = G(Device, bluusite=self.site1, company=self.company1,
                         device_type=bed, room=self.room2)

        self.bluu = G(BluuUser, username='bluu',
                      groups=[Group.objects.get(name='Bluu')])

        self.dealer = G(BluuUser, username='dealer', email='dealer@example.com')

        self.masteruser = G(BluuUser, username='masteruser',
                            email='masteruser@example.com')

    def testSingleBedOneSleep(self):
        """
        Tests if a bed algorithm works as expected
        """
        day = timedelta(days=1)
        three_minutes = timedelta(minutes=3)
        ten_minutes = timedelta(minutes=10)
        hour = timedelta(hours=1)
        two_hours = timedelta(hours=2)
        five_hours = timedelta(hours=5)
        today = datetime.today()
        yesterday = today - day

        # slept for one hour
        G(Status, device=self.device1, action=True, timestamp=yesterday)
        # stand up
        G(Status, device=self.device1, action=False, timestamp=yesterday + hour)
        # back to bed after 10 minutes
        G(Status, device=self.device1, action=True, timestamp=yesterday + hour +\
                                                    ten_minutes)
        # stand up after 5 hours
        G(Status, device=self.device1, action=False, timestamp=yesterday + hour +\
                ten_minutes + five_hours)

        site = BluuSite.objects.get(pk=self.site1.pk)
        data = site.get_sleeps()
        #json_data = site.get_sleeps()
        #data = json.loads(json_data)

        time_count = timedelta(hours=6, minutes=10)
        result = time_count.total_seconds()
        self.assertEquals(data[1][-1]['length'], result)

    def testSingleBedTwoSleeps(self):
        """
        Tests if a bed algorithm works as expected when there are two sleeps, 
        each over SLEEP_DURATION
        """
        day = timedelta(days=1)
        three_minutes = timedelta(minutes=3)
        ten_minutes = timedelta(minutes=10)
        hour = timedelta(hours=1)
        two_hours = timedelta(hours=2)
        five_hours = timedelta(hours=5)
        today = datetime.today()
        yesterday = today - day

        # slept for one hour
        G(Status, device=self.device1, action=True, timestamp=yesterday)
        # stand up
        G(Status, device=self.device1, action=False, timestamp=yesterday + hour)
        # back to bed after 10 minutes
        G(Status, device=self.device1, action=True, timestamp=yesterday + hour +\
                                                    ten_minutes)
        # stand up after 5 hours
        G(Status, device=self.device1, action=False, timestamp=yesterday + hour +\
                ten_minutes + five_hours)

        # go to bed again after 20 minutes - so second sleep starts here
        G(Status, device=self.device1, action=True, timestamp=yesterday + hour +\
                ten_minutes + five_hours + 2*ten_minutes)
        # wake up after 2 hours
        G(Status, device=self.device1, action=False, timestamp=yesterday + hour +\
                ten_minutes + five_hours + 2*ten_minutes + two_hours)


        site = BluuSite.objects.get(pk=self.site1.pk)
        data = site.get_sleeps()
        #json_data = site.get_sleeps()
        #data = json.loads(json_data)

        time_count = timedelta(hours=2)
        result = time_count.total_seconds()
        self.assertEquals(data[1][-1]['length'], result)

    def testSingleBedAlmostTwoSleeps(self):
        """
        Tests if a bed algorithm works as expected when there are two sleeps, 
        only first over SLEEP_DURATION and secon too short to be taken under
        consideration
        """
        day = timedelta(days=1)
        three_minutes = timedelta(minutes=3)
        ten_minutes = timedelta(minutes=10)
        hour = timedelta(hours=1)
        two_hours = timedelta(hours=2)
        five_hours = timedelta(hours=5)

        sleep_duration = timedelta(minutes=settings.SLEEP_DURATION)

        today = datetime.today()
        yesterday = today - day

        # slept for one hour
        G(Status, device=self.device1, action=True, timestamp=yesterday)
        # stand up
        G(Status, device=self.device1, action=False, timestamp=yesterday + hour)
        # back to bed after 10 minutes
        G(Status, device=self.device1, action=True, timestamp=yesterday + hour +\
                                                    ten_minutes)
        # stand up after 5 hours
        G(Status, device=self.device1, action=False, timestamp=yesterday + hour +\
                ten_minutes + five_hours)

        # go to bed again after 20 minutes - so second sleep starts here
        G(Status, device=self.device1, action=True, timestamp=yesterday + hour +\
                ten_minutes + five_hours + 2*ten_minutes)
        # wake up after less than SLEEP_DURATION
        G(Status, device=self.device1, action=False, timestamp=yesterday + hour +\
                ten_minutes + five_hours + 2*ten_minutes + sleep_duration-ten_minutes)


        site = BluuSite.objects.get(pk=self.site1.pk)
        data = site.get_sleeps()
        #json_data = site.get_sleeps()
        #data = json.loads(json_data)

        time_count = timedelta(hours=6, minutes=10)
        result = time_count.total_seconds()
        self.assertEquals(data[1][-1]['length'], result)

    def testSingleBedTwoSleepsLastSleep(self):
        """
        Tests if a bed algorithm works as expected when there are two sleeps, 
        each over SLEEP_DURATION and if proper sleeps is returned as last one
        """
        day = timedelta(days=1)
        three_minutes = timedelta(minutes=3)
        ten_minutes = timedelta(minutes=10)
        hour = timedelta(hours=1)
        two_hours = timedelta(hours=2)
        five_hours = timedelta(hours=5)
        today = datetime.today()
        yesterday = today - day

        # slept for one hour
        G(Status, device=self.device1, action=True, timestamp=yesterday)
        # stand up
        G(Status, device=self.device1, action=False, timestamp=yesterday + hour)
        # back to bed after 10 minutes
        G(Status, device=self.device1, action=True, timestamp=yesterday + hour +\
                                                    ten_minutes)
        # stand up after 5 hours
        G(Status, device=self.device1, action=False, timestamp=yesterday + hour +\
                ten_minutes + five_hours)

        # go to bed again after 20 minutes - so second sleep starts here
        G(Status, device=self.device1, action=True, timestamp=yesterday + hour +\
                ten_minutes + five_hours + 2*ten_minutes)
        # wake up after 2 hours
        G(Status, device=self.device1, action=False, timestamp=yesterday + hour +\
                ten_minutes + five_hours + 2*ten_minutes + two_hours)


        site = BluuSite.objects.get(pk=self.site1.pk)
        data = site.get_last_sleep()

        self.assertEquals(data, 7200)


