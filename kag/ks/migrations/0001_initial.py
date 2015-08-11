# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0003_auto_20150617_1440'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('entity_instance', models.ForeignKey(to='entity.EntityInstance')),
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
                ('name', models.CharField(max_length=150L)),
                ('description', models.CharField(max_length=2000L, null=True, blank=True)),
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
                ('event', models.ForeignKey(to='ks.Event')),
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
                ('URI_to_updates', models.CharField(max_length=200L)),
                ('processed', models.BooleanField(default=False)),
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
                ('URI', models.CharField(max_length=200L)),
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
                ('root_URI', models.CharField(max_length=200L)),
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
                ('root_instance_uri', models.CharField(max_length=2000L)),
                ('remote_url', models.CharField(max_length=200L)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='notification',
            name='subscriber',
            field=models.ForeignKey(to='ks.Subscriber'),
        ),
        migrations.AddField(
            model_name='event',
            name='event_type',
            field=models.ForeignKey(to='ks.EventType'),
        ),
    ]
