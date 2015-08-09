# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('URIInstance', models.CharField(max_length=2000L)),
                ('URI_imported_instance', models.CharField(max_length=2000L)),
                ('URI_previous_version', models.CharField(max_length=2000L, null=True, blank=True)),
                ('name', models.CharField(max_length=200L)),
                ('short_name', models.CharField(max_length=50L)),
                ('human_readable', models.TextField(null=True, blank=True)),
                ('legalcode', models.TextField(default=b'')),
                ('adaptation_shared', models.NullBooleanField()),
                ('attribution', models.NullBooleanField()),
                ('share_alike', models.NullBooleanField()),
                ('commercial_use', models.NullBooleanField()),
                ('url_info', models.CharField(max_length=160L, null=True, blank=True)),
                ('reccomended_by_opendefinition', models.NullBooleanField()),
                ('conformant_for_opendefinition', models.NullBooleanField()),
                ('image', models.CharField(max_length=160L, null=True, blank=True)),
                ('image_small', models.CharField(max_length=160L, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
