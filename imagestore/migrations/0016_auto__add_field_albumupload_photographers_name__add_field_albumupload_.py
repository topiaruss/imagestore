# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'AlbumUpload.photographers_name'
        db.add_column(u'imagestore_albumupload', 'photographers_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'AlbumUpload.event_name'
        db.add_column(u'imagestore_albumupload', 'event_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'AlbumUpload.image_description'
        db.add_column(u'imagestore_albumupload', 'image_description',
                      self.gf('django.db.models.fields.TextField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'AlbumUpload.photo_date'
        db.add_column(u'imagestore_albumupload', 'photo_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)


        # Changing field 'AlbumUpload.tags'
        db.alter_column(u'imagestore_albumupload', 'tags', self.gf('tagging_autocomplete.models.TagAutocompleteField')())
        # Adding field 'Image.photographers_name'
        db.add_column(u'imagestore_image', 'photographers_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Image.event_name'
        db.add_column(u'imagestore_image', 'event_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'Image.image_description'
        db.add_column(u'imagestore_image', 'image_description',
                      self.gf('django.db.models.fields.TextField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'Image.photo_date'
        db.add_column(u'imagestore_image', 'photo_date',
                      self.gf('django.db.models.fields.DateField')(default=None, blank=True),
                      keep_default=False)


        # Changing field 'Image.tags'
        db.alter_column(u'imagestore_image', 'tags', self.gf('tagging_autocomplete.models.TagAutocompleteField')())

    def backwards(self, orm):
        # Deleting field 'AlbumUpload.photographers_name'
        db.delete_column(u'imagestore_albumupload', 'photographers_name')

        # Deleting field 'AlbumUpload.event_name'
        db.delete_column(u'imagestore_albumupload', 'event_name')

        # Deleting field 'AlbumUpload.image_description'
        db.delete_column(u'imagestore_albumupload', 'image_description')

        # Deleting field 'AlbumUpload.photo_date'
        db.delete_column(u'imagestore_albumupload', 'photo_date')


        # Changing field 'AlbumUpload.tags'
        db.alter_column(u'imagestore_albumupload', 'tags', self.gf('django.db.models.fields.CharField')(max_length=255))
        # Deleting field 'Image.photographers_name'
        db.delete_column(u'imagestore_image', 'photographers_name')

        # Deleting field 'Image.event_name'
        db.delete_column(u'imagestore_image', 'event_name')

        # Deleting field 'Image.image_description'
        db.delete_column(u'imagestore_image', 'image_description')

        # Deleting field 'Image.photo_date'
        db.delete_column(u'imagestore_image', 'photo_date')


        # Changing field 'Image.tags'
        db.alter_column(u'imagestore_image', 'tags', self.gf('tagging.fields.TagField')())

    models = {
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
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'imagestore.album': {
            'Meta': {'ordering': "('order', 'created', 'name')", 'object_name': 'Album'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'head': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'head_of'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['imagestore.Image']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'albums'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        'imagestore.albumupload': {
            'Meta': {'object_name': 'AlbumUpload'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['imagestore.Album']", 'null': 'True', 'blank': 'True'}),
            'event_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_description': ('django.db.models.fields.TextField', [], {'max_length': '100', 'blank': 'True'}),
            'new_album_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'photo_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'photographers_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'tags': ('tagging_autocomplete.models.TagAutocompleteField', [], {}),
            'zip_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'imagestore.image': {
            'Meta': {'ordering': "('order', 'id')", 'object_name': 'Image'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'images'", 'null': 'True', 'to': "orm['imagestore.Album']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'event_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'image_description': ('django.db.models.fields.TextField', [], {'max_length': '100', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'photo_date': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'photographers_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tags': ('tagging_autocomplete.models.TagAutocompleteField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'images'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'video_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200'})
        }
    }

    complete_apps = ['imagestore']