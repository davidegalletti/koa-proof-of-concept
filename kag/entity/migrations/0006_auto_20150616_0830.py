# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def forwards_func(apps, schema_editor):
    Organization = apps.get_model("entity", "Organization")
    SimpleEntity = apps.get_model("entity", "SimpleEntity")
    
    db_alias = schema_editor.connection.alias

    the_koa_org = Organization.objects.get(pk=1)

    SimpleEntity.objects.using(db_alias).bulk_create([
        SimpleEntity(id=16, name="EntityInstance", owner_organization=the_koa_org, namespace="entity", URIInstance="http://thekoa.org/KS/entity/SimpleEntity/16", name_in_this_namespace="EntityInstance", module="entity", description="", table_name="", id_field="id", name_field="", description_field="")
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0005_entityinstance_version_description'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]
