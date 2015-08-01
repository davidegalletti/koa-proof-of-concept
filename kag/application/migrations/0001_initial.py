# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('name', models.CharField(max_length=255L, blank=True)),
                ('description', models.TextField(blank=True)),
                ('workflows', models.ManyToManyField(to='entity.Workflow')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AttributeInAMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('attribute', models.ForeignKey(to='entity.Attribute')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Method',
            fields=[
                ('workflowmethod_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.WorkflowMethod')),
                ('name', models.CharField(max_length=255L, blank=True)),
                ('description', models.TextField(blank=True)),
                ('create_instance', models.BooleanField(default=False)),
                ('script_precondition', models.TextField(blank=True)),
                ('script_postcondition', models.TextField(blank=True)),
                ('script_premethod', models.TextField(blank=True)),
                ('script_postmethod', models.TextField(blank=True)),
                ('attributes', models.ManyToManyField(related_name='container_method', to='application.AttributeInAMethod')),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.workflowmethod',),
        ),
        migrations.CreateModel(
            name='Widget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('widgetname', models.CharField(max_length=255L, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='attributeinamethod',
            name='implementation_method',
            field=models.ForeignKey(blank=True, to='application.Method', null=True),
        ),
        migrations.AddField(
            model_name='attributeinamethod',
            name='workflow',
            field=models.ForeignKey(blank=True, to='entity.Workflow', null=True),
        ),
    ]
