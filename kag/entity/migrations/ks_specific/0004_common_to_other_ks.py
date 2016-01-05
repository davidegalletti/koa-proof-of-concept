# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from entity.models import Organization, KnowledgeServer, DataSet, EntityStructure, SimpleEntity, EntityStructureNode
from license.models import License

def forwards_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0003_auto_20150617_1440'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

