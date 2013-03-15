import json
from django_webtest import WebTest
from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from accounts.models import BluuUser
from companies.models import Company
from bluusites.models import BluuSite
from devices.models import (Device, Status)


class SignalsTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        run_initialize_script()

        self.company1 = G(Company, name="C1")
        self.bluusite1 = G(BluuSite, ip='', company=self.company1)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1)

        
        self.user2 = G(BluuUser, username='test2',
                       groups=[Group.objects.get(name='Bluu')])

        self.ws_user = G(BluuUser, username='ws')
        self.ws_user.assign_group(group=Group.objects.get(name='WebService'),
                                  obj=self.bluusite1)

        self.user3 = G(BluuUser, username='test3')

    def testAccessToCreateDeviceStatus(self):
        """
        Test if user granted WebService role can update device status
        """
        form_data = {"serial": "serial",
                     "input4": "on", 
                     "float_data": "1.22", 
                     "timestamp": "2013-03-07T23:00:09.822000", 
                     "signal": "1", 
                     "action": "on", 
                     "data": "123"}
        self.app.post(
                reverse('v1:create_status', 
                        kwargs={'site_slug':self.bluusite1.slug,
                                'device_pk':self.device1.pk}),
                json.dumps(form_data),
                content_type='application/json;charset=utf-8',
                user='ws',
                status=201)
        self.assertEquals(Status.objects.filter(device=self.device1).count(), 1)

    def testSiteLastSeenUpdated(self):
        """
        Test if site's last seen is updated after device status is added
        """
        form_data = {"serial": "serial",
                     "input4": "on", 
                     "float_data": "1.22", 
                     "timestamp": "2013-03-07T23:00:09.822000", 
                     "signal": "1", 
                     "action": "on", 
                     "data": "123"}
        self.app.post(
                reverse('v1:create_status', 
                        kwargs={'site_slug':self.bluusite1.slug,
                                'device_pk':self.device1.pk}),
                json.dumps(form_data),
                content_type='application/json;charset=utf-8',
                user='ws',
                status=201)
        status = Status.objects.get(device=self.device1)
        site = BluuSite.objects.get(pk=self.bluusite1.pk)
        self.assertEquals(site.last_seen, status.created)
 
    def testSiteIPUpdated(self):
        """
        Test if site's IP is updated after device status is added
        """
        self.assertEquals(self.bluusite1.ip, '')
        form_data = {"serial": "serial",
                     "input4": "on", 
                     "float_data": "1.22", 
                     "timestamp": "2013-03-07T23:00:09.822000", 
                     "signal": "1", 
                     "action": "on", 
                     "data": "123"}
        self.app.post(
                reverse('v1:create_status', 
                        kwargs={'site_slug':self.bluusite1.slug,
                                'device_pk':self.device1.pk}),
                json.dumps(form_data),
                content_type='application/json;charset=utf-8',
                user='ws',
                status=201)
        site = BluuSite.objects.get(pk=self.bluusite1.pk)
        self.assertEquals(site.ip, '127.0.0.1')
 
