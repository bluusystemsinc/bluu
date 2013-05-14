from datetime import timedelta, datetime
import time
import json
from django.conf import settings
from django_webtest import WebTest
from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.core import mail
from django.test.client import RequestFactory

from alerts.models import (UserAlertConfig, Alert, UserAlertDevice,
                           AlertRunner, UserAlertRoom)
from accounts.models import BluuUser
from bluusites.models import BluuSite, Room
from devices.models import Device, DeviceType
from alerts.tasks import alert_trigger_runners
from alerts.ajax_views import UserAlertConfigSetView


def post_status(testcase, slug, serial, form_data):
    return testcase.app.post(reverse('v1:create_status',
                                     kwargs={'site_slug': slug,
                                             'device_slug': serial}),
                             json.dumps(form_data),
                             content_type='application/json;charset=utf-8',
                             user='ws',
                             status=201)


class AlertsOpenTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script
        run_initialize_script()
        run_initialize_dicts_script()

        self.bluusite1 = G(BluuSite, first_name='Jan', last_name='Kowalski')

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
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert notifications sent
        # Test that two messages has been sent (email and text).
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject,
                         'Jan Kowalski alert - device open')


class AlertsOGTTestCase(WebTest):
    csrf_checks = False

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
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

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
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        form_data['action'] = False
        form_data['timestamp'] = "2013-03-07T23:15:09"
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)
        # assert runner is not set
        self.assertFalse(AlertRunner.objects.all().exists())

        form_data['action'] = True
        form_data['timestamp'] = "2013-03-07T23:15:09"
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)
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
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert alert runner is set
        when = datetime.strptime("2013-03-07T23:10:09", "%Y-%m-%dT%H:%M:%S")
        self.assertEqual(AlertRunner.objects.all()[0].when, when)

        form_data['timestamp'] = "2013-03-07T23:05:09"
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)
        # assert runner is left intact
        self.assertEqual(AlertRunner.objects.all()[0].when, when)


class AlertsOGTRunnerTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script
        run_initialize_script()
        run_initialize_dicts_script()

        self.bluusite1 = G(BluuSite, first_name="Jan", last_name="Kowalski")

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

        uad = UserAlertDevice.objects.create(alert=self.alert_ogt,
                                             device=self.device1,
                                             user=self.user3,
                                             duration=10,
                                             unit=Alert.MINUTES,
                                             email_notification=True
                                            )
        # set alert runner
        AlertRunner.objects.create(
            when=datetime.now(),
            user_alert_device=uad,
            since=datetime.strptime("2013-03-07T23:00:09",
                                    "%Y-%m-%dT%H:%M:%S"))

    def testOpenGTRunnerRun(self):
        """
        Test if alert runner for open greater than is properly run
        """
        #run alert runner task
        alert_trigger_runners.delay()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Jan Kowalski alert - device open too long')


class AlertsCGTRunnerTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script
        run_initialize_script()
        run_initialize_dicts_script()

        self.bluusite1 = G(BluuSite, first_name="Jan", last_name="Kowalski")

        #USERS
        self.ws_user = G(BluuUser, username='ws')
        self.ws_user.assign_group(group=Group.objects.get(name='WebService'),
                                  obj=self.bluusite1)
        self.user3 = G(BluuUser, username='test3')

        # ALERTS & DEVICES
        self.bed = DeviceType.objects.get(name=DeviceType.BED)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.bed)

        self.alert_cgt = Alert.objects.get(alert_type=Alert.CLOSED_GREATER_THAN)

        #set some alerts
        UserAlertConfig.objects.create(bluusite=self.bluusite1,
                                       device_type=self.bed,
                                       user=self.user3,
                                       alert=self.alert_cgt,
                                       duration=10,
                                       unit=Alert.MINUTES
                                       )

        uad = UserAlertDevice.objects.create(alert=self.alert_cgt,
                                             device=self.device1,
                                             user=self.user3,
                                             duration=10,
                                             unit=Alert.MINUTES,
                                             email_notification=True
                                            )
        # set alert runner
        AlertRunner.objects.create(
            when=datetime.now(),
            user_alert_device=uad,
            since=datetime.strptime("2013-03-07T23:00:09",
                                    "%Y-%m-%dT%H:%M:%S"))

    def testClosedGTRunnerRun(self):
        """
        Test if alert runner for open greater than is properly run
        """
        #run alert runner task
        alert_trigger_runners.delay()
        runner = AlertRunner.objects.all()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Jan Kowalski alert - device closed too long')



class AlertsOGTNMTestCase(WebTest):
    """
    Tests if alerts for open greater than no motion are set properly
    """
    csrf_checks = False

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
        self.user1 = G(BluuUser, username='test1')

        # ALERTS & DEVICES
        self.device1_type = DeviceType.objects.get(name=DeviceType.DOOR)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.device1_type)

        self.device2_type = DeviceType.objects.get(name=DeviceType.MOTION)
        self.device2 = G(Device, serial='motion', bluusite=self.bluusite1,
                         device_type=self.device2_type)

        self.alert1 = Alert.objects.get(
            alert_type=Alert.OPEN_GREATER_THAN_NO_MOTION)

        #set alert
        UserAlertConfig.objects.create(bluusite=self.bluusite1,
                                       device_type=self.device1_type,
                                       user=self.user1,
                                       alert=self.alert1,
                                       duration=10,
                                       unit=Alert.MINUTES
                                       )

        UserAlertDevice.objects.create(alert=self.alert1,
                                        device=self.device1,
                                        user=self.user1,
                                        duration=10,
                                        unit=Alert.MINUTES,
                                        email_notification=True
                                       )

    def testOpenGTNM(self):
        """
        Test if alert runner for open greater than no motion is properly set
        """
        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "1.22",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert runner is set 10 minutes after the signal arrived
        runner = AlertRunner.objects.all()[0]
        self.assertEqual(runner.when, datetime.strptime("2013-03-07T23:10:09",
                                                        "%Y-%m-%dT%H:%M:%S"))

    def testOpenGTNMSetAgainAfterMotion(self):
        """
        Test if alert runner for open greater than no motion is
        properly cancelled and set again after motion has arrived.
        """
        # set ogtnm
        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "1.22",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)
        when = datetime.strptime("2013-03-07T23:10:09", "%Y-%m-%dT%H:%M:%S")
        runner = AlertRunner.objects.filter(when=when)
        self.assertTrue(runner.exists())

        # send motion
        form_data = {"serial": "motion",
                     "input4": "on",
                     "float_data": "1.22",
                     "timestamp": "2013-03-07T23:05:09",
                     "signal": "1",
                     "action": True,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device2.serial, form_data)

        # assert runner is properly set again after motion
        # there should be only one runner
        self.assertEqual(1, AlertRunner.objects.all().count())
        # that is configured to be triggered after ten minutes after motion's
        # timestamp. So motion.timestamp plus 10 minutes is expected here
        when = datetime.strptime("2013-03-07T23:15:09", "%Y-%m-%dT%H:%M:%S")
        runner = AlertRunner.objects.filter(when=when)
        self.assertTrue(runner.exists())


class ResetRunnersAfterDeviceConfigChangeTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script
        run_initialize_script()
        run_initialize_dicts_script()

        self.factory = RequestFactory()

        self.bluusite1 = G(BluuSite)

        #USERS
        self.ws_user = G(BluuUser, username='ws')
        self.ws_user.assign_group(group=Group.objects.get(name='WebService'),
                                  obj=self.bluusite1)
        self.user1 = G(BluuUser, username='test1')

        # ALERTS & DEVICES
        self.bed = DeviceType.objects.get(name=DeviceType.BED)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.bed)

        self.alert_ogt = Alert.objects.get(alert_type=Alert.OPEN_GREATER_THAN)

        #set some alerts
        self.uac = UserAlertConfig.objects.create(bluusite=self.bluusite1,
                                       device_type=self.bed,
                                       user=self.user1,
                                       alert=self.alert_ogt,
                                       duration=10,
                                       unit=Alert.MINUTES
                                       )

        UserAlertDevice.objects.create(alert=self.alert_ogt,
                                        device=self.device1,
                                        user=self.user1,
                                        duration=10,
                                        unit=Alert.MINUTES,
                                        email_notification=True
                                       )

    def testAlertRunnerChangedAfterAlertConfigChangeSet(self):
        """
        Test if alert runner is properly changed after alert config
        has been changed.
        """
        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "1.22",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "data": "123"}


        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert runner is set 10 minutes after the signal arrived
        runner = AlertRunner.objects.all()[0]
        self.assertEqual(runner.when, datetime.strptime("2013-03-07T23:10:09",
                                                        "%Y-%m-%dT%H:%M:%S"))

        # change alert configuration
        config_data = {'user': self.user1.pk,
                       'device_type': self.device1.device_type.pk,
                       'alert': self.alert_ogt.pk,
                       'duration': "5",
                       'unit': Alert.MINUTES,
                       'email_notification': True,
                       'text_notification': False}


        request = self.factory.post('/fake-path', config_data,
                                    content_type='application/json')
        request.user = self.user1
        view = UserAlertConfigSetView.as_view()
        response = view(request)

        self.app.post(
                reverse('site_alerts:user_alert_config_set',
                        kwargs={'pk': self.bluusite1.pk}),
                json.dumps(config_data),
                content_type='application/json;charset=utf-8',
                user='test1',
                status=200)


        # assert runner is set 5 minutes after the signal arrived
        self.assertEqual(1, AlertRunner.objects.count())
        runner = AlertRunner.objects.all()[0]
        self.assertEqual(runner.when, datetime.strptime("2013-03-07T23:05:09",
                                                        "%Y-%m-%dT%H:%M:%S"))


class AlertsMotionInRoomTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script
        run_initialize_script()
        run_initialize_dicts_script()

        self.bluusite1 = G(BluuSite, first_name='Jan', last_name='Kowalski')
        self.room1 = G(Room, name="room1", bluusite=self.bluusite1)

        # USERS
        self.ws_user = G(BluuUser, username='ws')
        self.ws_user.assign_group(group=Group.objects.get(name='WebService'),
                                  obj=self.bluusite1)
        self.user1 = G(BluuUser, username='test1')

        # DEVICES AND ALERTS
        self.motion_type = DeviceType.objects.get(name=DeviceType.MOTION)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         room=self.room1, device_type=self.motion_type)

        self.alert = Alert.objects.get(alert_type=Alert.MOTION_IN_ROOM)
        UserAlertRoom.objects.create(alert=self.alert,
                                        room=self.room1,
                                        user=self.user1,
                                        duration=0,
                                        unit=Alert.MINUTES,
                                        email_notification=True,
                                        text_notification=True
                                       )

    def testMotionInRoomNotificationsSent(self):
        """
        Test if alert runner for motion in room is properly set
        """
        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "1.22",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert notifications sent
        # Test that two messages has been sent (email and text).
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject,
                         'Jan Kowalski alert - device open')



class AlertsNoMotionGreaterThanTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script
        run_initialize_script()
        run_initialize_dicts_script()

        self.bluusite1 = G(BluuSite, first_name='Jan', last_name='Kowalski')
        self.room1 = G(Room, name="room1", bluusite=self.bluusite1)

        # USERS
        self.ws_user = G(BluuUser, username='ws')
        self.ws_user.assign_group(group=Group.objects.get(name='WebService'),
                                  obj=self.bluusite1)
        self.user1 = G(BluuUser, username='test1')

        # DEVICES AND ALERTS
        self.motion_type = DeviceType.objects.get(name=DeviceType.MOTION)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         room=self.room1, device_type=self.motion_type)

        self.alert = Alert.objects.get(
            alert_type=Alert.NOMOTION_IN_ROOM_GREATER_THAN)
        self.uar = UserAlertRoom.objects.create(alert=self.alert,
                                                room=self.room1,
                                                user=self.user1,
                                                duration=10,
                                                unit=Alert.MINUTES,
                                                email_notification=True,
                                                text_notification=True
                                                )

    def testNoMotionGTSet(self):
        """
        Test if alert runner for nomotion in room greater than is properly set
        """
        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "1.22",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert runner set to be run after settings.MOTION_TIME_GAP + alert duration
        self.assertEqual(1, AlertRunner.objects.count())
        runner = AlertRunner.objects.all()[0]
        duration_time= datetime.strptime("2013-03-07T23:10:09",
                                         "%Y-%m-%dT%H:%M:%S")
        timegap = timedelta(minutes=settings.MOTION_TIME_GAP)

        self.assertEqual(runner.when, duration_time+timegap)

    def testNoMotionGTUpdated(self):
        """
        Test if alert runner for nomotion in room greater than is properly
        updated.
        """
        # Set alert runner
        when = datetime.strptime("2013-03-07T23:15:09", "%Y-%m-%dT%H:%M:%S")
        AlertRunner.objects.create(
            when=when,
            user_alert_room=self.uar,
            since=datetime.strptime("2013-03-07T23:00:09",
                                    "%Y-%m-%dT%H:%M:%S"))

        # Test if runner is updated properly after new status arrived
        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "1.22",
                     "timestamp": "2013-03-07T23:11:09",
                     "signal": "1",
                     "action": True,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert only one runner exists and
        # this runner is set to be run after
        # settings.MOTION_TIME_GAP + alert duration (10 minutes)
        self.assertEqual(1, AlertRunner.objects.count())

        runner = AlertRunner.objects.all()[0]
        duration_time= datetime.strptime("2013-03-07T23:21:09",
                                         "%Y-%m-%dT%H:%M:%S")
        timegap = timedelta(minutes=settings.MOTION_TIME_GAP)

        self.assertEqual(runner.when, duration_time+timegap)

    def testNoMotionInRoomGTNotificationsSent(self):
        """
        Test if alert runner for nomotion in room gt is properly set
        """
        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "1.22",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert notifications sent
        # Test that two messages has been sent (email and text).
        alert_trigger_runners.delay()
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[0].subject,
            'Jan Kowalski alert - no motion in room for too much time')
