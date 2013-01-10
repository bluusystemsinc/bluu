# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Company'
        db.create_table(u'accounts_company', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=7, blank=True)),
            ('country', self.gf('accounts.countries.CountryField')(default=u'US', max_length=2, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('contact_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'accounts', ['Company'])

        # Adding model 'Site'
        db.create_table(u'accounts_site', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=7, blank=True)),
            ('country', self.gf('accounts.countries.CountryField')(default=u'US', max_length=2, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('middle_initial', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
        ))
        db.send_create_signal(u'accounts', ['Site'])

        # Adding model 'BluuUser'
        db.create_table(u'accounts_bluuuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cell', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('cell_text_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
        ))
        db.send_create_signal(u'accounts', ['BluuUser'])

        # Adding M2M table for field groups on 'BluuUser'
        db.create_table(u'accounts_bluuuser_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('bluuuser', models.ForeignKey(orm[u'accounts.bluuuser'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(u'accounts_bluuuser_groups', ['bluuuser_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'BluuUser'
        db.create_table(u'accounts_bluuuser_user_permissions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('bluuuser', models.ForeignKey(orm[u'accounts.bluuuser'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(u'accounts_bluuuser_user_permissions', ['bluuuser_id', 'permission_id'])

        # Adding M2M table for field company on 'BluuUser'
        db.create_table(u'accounts_bluuuser_company', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('bluuuser', models.ForeignKey(orm[u'accounts.bluuuser'], null=False)),
            ('company', models.ForeignKey(orm[u'accounts.company'], null=False))
        ))
        db.create_unique(u'accounts_bluuuser_company', ['bluuuser_id', 'company_id'])

        # Adding M2M table for field site on 'BluuUser'
        db.create_table(u'accounts_bluuuser_site', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('bluuuser', models.ForeignKey(orm[u'accounts.bluuuser'], null=False)),
            ('site', models.ForeignKey(orm[u'accounts.site'], null=False))
        ))
        db.create_unique(u'accounts_bluuuser_site', ['bluuuser_id', 'site_id'])


    def backwards(self, orm):
        # Deleting model 'Company'
        db.delete_table(u'accounts_company')

        # Deleting model 'Site'
        db.delete_table(u'accounts_site')

        # Deleting model 'BluuUser'
        db.delete_table(u'accounts_bluuuser')

        # Removing M2M table for field groups on 'BluuUser'
        db.delete_table('accounts_bluuuser_groups')

        # Removing M2M table for field user_permissions on 'BluuUser'
        db.delete_table('accounts_bluuuser_user_permissions')

        # Removing M2M table for field company on 'BluuUser'
        db.delete_table('accounts_bluuuser_company')

        # Removing M2M table for field site on 'BluuUser'
        db.delete_table('accounts_bluuuser_site')


    models = {
        u'accounts.bluuuser': {
            'Meta': {'object_name': 'BluuUser'},
            'cell': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'cell_text_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'company_bluuuser'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['accounts.Company']"}),
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
            'site': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'site_bluuuser'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['accounts.Site']"}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'accounts.company': {
            'Meta': {'object_name': 'Company'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'country': ('accounts.countries.CountryField', [], {'default': "u'US'", 'max_length': '2', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '7', 'blank': 'True'})
        },
        u'accounts.site': {
            'Meta': {'object_name': 'Site'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'country': ('accounts.countries.CountryField', [], {'default': "u'US'", 'max_length': '2', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'middle_initial': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '7', 'blank': 'True'})
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
        }
    }

    complete_apps = ['accounts']