# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0004_attributetype_widgets'),
    ]

    operations = [
        migrations.AddField(
            model_name='entityinstance',
            name='version_description',
            field=models.CharField(max_length=2000L, null=True, blank=True),
        ),
    ]
