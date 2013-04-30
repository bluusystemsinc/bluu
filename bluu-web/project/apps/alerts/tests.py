from datetime import timedelta, datetime
import time
import json
from alerts.models import UserAlertConfig, Alert, UserAlertDevice, AlertRunner
from apiv1.views import DeviceStatusSerializer, is_heartbeat
from django_webtest import WebTest
from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.core import mail

from accounts.models import BluuUser
from companies.models import Company
from bluusites.models import BluuSite
from devices.models import (Device, Status, DeviceType)



class AlertsOpenTestCase(WebTest):
    csrf_checks = False

    def post_status(self, slug, serial, form_data):
        return self.app.post(
                reverse('v1:create_status',
                        kwargs={'site_slug': self.bluusite1.slug,
                                'device_slug': self.device1.serial}),
                json.dumps(form_data),
                content_type='application/json;charset=utf-8',
                user='ws',
                status=201)

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script
        run_initialize_script()
        run_initialize_dicts_script()

        self.bluusite1 = G(BluuSite)

        # USERS
        self.ws_user = G(BluuUser, username='ws')
        self.ws_user.assign_group(group=Group.objects.get(name='WebService'),
                                  obj=self.bluusite1)
        self.user1 = G(BluuUser, username='test1')

        # DEVICES AND ALERTS
        self.window = DeviceType.objects.get(name=DeviceType.WINDOW)
        self.alert_o = Alert.objects.get(alert_type=Alert.OPEN)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.window)

        #set some alerts
        #UserAlertConfig.objects.create(bluusite=self.bluusite1,
        #                               device_type=self.window,
        #                               user=self.user1,
        #                               alert=self.alert_o,
        #                               duration=0,
        #                               unit=Alert.MINUTES
        #                               )

        UserAlertDevice.objects.create(alert=self.alert_o,
                                        device=self.device1,
                                        user=self.user1,
                                        duration=0,
                                        unit=Alert.MINUTES,
                                        email_notification=True,
                                        text_notification=True
                                       )

    def testOpenNotificationsSent(self):
        """
        Test if alert runner for open greater than is properly set
        """
        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "1.22",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "data": "123"}
        self.post_status(self.bluusite1.slug, self.device1.serial, form_data)

        # assert notifications sent
        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        print mail.outbox
        print mail.outbox[0].subject
        print mail.outbox[0].body
        # Verify that the subject of the first message is correct.
        #self.assertEqual(mail.outbox[0].subject, 'Subject here')


class AlertsOGTTestCase(WebTest):
    csrf_checks = False

    def post_status(self, slug, serial, form_data):
        return self.app.post(
                reverse('v1:create_status',
                        kwargs={'site_slug': self.bluusite1.slug,
                                'device_slug': self.device1.serial}),
                json.dumps(form_data),
                content_type='application/json;charset=utf-8',
                user='ws',
                status=201)

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script
        run_initialize_script()
        run_initialize_dicts_script()

        self.bluusite1 = G(BluuSite)

        #USERS
        self.ws_user = G(BluuUser, username='ws')
        self.ws_user.assign_group(group=Group.objects.get(name='WebService'),
                                  obj=self.bluusite1)
        self.user3 = G(BluuUser, username='test3')

        # ALERTS & DEVICES
        self.bed = DeviceType.objects.get(name=DeviceType.BED)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.bed)

        self.alert_ogt = Alert.objects.get(alert_type=Alert.OPEN_GREATER_THAN)

        #set some alerts
        UserAlertConfig.objects.create(bluusite=self.bluusite1,
                                       device_type=self.bed,
                                       user=self.user3,
                                       alert=self.alert_ogt,
                                       duration=10,
                                       unit=Alert.MINUTES
                                       )

        UserAlertDevice.objects.create(alert=self.alert_ogt,
                                        device=self.device1,
                                        user=self.user3,
                                        duration=10,
                                        unit=Alert.MINUTES,
                                        email_notification=True
                                       )

    def testOpenGT(self):
        """
        Test if alert runner for open greater than is properly set
        """
        form_data = {"serial": "serial",
                     "input4": "on", 
                     "float_data": "1.22", 
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1", 
                     "action": True,
                     "data": "123"}
        self.post_status(self.bluusite1.slug, self.device1.serial, form_data)

        # assert runner is set 10 minutes after the signal arrived
        runner = AlertRunner.objects.all()[0]
        self.assertEqual(runner.when, datetime.strptime("2013-03-07T23:10:09",
                                                        "%Y-%m-%dT%H:%M:%S"))

    def testOpenGTInvalidatedAndSetAgain(self):
        """
        Test if alert runner for open greater than is invalidated after close
        then properly set after open.
        """
        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "1.22",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "data": "123"}
        self.post_status(self.bluusite1.slug, self.device1.serial, form_data)

        form_data['action'] = False
        form_data['timestamp'] = "2013-03-07T23:15:09"
        self.post_status(self.bluusite1.slug, self.device1.serial, form_data)
        # assert runner is not set
        self.assertFalse(AlertRunner.objects.all().exists())

        form_data['action'] = True
        form_data['timestamp'] = "2013-03-07T23:15:09"
        self.post_status(self.bluusite1.slug, self.device1.serial, form_data)
        # assert runner is properly set again after open
        # alert is configured to be triggered after ten minutes so +10m here
        when = datetime.strptime("2013-03-07T23:25:09", "%Y-%m-%dT%H:%M:%S")
        runner = AlertRunner.objects.filter(when=when)
        self.assertTrue(runner.exists())


    def testOpenGTLeftIntactAfterSecondOpen(self):
        """
        Test if alert runner for open greater than is left intact after second
        "action": True (open) came.
        """
        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "1.22",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "data": "123"}
        self.post_status(self.bluusite1.slug, self.device1.serial, form_data)

        # assert alert runner is set
        when = datetime.strptime("2013-03-07T23:10:09", "%Y-%m-%dT%H:%M:%S")
        self.assertEqual(AlertRunner.objects.all()[0].when, when)

        form_data['timestamp'] = "2013-03-07T23:05:09"
        self.post_status(self.bluusite1.slug, self.device1.serial, form_data)
        # assert runner is left intact
        self.assertEqual(AlertRunner.objects.all()[0].when, when)

