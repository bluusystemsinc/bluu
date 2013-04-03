# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Alert'
        db.create_table(u'alerts_alert', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alert_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'alerts', ['Alert'])

        # Adding M2M table for field device_types on 'Alert'
        db.create_table(u'alerts_alert_device_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('alert', models.ForeignKey(orm[u'alerts.alert'], null=False)),
            ('devicetype', models.ForeignKey(orm[u'devices.devicetype'], null=False))
        ))
        db.create_unique(u'alerts_alert_device_types', ['alert_id', 'devicetype_id'])

        # Adding model 'UserAlert'
        db.create_table(u'alerts_useralert', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.BluuUser'])),
            ('alert', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['alerts.Alert'])),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('email_notification', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('text_notification', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'alerts', ['UserAlert'])


    def backwards(self, orm):
        # Deleting model 'Alert'
        db.delete_table(u'alerts_alert')

        # Removing M2M table for field device_types on 'Alert'
        db.delete_table('alerts_alert_device_types')

        # Deleting model 'UserAlert'
        db.delete_table(u'alerts_useralert')


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
        u'alerts.useralert': {
            'Meta': {'object_name': 'UserAlert'},
            'alert': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['alerts.Alert']"}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'email_notification': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text_notification': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'devices.devicetype': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'DeviceType'},
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['alerts']