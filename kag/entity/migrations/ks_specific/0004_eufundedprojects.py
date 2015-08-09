# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from entity.models import Organization, KnowledgeServer

def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    test_eu_projects_org = Organization();test_eu_projects_org.name="A test Organization hosting EU funded projects information";test_eu_projects_org.website='http://eu_projects_org.example.com';test_eu_projects_org.description="This is just a test Organization.";test_eu_projects_org.save(using=db_alias)
    
    root_ks = KnowledgeServer.this_knowledge_server()
    root_ks.this_ks = False
    root_ks.save(using=db_alias)

    test_eu_projects_org_ks = KnowledgeServer(name="A test Open Knowledge Server using some data from cordis.europa.eu.", scheme="http", netloc="eufundedprojects.thekoa.org", description="WARNING: THIS IS NOT AFFILIATED WITH cordis.europa.eu. IT IS JUST A TEST USING SOME cordis.europa.eu DATA.", organization=test_eu_projects_org, this_ks=True)
    test_eu_projects_org_ks.save(using=db_alias)
    



class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0003_auto_20150617_1440'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

