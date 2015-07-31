# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from entity.models import Organization, KnowledgeServer

def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    test_onu_org = Organization();test_onu_org.name="United Nations";test_onu_org.website='http://www.un.org';test_onu_org.description="Test United Nations";test_onu_org.save(using=db_alias)
    
    root_ks = KnowledgeServer.this_knowledge_server()
    root_ks.this_ks = False
    root_ks.save(using=db_alias)

    test_onu_org_ks = KnowledgeServer(name="Test ONU Knowledge Server", scheme="http", netloc="testonuks.thekoa.org", description="Test ONU Knowledge Server", organization=test_onu_org, this_ks=True)
    test_onu_org_ks.save(using=db_alias)
    



class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0003_auto_20150617_1440'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

