# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0001_initial'),
        ('entity', '0003_auto_20150521_0719'),
    ]

    operations = [
        migrations.AddField(
            model_name='attributetype',
            name='widgets',
            field=models.ManyToManyField(to='application.Widget', blank=True),
        ),
    ]
