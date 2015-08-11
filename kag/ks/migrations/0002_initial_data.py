# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from ks.models import EventType
from entity.models import SimpleEntity

def forwards_func(apps, schema_editor):
    
    db_alias = schema_editor.connection.alias
    
    se = SimpleEntity()
    se=SimpleEntity();se.name="EventType";se.module="ks";se.save(using=db_alias)
    
    et = EventType()
    et.name = "New version"
    et.save(using=db_alias)


class Migration(migrations.Migration):

    dependencies = [
        ('ks', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

