# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forwards_func(apps, schema_editor):
    Organization = apps.get_model("entity", "Organization")
    KnowledgeServer = apps.get_model("entity", "KnowledgeServer")
    
    db_alias = schema_editor.connection.alias

    orgs = Organization.objects.using(db_alias).bulk_create([
        Organization(pk=1, name="Ministero degli Interni", URIInstance="http://fakeinterniitks.thekoa.org/entity/Organization/1", description=""),
    ])
    fake_interni_it_org = orgs[0]
    
    KSs = KnowledgeServer.objects.using(db_alias).bulk_create([
        KnowledgeServer(pk=2, name="Fake interni.it KS", uri="http://fakeinterniitks.thekoa.org", URIInstance="http://rootks.thekoa.org/entity/KnowledgeServer/2", description="Fake interni.it KS", organization=fake_interni_it_org, this_ks=True),
    ])
    fake_interni_it_org_ks = KSs[0]
    



class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0003_auto_20150617_1440'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

