# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0003_auto_20150508_2234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflow',
            name='entity',
            field=models.ForeignKey(blank=True, to='entity.Entity', null=True),
        ),
    ]
