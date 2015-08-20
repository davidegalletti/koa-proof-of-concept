# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('license', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('name', models.CharField(max_length=255L, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AttributeType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('name', models.CharField(max_length=255L, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DBConnection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('connection_string', models.CharField(max_length=255L)),
                ('name', models.CharField(max_length=100L, null=True, blank=True)),
                ('description', models.CharField(max_length=2000L, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='EntityStructure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('namespace', models.CharField(max_length=500L, blank=True)),
                ('name', models.CharField(max_length=200L)),
                ('description', models.CharField(max_length=2000L)),
                ('is_shallow', models.BooleanField(default=False)),
                ('is_a_view', models.BooleanField(default=False)),
                ('multiple_releases', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EntityInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('filter_text', models.CharField(max_length=200L, null=True, blank=True)),
                ('version_major', models.IntegerField(blank=True, null=True)),
                ('version_minor', models.IntegerField(blank=True, null=True)),
                ('version_patch', models.IntegerField(blank=True, null=True)),
                ('version_description', models.CharField(max_length=2000L, default=b'')),
                ('version_date', models.DateTimeField(auto_now_add=True)),
                ('dataset_date', models.DateTimeField(auto_now_add=True)),
                ('version_released', models.BooleanField(default=False)),
                ('entry_point_instance_id', models.IntegerField(null=True, blank=True)),
                ('description', models.CharField(max_length=2000L, default=b'')),
                ('license', models.ForeignKey(null=True, to='license.License', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EntityStructureNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('attribute', models.CharField(max_length=255L, blank=True)),
                ('external_reference', models.BooleanField(default=False, db_column=b'externalReference')),
                ('is_many', models.BooleanField(default=False, db_column=b'isMany')),
                ('child_nodes', models.ManyToManyField(related_name='parent_entity_structure_node', to='entity.EntityStructureNode', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('name', models.CharField(max_length=500L, blank=True)),
                ('description', models.CharField(max_length=2000L, blank=True)),
                ('website', models.CharField(max_length=500L, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KnowledgeServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('name', models.CharField(max_length=500L, blank=True)),
                ('description', models.CharField(max_length=2000L, blank=True)),
                ('netloc', models.CharField(max_length=200L)),
                ('scheme', models.CharField(max_length=50L)),
                ('organization', models.ForeignKey(to='entity.Organization')),
                ('this_ks', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SimpleEntity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('name', models.CharField(max_length=100L)),
                ('module', models.CharField(max_length=100L)),
                ('description', models.CharField(max_length=2000L, default=b'')),
                ('table_name', models.CharField(max_length=255L, db_column=b'tableName', default=b'')),
                ('id_field', models.CharField(max_length=255L, db_column=b'idField', default=b'id')),
                ('name_field', models.CharField(max_length=255L, db_column=b'nameField', default=b'name')),
                ('description_field', models.CharField(max_length=255L, db_column=b'descriptionField', default=b'description')),
                ('connection', models.ForeignKey(blank=True, to='entity.DBConnection', null=True)),
                ('entity_structure', models.ForeignKey(blank=True, to='entity.EntityStructure', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('docfile', models.FileField(upload_to=b'documents/%Y/%m/%d')),
            ],
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('name', models.CharField(max_length=100L)),
                ('description', models.CharField(max_length=2000L, blank=True)),
                ('entity_structure', models.ForeignKey(blank=True, to='entity.EntityStructure', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorkflowMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorkflowStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('name', models.CharField(max_length=100L)),
                ('description', models.CharField(max_length=2000L, blank=True)),
                ('workflow', models.ForeignKey(blank=True, to='entity.Workflow', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorkflowTransition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('notes', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('instance', models.ForeignKey(to='entity.EntityInstance')),
                ('status_from', models.ForeignKey(related_name='+', to='entity.WorkflowStatus')),
                ('workflow_method', models.ForeignKey(to='entity.WorkflowMethod')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('type', models.CharField(default=b'New version', max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('processed', models.BooleanField(default=False)),
                ('entity_instance', models.ForeignKey(to='entity.EntityInstance')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('sent', models.BooleanField(default=False)),
                ('remote_url', models.CharField(max_length=200L)),
                ('event', models.ForeignKey(to='entity.Event')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NotificationReceived',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('URL_dataset', models.CharField(max_length=200L)),
                ('URL_structure', models.CharField(max_length=200L)),
                ('processed', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubscriptionToOther',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('URI', models.CharField(max_length=200L)),
                ('root_URIInstance', models.CharField(max_length=200L)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubscriptionToThis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('root_URIInstance', models.CharField(max_length=2000L)),
                ('remote_url', models.CharField(max_length=200L)),
                ('first_notification_prepared', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='workflowmethod',
            name='final_status',
            field=models.ForeignKey(related_name='+', to='entity.WorkflowStatus'),
        ),
        migrations.AddField(
            model_name='workflowmethod',
            name='initial_statuses',
            field=models.ManyToManyField(related_name='+', to='entity.WorkflowStatus', blank=True),
        ),
        migrations.AddField(
            model_name='workflowmethod',
            name='workflow',
            field=models.ForeignKey(to='entity.Workflow'),
        ),
        migrations.AddField(
            model_name='entitystructurenode',
            name='simple_entity',
            field=models.ForeignKey(to='entity.SimpleEntity'),
        ),
        migrations.AddField(
            model_name='entityinstance',
            name='entity_structure',
            field=models.ForeignKey(to='entity.EntityStructure'),
        ),
        migrations.AddField(
            model_name='entityinstance',
            name='owner_knowledge_server',
            field=models.ForeignKey(to='entity.KnowledgeServer'),
        ),
        migrations.AddField(
            model_name='entityinstance',
            name='root',
            field=models.ForeignKey(related_name='versions', blank=True, to='entity.EntityInstance', null=True),
        ),
        migrations.AddField(
            model_name='entityinstance',
            name='filter_entity_instance',
            field=models.ForeignKey(blank=True, to='entity.EntityInstance', null=True),
        ),
        migrations.AddField(
            model_name='entitystructure',
            name='entry_point',
            field=models.ForeignKey(to='entity.EntityStructureNode'),
        ),
        migrations.AddField(
            model_name='attribute',
            name='simple_entity',
            field=models.ForeignKey(blank=True, to='entity.SimpleEntity', null=True),
        ),
        migrations.AddField(
            model_name='attribute',
            name='type',
            field=models.ForeignKey(to='entity.AttributeType'),
        ),
    ]
