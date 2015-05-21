# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userauthorization', '0001_initial'),
        ('entity', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflowtransition',
            name='user',
            field=models.ForeignKey(blank=True, to='userauthorization.KUser', null=True),
        ),
    ]
