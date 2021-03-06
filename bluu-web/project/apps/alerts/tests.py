import json

import datetime
from companies.models import Company
from django.conf import settings
from django_webtest import WebTest
from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.core import mail
from django.test.client import RequestFactory
from alerts.models import (UserAlertConfig, Alert, UserAlertDevice,
                           AlertRunner, UserAlertRoom, UserAlertScaleConfig,
                           UserAlertScale, SystemAlertRunner)
from accounts.models import BluuUser
from bluusites.models import BluuSite, Room
from devices.models import Device, DeviceType, Status
from alerts.tasks import (alert_trigger_runners, alert_trigger_system_runners,
                          alert_trigger_motion_in_room_checks)
from alerts.ajax_views import (UserAlertConfigSetView )
from mock import patch


def post_status(testcase, slug, serial, form_data):
    return testcase.app.post(reverse('v1:create_status',
                                     kwargs={'site_slug': slug,
                                             'device_slug': serial}),
                             json.dumps(form_data),
                             content_type='application/json;charset=utf-8',
                             user='{}_{}'.format(
                                 settings.WEBSERVICE_USERNAME_PREFIX, slug),
                             status=201)


class AlertsOpenTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script

        run_initialize_script()
        run_initialize_dicts_script()

        self.bluusite1 = G(BluuSite, first_name='Jan', last_name='Kowalski',
                           site_alerts=True, site_dealer_alerts=True)

        # USERS
        self.user1 = G(BluuUser, username='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)

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
        Test if notification for open greater than is sent
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
        self.user1 = G(BluuUser, username='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)


        # ALERTS & DEVICES
        self.bed = DeviceType.objects.get(name=DeviceType.BED)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.bed)

        self.alert_ogt = Alert.objects.get(alert_type=Alert.OPEN_GREATER_THAN)

        #set some alerts
        UserAlertConfig.objects.create(bluusite=self.bluusite1,
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
        self.assertEqual(runner.when,
                         datetime.datetime.strptime("2013-03-07T23:10:09",
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
        form_data['timestamp'] = "2013-03-07T23:20:09"
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)
        # assert runner is properly set again after open
        # alert is configured to be triggered after ten minutes so +10m here
        when = datetime.datetime.strptime("2013-03-07T23:30:09",
                                          "%Y-%m-%dT%H:%M:%S")
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
        when = datetime.datetime.strptime("2013-03-07T23:10:09",
                                          "%Y-%m-%dT%H:%M:%S")
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
        self.user1 = G(BluuUser, username='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)


        # ALERTS & DEVICES
        self.bed = DeviceType.objects.get(name=DeviceType.BED)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.bed)

        self.alert_ogt = Alert.objects.get(alert_type=Alert.OPEN_GREATER_THAN)

        #set some alerts
        UserAlertConfig.objects.create(bluusite=self.bluusite1,
                                       device_type=self.bed,
                                       user=self.user1,
                                       alert=self.alert_ogt,
                                       duration=10,
                                       unit=Alert.MINUTES
        )

        uad = UserAlertDevice.objects.create(alert=self.alert_ogt,
                                             device=self.device1,
                                             user=self.user1,
                                             duration=10,
                                             unit=Alert.MINUTES,
                                             email_notification=True
        )
        # set alert runner
        AlertRunner.objects.create(
            when=datetime.datetime.now(),
            user_alert_device=uad,
            since=datetime.datetime.strptime("2013-03-07T23:00:09",
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
        self.user1 = G(BluuUser, username='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)


        # ALERTS & DEVICES
        self.bed = DeviceType.objects.get(name=DeviceType.BED)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.bed)

        self.alert_cgt = Alert.objects.get(alert_type=Alert.CLOSED_GREATER_THAN)

        #set some alerts
        UserAlertConfig.objects.create(bluusite=self.bluusite1,
                                       device_type=self.bed,
                                       user=self.user1,
                                       alert=self.alert_cgt,
                                       duration=10,
                                       unit=Alert.MINUTES
        )

        uad = UserAlertDevice.objects.create(alert=self.alert_cgt,
                                             device=self.device1,
                                             user=self.user1,
                                             duration=10,
                                             unit=Alert.MINUTES,
                                             email_notification=True
        )
        # set alert runner
        AlertRunner.objects.create(
            when=datetime.datetime.now(),
            user_alert_device=uad,
            since=datetime.datetime.strptime("2013-03-07T23:00:09",
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
        self.user1 = G(BluuUser, username='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)


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
        self.assertEqual(runner.when,
                         datetime.datetime.strptime("2013-03-07T23:10:09",
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
        when = datetime.datetime.strptime("2013-03-07T23:10:09",
                                          "%Y-%m-%dT%H:%M:%S")
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
        when = datetime.datetime.strptime("2013-03-07T23:15:09",
                                          "%Y-%m-%dT%H:%M:%S")
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
        self.user1 = G(BluuUser, username='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)

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
        self.assertEqual(runner.when,
                         datetime.datetime.strptime("2013-03-07T23:10:09",
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
        self.assertEqual(runner.when,
                         datetime.datetime.strptime("2013-03-07T23:05:09",
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
        self.user1 = G(BluuUser, username='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)

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
                         'Jan Kowalski alert - motion in room')


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
        self.user1 = G(BluuUser, username='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)

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
        duration_time = datetime.datetime.strptime("2013-03-07T23:10:09",
                                                   "%Y-%m-%dT%H:%M:%S")
        timegap = datetime.timedelta(minutes=settings.MOTION_TIME_GAP)

        self.assertEqual(runner.when, duration_time + timegap)

    def testNoMotionGTUpdated(self):
        """
        Test if alert runner for nomotion in room greater than is properly
        updated.
        """
        # Set alert runner
        when = datetime.datetime.strptime("2013-03-07T23:15:09",
                                          "%Y-%m-%dT%H:%M:%S")
        AlertRunner.objects.create(
            when=when,
            user_alert_room=self.uar,
            since=datetime.datetime.strptime("2013-03-07T23:00:09",
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
        duration_time = datetime.datetime.strptime("2013-03-07T23:21:09",
                                                   "%Y-%m-%dT%H:%M:%S")
        timegap = datetime.timedelta(minutes=settings.MOTION_TIME_GAP)

        self.assertEqual(runner.when, duration_time + timegap)

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


class AlertsActiveInPeriodLTTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script

        run_initialize_script()
        run_initialize_dicts_script()

        self.bluusite1 = G(BluuSite, first_name="Jan", last_name="Kowalski")

        #USERS
        self.user1 = G(BluuUser, username='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)

        # ALERTS & DEVICES
        self.bed = DeviceType.objects.get(name=DeviceType.BED)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.bed)

        self.alert = Alert.objects.get(
            alert_type=Alert.ACTIVE_IN_PERIOD_LESS_THAN)

        #set some alerts
        UserAlertConfig.objects.create(bluusite=self.bluusite1,
                                       device_type=self.bed,
                                       user=self.user1,
                                       alert=self.alert,
                                       duration=10,
                                       unit=Alert.HOURS)

        uad = UserAlertDevice.objects.create(alert=self.alert,
                                             device=self.device1,
                                             user=self.user1,
                                             duration=10,
                                             unit=Alert.HOURS,
                                             email_notification=True)

    def testAlertNotSetForActiveStatus(self):
        """
        Test if alert runner for inactive in period greater than
        isn't set after "actitve / open" signal arrived
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
        self.assertEqual(AlertRunner.objects.count(), 0)

    def testAlertSetForFirstStatus(self):
        """
        Test if alert runner for active in period less than
        is properly set when there are no other statuses recorded
        """
        strptime = datetime.datetime.strptime
        #with mock_now(datetime.datetime(2013, 03, 07, 23, 0, 9)):
        with patch('alerts.models.datetime') as mock_now:
            mock_now.now.return_value = datetime.datetime(2013, 03, 07, 23, 0,
                                                          9)
            form_data = {"serial": "serial",
                         "input4": "on",
                         "float_data": "1.22",
                         "timestamp": "2013-03-07T23:00:09",
                         "signal": "1",
                         "action": False,
                         "data": "123"}
            post_status(self, self.bluusite1.slug, self.device1.serial,
                        form_data)

            # assert runner is set to be run immediately because activity time
            # is less than 10h
            runner = AlertRunner.objects.all()[0]
            self.assertEqual(runner.when, strptime("2013-03-07T23:00:09",
                                                   "%Y-%m-%dT%H:%M:%S"))

    def testAlertSetForManyStatuses(self):
        """
        Test if alert runner for active in period less than
        is properly set when there are many statuses recorded
        """
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.bed,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T20:00:09",
                              action=True)
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.bed,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T23:30:09",
                              action=False)
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.bed,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T23:40:09",
                              action=True)
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.bed,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T06:00:09",
                              action=False)
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.bed,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T12:00:09",
                              action=True)

        #with mock_now(datetime.datetime(2013, 03, 07, 23, 0, 9)):
        with patch('alerts.models.datetime') as mock_now:
            mock_now.now.return_value = datetime.datetime(2013, 03, 07, 23, 0,
                                                          9)
            #mock_now.side_effect = lambda *args, **kw: datetime(*args, **kw)

            form_data = {"serial": "serial",
                         "input4": "on",
                         "float_data": "1.22",
                         "timestamp": "2013-03-07T23:00:09",
                         "signal": "1",
                         "action": False,
                         "data": "123"}
            post_status(self, self.bluusite1.slug, self.device1.serial,
                        form_data)

            # assert runner is set properly
            self.assertEqual(AlertRunner.objects.count(), 1)
            runner = AlertRunner.objects.all()[0]
            self.assertEqual(runner.when,
                             datetime.datetime.strptime("2013-03-08T13:00:09",
                                                        "%Y-%m-%dT%H:%M:%S"))


class AlertsActiveInPeriodLTRunnerTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script

        run_initialize_script()
        run_initialize_dicts_script()

        self.bluusite1 = G(BluuSite, first_name="Jan", last_name="Kowalski")

        #USERS
        self.user1 = G(BluuUser, username='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)


        # ALERTS & DEVICES
        self.bed = DeviceType.objects.get(name=DeviceType.BED)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.bed)

        self.alert = Alert.objects.get(
            alert_type=Alert.ACTIVE_IN_PERIOD_LESS_THAN)

        #set some alerts
        UserAlertConfig.objects.create(bluusite=self.bluusite1,
                                       device_type=self.bed,
                                       user=self.user1,
                                       alert=self.alert,
                                       duration=10,
                                       unit=Alert.HOURS
        )

        uad = UserAlertDevice.objects.create(alert=self.alert,
                                             device=self.device1,
                                             user=self.user1,
                                             duration=10,
                                             unit=Alert.HOURS,
                                             email_notification=True
        )
        # set alert runner
        AlertRunner.objects.create(
            when=datetime.datetime.now(),
            user_alert_device=uad,
            since=datetime.datetime.strptime("2013-03-07T23:00:09",
                                             "%Y-%m-%dT%H:%M:%S"))

    def testAIPLTRunnerRun(self):
        """
        Test if alert runner for open less than in period is properly run
        """
        #run alert runner task
        alert_trigger_runners.delay()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Jan Kowalski alert - active less than expected in a period')


class AlertsActiveInPeriodGTTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script

        run_initialize_script()
        run_initialize_dicts_script()

        self.bluusite1 = G(BluuSite, first_name="Jan", last_name="Kowalski")

        #USERS
        self.user1 = G(BluuUser, username='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)


        # ALERTS & DEVICES
        self.seat = DeviceType.objects.get(name=DeviceType.SEAT)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.seat)

        self.alert = Alert.objects.get(
            alert_type=Alert.ACTIVE_IN_PERIOD_GREATER_THAN)

        #set some alerts
        UserAlertConfig.objects.create(bluusite=self.bluusite1,
                                       device_type=self.seat,
                                       user=self.user1,
                                       alert=self.alert,
                                       duration=6,
                                       unit=Alert.HOURS
        )

        uad = UserAlertDevice.objects.create(alert=self.alert,
                                             device=self.device1,
                                             user=self.user1,
                                             duration=6,
                                             unit=Alert.HOURS,
                                             email_notification=True
        )

    def testAlertNotSetForInactiveStatus(self):
        """
        Test if alert runner for active in period greater than
        isn't set after "inactive / closed" signal arrived
        """
        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "1.22",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": False,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert runner is set 10 minutes after the signal arrived
        self.assertEqual(AlertRunner.objects.count(), 0)

    def testAlertSetForFirstStatus(self):
        """
        Test if alert runner for active in period greater than
        is properly set when there are no other statuses recorded
        """
        strptime = datetime.datetime.strptime
        #with mock_now(datetime.datetime(2013, 03, 07, 23, 0, 9)):
        with patch('alerts.models.datetime') as mock_now:
            mock_now.now.return_value = datetime.datetime(2013, 03, 07, 23, 0,
                                                          9)
            form_data = {"serial": "serial",
                         "input4": "on",
                         "float_data": "1.22",
                         "timestamp": "2013-03-07T23:00:09",
                         "signal": "1",
                         "action": True,
                         "data": "123"}
            post_status(self, self.bluusite1.slug, self.device1.serial,
                        form_data)

            # assert runner is set to be run after 10 hours of activity
            # since now
            runner = AlertRunner.objects.all()[0]
            self.assertEqual(runner.when, strptime("2013-03-08T05:00:09",
                                                   "%Y-%m-%dT%H:%M:%S"))

    def testAlertSetForManyStatuses(self):
        """
        Test if alert runner for active in period greater than
        is properly set when there are many statuses recorded
        """
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.seat,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T20:00:09",
                              action=True)
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.seat,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T23:30:09",
                              action=False)
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.seat,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T09:30:09",
                              action=True)
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.seat,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T10:40:09",
                              action=False)
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.seat,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T20:00:09",
                              action=True)
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.seat,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T21:00:09",
                              action=False)

        #with mock_now(datetime.datetime(2013, 03, 07, 23, 0, 9)):
        with patch('alerts.models.datetime') as mock_now:
            mock_now.now.return_value = datetime.datetime(2013, 03, 07, 23, 0,
                                                          9)
            #mock_now.side_effect = lambda *args, **kw: datetime(*args, **kw)

            form_data = {"serial": "serial",
                         "input4": "on",
                         "float_data": "1.22",
                         "timestamp": "2013-03-07T23:00:09",
                         "signal": "1",
                         "action": True,
                         "data": "123"}
            post_status(self, self.bluusite1.slug, self.device1.serial,
                        form_data)

            # assert runner is set properly
            self.assertEqual(AlertRunner.objects.count(), 1)
            runner = AlertRunner.objects.all()[0]
            self.assertEqual(runner.when,
                             datetime.datetime.strptime("2013-03-08T02:20:09",
                                                        "%Y-%m-%dT%H:%M:%S"))


class AlertsActiveInPeriodGTRunnerTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script

        run_initialize_script()
        run_initialize_dicts_script()

        self.bluusite1 = G(BluuSite, first_name="Jan", last_name="Kowalski")

        #USERS
        self.user1 = G(BluuUser, username='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)


        # ALERTS & DEVICES
        self.seat = DeviceType.objects.get(name=DeviceType.SEAT)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.seat)

        self.alert = Alert.objects.get(
            alert_type=Alert.ACTIVE_IN_PERIOD_GREATER_THAN)

        #set some alerts
        UserAlertConfig.objects.create(bluusite=self.bluusite1,
                                       device_type=self.seat,
                                       user=self.user1,
                                       alert=self.alert,
                                       duration=10,
                                       unit=Alert.HOURS
        )

        uad = UserAlertDevice.objects.create(alert=self.alert,
                                             device=self.device1,
                                             user=self.user1,
                                             duration=10,
                                             unit=Alert.HOURS,
                                             email_notification=True
        )
        # set alert runner
        AlertRunner.objects.create(
            when=datetime.datetime.now(),
            user_alert_device=uad,
            since=datetime.datetime.strptime("2013-03-07T23:00:09",
                                             "%Y-%m-%dT%H:%M:%S"))

    def testAIPLTRunnerRun(self):
        """
        Test if alert runner for open greater than in period is properly run
        """
        #run alert runner task
        alert_trigger_runners.delay()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Jan Kowalski alert - active greater than expected in a period')


class ScaleAlertChangedAfterScaleConfigChangeTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script

        run_initialize_script()
        run_initialize_dicts_script()

        self.factory = RequestFactory()

        self.bluusite1 = G(BluuSite, first_name='Jan', last_name='Kowalski')

        #USERS
        self.user1 = G(BluuUser, username='test1', password='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)


        # ALERTS & DEVICES
        self.scale = DeviceType.objects.get(name=DeviceType.SCALE)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.scale)

        self.alert_wgt = Alert.objects.get(alert_type=Alert.WEIGHT_GREATER_THAN)

        #set some alerts
        self.uac = UserAlertScaleConfig.objects.create(bluusite=self.bluusite1,
                                                       device_type=self.scale,
                                                       user=self.user1,
                                                       alert=self.alert_wgt,
                                                       weight=100)

        UserAlertScale.objects.create(alert=self.alert_wgt,
                                      device=self.device1,
                                      user=self.user1,
                                      weight=100,
                                      email_notification=True)


    def testUserAlertScaleChangedAfterAlertConfigChangeSet(self):
        """
        Test if alert sclae is properly changed after alert config
        has been changed.
        """
        # change alert configuration
        config_data = {'user': self.user1.pk,
                       'device_type': self.device1.device_type.pk,
                       'alert': self.alert_wgt.pk,
                       'weight': "90",
                       'email_notification': True,
                       'text_notification': False}
        res = self.app.post(reverse('site_alerts:user_alert_scale_config_set',
                                    kwargs={'pk': self.bluusite1.pk}),
                            json.dumps(config_data),
                            content_type='application/json;charset=utf-8',
                            user=self.user1.username,
                            status=200)

        self.assertEqual(UserAlertScale.objects.count(), 1)
        self.assertEqual(UserAlertScale.objects.all()[0].weight, 90)

    def testWGTNotificationSent(self):
        """
        Test if notification for weight greater than is sent
        """
        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "120",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert notifications sent
        # Test that one message has been sent (email and no text).
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Jan Kowalski alert - weight greater than expected')


class ScaleWLTAlertSentTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script

        run_initialize_script()
        run_initialize_dicts_script()

        self.factory = RequestFactory()

        self.bluusite1 = G(BluuSite, first_name='Jan', last_name='Kowalski')

        #USERS
        self.user1 = G(BluuUser, username='test1', password='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)


        # ALERTS & DEVICES
        self.scale = DeviceType.objects.get(name=DeviceType.SCALE)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.scale)

        self.alert_wlt = Alert.objects.get(alert_type=Alert.WEIGHT_LESS_THAN)

        #set some alerts
        self.uac = UserAlertScaleConfig.objects.create(bluusite=self.bluusite1,
                                                       device_type=self.scale,
                                                       user=self.user1,
                                                       alert=self.alert_wlt,
                                                       weight=100)

        UserAlertScale.objects.create(alert=self.alert_wlt,
                                      device=self.device1,
                                      user=self.user1,
                                      weight=100,
                                      email_notification=True)

    def testWLTNotificationSent(self):
        """
        Test if notification for weight less than is sent
        """
        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "120",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert notifications sent
        # Test that one message has been sent (email and no text).
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Jan Kowalski alert - weight less than expected')


class ScaleSUAlertSentTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script

        run_initialize_script()
        run_initialize_dicts_script()

        self.factory = RequestFactory()

        self.bluusite1 = G(BluuSite, first_name='Jan', last_name='Kowalski')

        #USERS
        self.user1 = G(BluuUser, username='test1', password='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)


        # ALERTS & DEVICES
        self.scale = DeviceType.objects.get(name=DeviceType.SCALE)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.scale)

        self.alert_su = Alert.objects.get(alert_type=Alert.SCALE_USED)

        #set some alerts
        self.uac = UserAlertScaleConfig.objects.create(bluusite=self.bluusite1,
                                                       device_type=self.scale,
                                                       user=self.user1,
                                                       alert=self.alert_su,
                                                       weight=100)

        UserAlertScale.objects.create(alert=self.alert_su,
                                      device=self.device1,
                                      user=self.user1,
                                      weight=100,
                                      email_notification=True)


    def testSUNotificationSent(self):
        """
        Test if notification for weight less than is sent
        """
        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "120",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert notifications sent
        # Test that one message has been sent (email and no text).
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Jan Kowalski alert - scale used')


class SysAlertBatteryTestCase(WebTest):
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

        self.factory = RequestFactory()
        self.company1 = G(Company, name="C1")
        self.bluusite1 = G(BluuSite, company=self.company1,
                           first_name='Jan', last_name='Kowalski',
                           email='jkowalski@example.com')

        #USERS
        self.user1 = G(BluuUser, username='test1', password='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)

        self.user2 = G(BluuUser, username='test2', password='test2')
        self.user2.assign_group(group=Group.objects.get(name='Master User'),
                                obj=self.bluusite1)

        self.dealer = G(BluuUser, username='dealer',
                        first_name='Dealer', last_name='Dealer',
                        email='dealer@example.com', cell_text_email='')

        # ALERTS & DEVICES
        self.door = DeviceType.objects.get(name=DeviceType.DOOR)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.door)

        self.alert_battery = Alert.objects.get(alert_type=Alert.SYSTEM_BATTERY)

    def testBatteryNotificationsSent(self):
        """
        Test if system notifications for battery are sent
        """
        self.company1.assign_user(self.dealer, 'dealer@example.com',
                                  self.dealer_group)

        dealer = BluuUser.objects.get(username='dealer')
        #self.assertTrue(dealer.has_perm('bluusites.change_bluusite',
        #                                self.site1))

        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "120",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "battery": True,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert notifications sent
        # Test that three messages has been sent: email and text for master user
        #  and email for dealer
        self.assertEqual(len(mail.outbox), 3)
        #for email in mail.outbox:
        #    print email.subject, email.body

    def testBatteryRunnersSet(self):
        """
        Test if system runners for battery are set
        """
        self.company1.assign_user(self.dealer, 'dealer@example.com',
                                  self.dealer_group)

        dealer = BluuUser.objects.get(username='dealer')
        #self.assertTrue(dealer.has_perm('bluusites.change_bluusite',
        #                                self.site1))

        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "120",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "battery": True,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert runners set
        self.assertEquals(SystemAlertRunner.objects.filter(
            alert__alert_type=Alert.SYSTEM_BATTERY).count(), 3)

    def testBatteryRunnersRun(self):
        """
        Test if system runners for battery are run
        """

        self.company1.assign_user(self.dealer, 'dealer@example.com',
                                  self.dealer_group)

        # set alert runner
        SystemAlertRunner.objects.create(
            bluusite=self.bluusite1,
            device=self.device1,
            alert=Alert.objects.get(alert_type=Alert.SYSTEM_BATTERY),
            when=datetime.datetime.now(),
            period='period',
            since=datetime.datetime.strptime("2013-03-07T23:00:09",
                                             "%Y-%m-%dT%H:%M:%S"))

        alert_trigger_system_runners.delay()
        self.assertEqual(len(mail.outbox), 3)


class SysDeviceOfflineTestCase(WebTest):
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

        self.factory = RequestFactory()
        self.company1 = G(Company, name="C1")
        self.bluusite1 = G(BluuSite, company=self.company1,
                           first_name='Jan', last_name='Kowalski',
                           email='jkowalski@example.com')

        #USERS
        self.user1 = G(BluuUser, username='test1', password='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)

        self.user2 = G(BluuUser, username='test2', password='test2')
        self.user2.assign_group(group=Group.objects.get(name='Master User'),
                                obj=self.bluusite1)

        self.dealer = G(BluuUser, username='dealer',
                        first_name='Dealer', last_name='Dealer',
                        email='dealer@example.com', cell_text_email='')

        # ALERTS & DEVICES
        self.door = DeviceType.objects.get(name=DeviceType.DOOR)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.door)

        self.alert_battery = Alert.objects.get(alert_type=Alert.SYSTEM_BATTERY)

    def testDeviceOfflineRunnersSet(self):
        """
        Test if system runners for device offline are set
        """
        self.company1.assign_user(self.dealer, 'dealer@example.com',
                                  self.dealer_group)

        dealer = BluuUser.objects.get(username='dealer')
        #self.assertTrue(dealer.has_perm('bluusites.change_bluusite',
        #                                self.site1))

        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "120",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "battery": True,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert 4 runners set (15m, 24h, week, month)
        self.assertEquals(SystemAlertRunner.objects.filter(
            alert__alert_type=Alert.SYSTEM_DEVICE_OFFLINE).count(), 4)

    def testDeviceOfflineRunnersRun(self):
        """
        Test if system runners for device offline are run
        """

        self.company1.assign_user(self.dealer, 'dealer@example.com',
                                  self.dealer_group)

        # set alert runner
        SystemAlertRunner.objects.create(
            bluusite=self.bluusite1,
            device=self.device1,
            alert=Alert.objects.get(alert_type=Alert.SYSTEM_DEVICE_OFFLINE),
            when=datetime.datetime.now(),
            period='period',
            since=datetime.datetime.strptime("2013-03-07T23:00:09",
                                             "%Y-%m-%dT%H:%M:%S"))

        alert_trigger_system_runners.delay()
        self.assertEqual(len(mail.outbox), 3)


class SysBluuSiteOfflineTestCase(WebTest):
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

        self.factory = RequestFactory()
        self.company1 = G(Company, name="C1")
        self.bluusite1 = G(BluuSite, company=self.company1,
                           first_name='Jan', last_name='Kowalski',
                           email='jkowalski@example.com')

        #USERS
        self.user1 = G(BluuUser, username='test1', password='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)

        self.user2 = G(BluuUser, username='test2', password='test2')
        self.user2.assign_group(group=Group.objects.get(name='Master User'),
                                obj=self.bluusite1)

        self.dealer = G(BluuUser, username='dealer',
                        first_name='Dealer', last_name='Dealer',
                        email='dealer@example.com', cell_text_email='')

        # ALERTS & DEVICES
        self.door = DeviceType.objects.get(name=DeviceType.DOOR)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.door)

        self.alert_battery = Alert.objects.get(alert_type=Alert.SYSTEM_BATTERY)

    def testBluuSiteOfflineRunnersSet(self):
        """
        Test if system runners for bluusite offline are set
        """
        self.company1.assign_user(self.dealer, 'dealer@example.com',
                                  self.dealer_group)

        dealer = BluuUser.objects.get(username='dealer')
        #self.assertTrue(dealer.has_perm('bluusites.change_bluusite',
        #                                self.site1))

        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "120",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "action": True,
                     "battery": True,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert 4 runners set (15m, 24h, week, month)
        self.assertEquals(SystemAlertRunner.objects.filter(
            alert__alert_type=Alert.SYSTEM_SITE_OFFLINE).count(), 4)

    def testBluuSiteHeartbeatOfflineRunnersSet(self):
        """
        Test if system runners for bluusite offline are set after heartbeat
        """
        self.company1.assign_user(self.dealer, 'dealer@example.com',
                                  self.dealer_group)

        dealer = BluuUser.objects.get(username='dealer')
        #self.assertTrue(dealer.has_perm('bluusites.change_bluusite',
        #                                self.site1))

        form_data = {"last_seen": "2013-03-07T23:00:09"}

        self.app.put(reverse('v1:site_heartbeat',
                             kwargs={'site_slug': self.bluusite1.slug}),
                     json.dumps(form_data),
                     content_type='application/json;charset=utf-8',
                     user='{}_{}'.format(
                         settings.WEBSERVICE_USERNAME_PREFIX,
                         self.bluusite1.slug),
                     status=200)

        #post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert 4 runners set (15m, 24h, week, month)
        self.assertEquals(SystemAlertRunner.objects.filter(
            alert__alert_type=Alert.SYSTEM_SITE_OFFLINE).count(), 4)

    def testBluuSiteOfflineRunnersRun(self):
        """
        Test if system runners for device offline are run
        """

        self.company1.assign_user(self.dealer, 'dealer@example.com',
                                  self.dealer_group)

        # set alert runner
        SystemAlertRunner.objects.create(
            bluusite=self.bluusite1,
            alert=Alert.objects.get(alert_type=Alert.SYSTEM_SITE_OFFLINE),
            when=datetime.datetime.now(),
            period='period',
            since=datetime.datetime.strptime("2013-03-07T23:00:09",
                                             "%Y-%m-%dT%H:%M:%S"))

        alert_trigger_system_runners.delay()
        self.assertEqual(len(mail.outbox), 3)

    def testDeviceOfflineRunnersNotRunIfSiteOffline(self):
        """
        Test if system runners for device offline are not run if whole site
        is offline
        """

        self.company1.assign_user(self.dealer, 'dealer@example.com',
                                  self.dealer_group)

        # set alert runner
        SystemAlertRunner.objects.create(
            bluusite=self.bluusite1,
            device=self.device1,
            alert=Alert.objects.get(alert_type=Alert.SYSTEM_DEVICE_OFFLINE),
            when=datetime.datetime.now(),
            period='period',
            since=datetime.datetime.strptime("2013-03-07T23:00:09",
                                             "%Y-%m-%dT%H:%M:%S"))

        # set alert runner
        SystemAlertRunner.objects.create(
            bluusite=self.bluusite1,
            alert=Alert.objects.get(alert_type=Alert.SYSTEM_SITE_OFFLINE),
            when=datetime.datetime.now(),
            period='period',
            since=datetime.datetime.strptime("2013-03-07T23:00:09",
                                             "%Y-%m-%dT%H:%M:%S"))

        alert_trigger_system_runners.delay()
        self.assertEqual(len(mail.outbox), 3)


class SysAlertTamperTestCase(WebTest):
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

        self.factory = RequestFactory()
        self.company1 = G(Company, name="C1")
        self.bluusite1 = G(BluuSite, company=self.company1,
                           first_name='Jan', last_name='Kowalski',
                           email='jkowalski@example.com')

        #USERS
        self.user1 = G(BluuUser, username='test1', password='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)

        self.user2 = G(BluuUser, username='test2', password='test2')
        self.user2.assign_group(group=Group.objects.get(name='Master User'),
                                obj=self.bluusite1)

        self.dealer = G(BluuUser, username='dealer',
                        first_name='Dealer', last_name='Dealer',
                        email='dealer@example.com', cell_text_email='')

        # ALERTS & DEVICES
        self.door = DeviceType.objects.get(name=DeviceType.DOOR)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         device_type=self.door)

        self.alert_tamper = Alert.objects.get(alert_type=Alert.SYSTEM_TAMPER)

    def testTamperNotificationsSent(self):
        """
        Test if system notifications for battery are sent
        """
        self.company1.assign_user(self.dealer, 'dealer@example.com',
                                  self.dealer_group)

        dealer = BluuUser.objects.get(username='dealer')
        #self.assertTrue(dealer.has_perm('bluusites.change_bluusite',
        #                                self.site1))

        form_data = {"serial": "serial",
                     "input4": "on",
                     "float_data": "120",
                     "timestamp": "2013-03-07T23:00:09",
                     "signal": "1",
                     "tamper": True,
                     "action": True,
                     "battery": False,
                     "data": "123"}
        post_status(self, self.bluusite1.slug, self.device1.serial, form_data)

        # assert notifications sent
        # Test that three messages has been sent: email and text for master user
        #  and email for dealer
        #for email in mail.outbox:
        #    print email.subject, email.body
        self.assertEqual(len(mail.outbox), 3)


class AlertsMotionInRoomTestCase(WebTest):
    """
    Tests Motion in room calculations
    """
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script

        run_initialize_script()
        run_initialize_dicts_script()

        self.bluusite1 = G(BluuSite, first_name='Jan', last_name='Kowalski')
        self.room1 = G(Room, name="room1", bluusite=self.bluusite1)

        # USERS
        self.user1 = G(BluuUser, username='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)

        # DEVICES AND ALERTS
        self.motion_type = DeviceType.objects.get(name=DeviceType.MOTION)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         room=self.room1, device_type=self.motion_type)

        self.device2 = G(Device, serial='serial2', bluusite=self.bluusite1,
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

    def testMotionInRoomCalculationGaps(self):
        """
        Tests motion in room - long delays between statuses, so only gaps should
        be considered
        """
        # Add some statuses
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T20:00:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T23:30:09",
                              action=True)
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T23:40:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T06:00:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T12:00:09",
                              action=True)

        #with mock_now(datetime.datetime(2013, 03, 07, 23, 0, 9)):
        with patch('alerts.models.datetime') as mock_now:
            mock_now.now.return_value = datetime.datetime(2013, 03, 07, 23, 0,
                                                          9)
            till = datetime.datetime.strptime("2013-03-07T23:00:09",
                                              "%Y-%m-%dT%H:%M:%S")
            #mock_now.side_effect = lambda *args, **kw: datetime(*args, **kw)
            res = self.room1.get_motion_activity_time(till, 24 * 60)
            self.assertEquals(res, datetime.timedelta(minutes=20))

    def testMotionInRoomCalculationOverlaps(self):
        """
        Tests motion in room - some statues overlap other
        """
        # Add some statuses
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T20:00:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T23:30:09",
                              action=True)
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T23:34:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T06:00:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T06:04:09",
                              action=True)

        #with mock_now(datetime.datetime(2013, 03, 07, 23, 0, 9)):
        with patch('alerts.models.datetime') as mock_now:
            mock_now.now.return_value = datetime.datetime(2013, 03, 07, 23, 0,
                                                          9)
            till = datetime.datetime.strptime("2013-03-07T23:00:09",
                                              "%Y-%m-%dT%H:%M:%S")
            #mock_now.side_effect = lambda *args, **kw: datetime(*args, **kw)
            res = self.room1.get_motion_activity_time(till, 24 * 60)
            self.assertEquals(res, datetime.timedelta(minutes=18))

    def testMotionInRoomCalculationEntryMotion(self):
        """
        Tests motion in room - entry status is active and should be added to
        calculated time
        """
        # Add some statuses
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T22:58:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T23:30:09",
                              action=True)
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T23:34:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T06:00:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T06:04:09",
                              action=True)

        #with mock_now(datetime.datetime(2013, 03, 07, 23, 0, 9)):
        with patch('alerts.models.datetime') as mock_now:
            mock_now.now.return_value = datetime.datetime(2013, 03, 07, 23, 0,
                                                          9)
            till = datetime.datetime.strptime("2013-03-07T23:00:09",
                                              "%Y-%m-%dT%H:%M:%S")
            #mock_now.side_effect = lambda *args, **kw: datetime(*args, **kw)
            res = self.room1.get_motion_activity_time(till, 24 * 60)
            self.assertEquals(res, datetime.timedelta(minutes=21))

    def testMotionInRoomCalculationExitMotion(self):
        """
        Tests motion in room - exit status is active and should be added to
        calculated time not as timegap
        """
        # Add some statuses
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T22:58:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T23:30:09",
                              action=True)
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T23:34:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T06:00:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T22:57:09",
                              action=True)

        #with mock_now(datetime.datetime(2013, 03, 07, 23, 0, 9)):
        with patch('alerts.models.datetime') as mock_now:
            mock_now.now.return_value = datetime.datetime(2013, 03, 07, 23, 0,
                                                          9)
            till = datetime.datetime.strptime("2013-03-07T23:00:09",
                                              "%Y-%m-%dT%H:%M:%S")
            #mock_now.side_effect = lambda *args, **kw: datetime(*args, **kw)
            res = self.room1.get_motion_activity_time(till, 24 * 60)
            self.assertEquals(res, datetime.timedelta(minutes=19))


class AlertsMIRGTTestCase(WebTest):
    """
    Tests Motion In Room Greater Than
    """
    csrf_checks = False

    def setUp(self):
        from scripts.initialize_roles import run as run_initialize_script
        from scripts.initialize_dicts import run as run_initialize_dicts_script

        run_initialize_script()
        run_initialize_dicts_script()

        self.bluusite1 = G(BluuSite, first_name='Jan', last_name='Kowalski')
        self.room1 = G(Room, name="room1", bluusite=self.bluusite1)

        # USERS
        self.user1 = G(BluuUser, username='test1')
        self.user1.assign_group(group=Group.objects.get(name='User'),
                                obj=self.bluusite1)

        # DEVICES AND ALERTS
        self.motion_type = DeviceType.objects.get(name=DeviceType.MOTION)
        self.device1 = G(Device, serial='serial', bluusite=self.bluusite1,
                         room=self.room1, device_type=self.motion_type)

        self.device2 = G(Device, serial='serial2', bluusite=self.bluusite1,
                         room=self.room1, device_type=self.motion_type)

        self.alert = Alert.objects.get(
            alert_type=Alert.MOTION_IN_ROOM_GREATER_THAN)

        self.alert_less = Alert.objects.get(
            alert_type=Alert.MOTION_IN_ROOM_LESS_THAN)



        self.uar = UserAlertRoom.objects.create(alert=self.alert,
                                                room=self.room1,
                                                user=self.user1,
                                                duration=10,
                                                unit=Alert.MINUTES,
                                                email_notification=True,
                                                text_notification=True
        )

        self.uar = UserAlertRoom.objects.create(alert=self.alert_less,
                                                room=self.room1,
                                                user=self.user1,
                                                duration=10,
                                                unit=Alert.MINUTES,
                                                email_notification=True,
                                                text_notification=True
        )


    def testMotionActivityGTCheckTriggered(self):
        """
        Tests if motion activity alert are triggered
        when motion in room - is gt
        """
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T20:00:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T23:30:09",
                              action=True)
        Status.objects.create(device=self.device1,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-06T23:40:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T06:00:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T12:00:09",
                              action=True)

        with patch('alerts.tasks.datetime') as mock_now:
            mock_now.now.return_value = datetime.datetime(2013, 03, 07, 23, 0,
                                                          9)
            alert_trigger_motion_in_room_checks.delay()
            self.assertEqual(len(mail.outbox), 2)

    def testMotionActivityLTCheckTriggered(self):
        """
        Tests if motion activity alert are triggered
        when motion in room - is gt
        """
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T06:00:09",
                              action=True)
        Status.objects.create(device=self.device2,
                              bluusite=self.bluusite1,
                              device_type=self.motion_type,
                              room=self.device1.room,
                              data='123',
                              signal='1',
                              timestamp="2013-03-07T06:02:09",
                              action=True)

        with patch('alerts.tasks.datetime') as mock_now:
            mock_now.now.return_value = datetime.datetime(2013, 03, 07, 23, 0,
                                                          9)
            alert_trigger_motion_in_room_checks.delay()
            self.assertEqual(len(mail.outbox), 2)

