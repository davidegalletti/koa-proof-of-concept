# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias



class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0004_common_to_other_ks'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

