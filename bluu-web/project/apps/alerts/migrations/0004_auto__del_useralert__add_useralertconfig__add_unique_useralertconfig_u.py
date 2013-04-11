# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'UserAlert'
        db.delete_table(u'alerts_useralert')

        # Adding model 'UserAlertConfig'
        db.create_table(u'alerts_useralertconfig', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.BluuUser'])),
            ('alert', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alerts.Alert'])),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('email_notification', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('text_notification', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'alerts', ['UserAlertConfig'])

        # Adding unique constraint on 'UserAlertConfig', fields ['user', 'alert']
        db.create_unique(u'alerts_useralertconfig', ['user_id', 'alert_id'])

        # Adding model 'UserAlertDevice'
        db.create_table(u'alerts_useralertdevice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.BluuUser'])),
            ('alert', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alerts.Alert'])),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devices.Device'])),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('email_notification', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('text_notification', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'alerts', ['UserAlertDevice'])

        # Adding unique constraint on 'UserAlertDevice', fields ['user', 'device', 'alert']
        db.create_unique(u'alerts_useralertdevice', ['user_id', 'device_id', 'alert_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'UserAlertDevice', fields ['user', 'device', 'alert']
        db.delete_unique(u'alerts_useralertdevice', ['user_id', 'device_id', 'alert_id'])

        # Removing unique constraint on 'UserAlertConfig', fields ['user', 'alert']
        db.delete_unique(u'alerts_useralertconfig', ['user_id', 'alert_id'])

        # Adding model 'UserAlert'
        db.create_table(u'alerts_useralert', (
            ('email_notification', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.BluuUser'])),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devices.Device'])),
            ('text_notification', self.gf('django.db.models.fields.BooleanField')(default=False)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('alert', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alerts.Alert'])),
        ))
        db.send_create_signal(u'alerts', ['UserAlert'])

        # Deleting model 'UserAlertConfig'
        db.delete_table(u'alerts_useralertconfig')

        # Deleting model 'UserAlertDevice'
        db.delete_table(u'alerts_useralertdevice')


    models = {
        u'accounts.bluuuser': {
            'Meta': {'object_name': 'BluuUser'},
            'cell': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'cell_text_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'alerts.alert': {
            'Meta': {'object_name': 'Alert'},
            'alert_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'device_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['devices.DeviceType']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'alerts.useralertconfig': {
            'Meta': {'unique_together': "((u'user', u'alert'),)", 'object_name': 'UserAlertConfig'},
            'alert': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alerts.Alert']"}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'email_notification': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text_notification': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.BluuUser']"})
        },
        u'alerts.useralertdevice': {
            'Meta': {'unique_together': "((u'user', u'device', u'alert'),)", 'object_name': 'UserAlertDevice'},
            'alert': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alerts.Alert']"}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devices.Device']"}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'email_notification': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text_notification': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.BluuUser']"})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'bluusites.bluusite': {
            'Meta': {'object_name': 'BluuSite'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['companies.Company']", 'on_delete': 'models.PROTECT'}),
            'country': ('utils.countries.CountryField', [], {'default': "u'US'", 'max_length': '2'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'many_inhabitants': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'middle_initial': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None', 'unique_with': '()'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['accounts.BluuUser']", 'null': 'True', 'through': u"orm['bluusites.BluuSiteAccess']", 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '7'})
        },
        u'bluusites.bluusiteaccess': {
            'Meta': {'unique_together': "((u'site', u'user'), (u'site', u'email'))", 'object_name': 'BluuSiteAccess'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bluusites.BluuSite']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.BluuUser']", 'null': 'True', 'blank': 'True'})
        },
        u'bluusites.room': {
            'Meta': {'object_name': 'Room'},
            'bluusite': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bluusites.BluuSite']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'companies.company': {
            'Meta': {'object_name': 'Company'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '6'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'country': ('utils.countries.CountryField', [], {'default': "u'US'", 'max_length': '2', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'employees': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['accounts.BluuUser']", 'null': 'True', 'through': u"orm['companies.CompanyAccess']", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '7', 'blank': 'True'})
        },
        u'companies.companyaccess': {
            'Meta': {'unique_together': "((u'company', u'user'), (u'company', u'email'))", 'object_name': 'CompanyAccess'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['companies.Company']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.BluuUser']", 'null': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'devices.device': {
            'Meta': {'unique_together': "((u'bluusite', u'serial'),)", 'object_name': 'Device'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'bluusite': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bluusites.BluuSite']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'device_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devices.DeviceType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bluusites.Room']"}),
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "u'serial'"})
        },
        u'devices.devicetype': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'DeviceType'},
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'invitations.invitationkey': {
            'Meta': {'object_name': 'InvitationKey'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date_invited': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations_sent'", 'to': u"orm['accounts.BluuUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'registrant': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'invitations_used'", 'null': 'True', 'to': u"orm['accounts.BluuUser']"})
        }
    }

    complete_apps = ['alerts']