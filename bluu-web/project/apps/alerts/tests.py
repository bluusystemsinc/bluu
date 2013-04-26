import json
from apiv1.views import DeviceStatusSerializer, is_heartbeat
from django_webtest import WebTest
from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from accounts.models import BluuUser
from companies.models import Company
from bluusites.models import BluuSite
from devices.models import (Device, Status)


class AlertsTestCase(WebTest):
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

    def testAlerts(self):
        """
        Test if alert checks are fired
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
                        kwargs={'site_slug': self.bluusite1.slug,
                                'device_slug': self.device1.serial}),
                json.dumps(form_data),
                content_type='application/json;charset=utf-8',
                user='ws',
                status=201)
        self.assertEquals(Status.objects.filter(device=self.device1).count(), 1)


