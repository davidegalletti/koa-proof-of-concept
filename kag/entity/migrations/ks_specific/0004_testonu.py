# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forwards_func(apps, schema_editor):
    Organization = apps.get_model("entity", "Organization")
    KnowledgeServer = apps.get_model("entity", "KnowledgeServer")
    
    db_alias = schema_editor.connection.alias

    orgs = Organization.objects.using(db_alias).bulk_create([
       Organization(name="United Nations", description="Test United Nations", website='http://testonuks.theKOA.org'),
    ])
    test_onu_org = orgs[0]

    root_ks = KnowledgeServer.objects.get(pk=1)
    root_ks.this_ks = False
    root_ks.save()
    
    KSs = KnowledgeServer.objects.using(db_alias).bulk_create([
        KnowledgeServer(name="Test ONU KS", scheme="http", netloc="testonuks.thekoa.org", description="Test ONU KS", organization=test_onu_org, this_ks=True),
    ])
    test_onu_org_ks = KSs[0]
    



class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0003_auto_20150617_1440'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

