# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from entity.models import Organization, KnowledgeServer

def forwards_func(apps, schema_editor):
    test_interni_it_org = Organization();test_interni_it_org.name="Ministero degli Interni";test_interni_it_org.website='http://www.interno.gov.it';test_interni_it_org.description="Test Ministero degli Interni";test_interni_it_org.save()
    
    root_ks = KnowledgeServer.this_knowledge_server()
    root_ks.this_ks = False
    root_ks.save()

    test_interni_it_org_ks = KnowledgeServer(name="Test interno.gov.it Knowledge Server", scheme="http", netloc="testinterniitks.thekoa.org", description="Test interno.gov.it Knowledge Server", organization=test_interni_it_org, this_ks=True)
    test_interni_it_org_ks.save()



class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0003_auto_20150617_1440'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

