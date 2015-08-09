# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('entity_instance_uri', models.CharField(max_length=2000L)),
                ('root_instance_uri', models.CharField(max_length=2000L)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EventType',
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
            name='Notification',
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
            name='NotificationReceived',
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
            name='Subscriber',
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
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('root_instance_uri', models.CharField(max_length=2000L)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='event',
            name='event_type',
            field=models.ForeignKey(to='ks.EventType'),
        ),
    ]
