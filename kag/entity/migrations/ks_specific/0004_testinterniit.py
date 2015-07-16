# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forwards_func(apps, schema_editor):
    Organization = apps.get_model("entity", "Organization")
    KnowledgeServer = apps.get_model("entity", "KnowledgeServer")
    
    db_alias = schema_editor.connection.alias

#         Organization(pk=2, name="Ministero degli Interni", URIInstance="http://testinterniitks.thekoa.org/entity/Organization/2", description="Test Ministero degli Interni"),
    orgs = Organization.objects.using(db_alias).bulk_create([
        Organization(name="Ministero degli Interni", description="Test Ministero degli Interni"),
    ])
    test_interni_it_org = orgs[0]

    root_ks = KnowledgeServer.objects.get(pk=1)
    root_ks.this_ks = False
    root_ks.save()
#         KnowledgeServer(pk=2, name="Test interni.it KS", scheme="http", netloc="testinterniitks.thekoa.org", URIInstance="http://testinterniitks.thekoa.org/entity/KnowledgeServer/2", description="Test interni.it KS", organization=test_interni_it_org, this_ks=True),
    KSs = KnowledgeServer.objects.using(db_alias).bulk_create([
        KnowledgeServer(name="Test interni.it KS", scheme="http", netloc="testinterniitks.thekoa.org", description="Test interni.it KS", organization=test_interni_it_org, this_ks=True),
    ])
    test_interni_it_org_ks = KSs[0]


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0003_auto_20150617_1440'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

