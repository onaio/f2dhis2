# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'FormhubService.name'
        db.alter_column('dhis_formhub_servicet', 'name', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'DataElement.name'
        db.alter_column('dhis_data_element', 'name', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'OrganizationUnit.name'
        db.alter_column('dhis_orgunit', 'name', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'DataSet.name'
        db.alter_column('dhis_data_set', 'name', self.gf('django.db.models.fields.CharField')(max_length=100))

    def backwards(self, orm):

        # Changing field 'FormhubService.name'
        db.alter_column('dhis_formhub_servicet', 'name', self.gf('django.db.models.fields.CharField')(max_length=32))

        # Changing field 'DataElement.name'
        db.alter_column('dhis_data_element', 'name', self.gf('django.db.models.fields.CharField')(max_length=32))

        # Changing field 'OrganizationUnit.name'
        db.alter_column('dhis_orgunit', 'name', self.gf('django.db.models.fields.CharField')(max_length=32))

        # Changing field 'DataSet.name'
        db.alter_column('dhis_data_set', 'name', self.gf('django.db.models.fields.CharField')(max_length=32))

    models = {
        'main.dataelement': {
            'Meta': {'unique_together': "(('data_set', 'data_element_id'),)", 'object_name': 'DataElement', 'db_table': "'dhis_data_element'"},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data_element_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'data_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.DataSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.dataqueue': {
            'Meta': {'object_name': 'DataQueue', 'db_table': "'dhis_data_queue'"},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'processed_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.FormhubService']"})
        },
        'main.dataset': {
            'Meta': {'object_name': 'DataSet', 'db_table': "'dhis_data_set'"},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data_set_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'frequency': ('django.db.models.fields.PositiveIntegerField', [], {'default': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.datavalueset': {
            'Meta': {'object_name': 'DataValueSet', 'db_table': "'dhis_data_value_set'"},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.DataSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'organization_unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.OrganizationUnit']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.FormhubService']"})
        },
        'main.formdataelement': {
            'Meta': {'unique_together': "(('data_value_set', 'data_element'),)", 'object_name': 'FormDataElement', 'db_table': "'dhis_form_data_element'"},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data_element': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.DataElement']"}),
            'data_value_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.DataValueSet']"}),
            'form_field': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'main.formhubservice': {
            'Meta': {'unique_together': "(('id_string', 'url'),)", 'object_name': 'FormhubService', 'db_table': "'dhis_formhub_servicet'"},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_string': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'main.organizationunit': {
            'Meta': {'object_name': 'OrganizationUnit', 'db_table': "'dhis_orgunit'"},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'org_unit_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        }
    }

    complete_apps = ['main']