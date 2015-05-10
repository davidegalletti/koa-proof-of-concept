# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0001_initial'),
        ('application', '0002_auto_20150508_1656'),
    ]

    operations = [
        migrations.AddField(
            model_name='attributetype',
            name='widgets',
            field=models.ManyToManyField(to='application.Widget', blank=True),
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
