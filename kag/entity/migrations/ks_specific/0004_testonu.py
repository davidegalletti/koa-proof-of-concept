# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from entity.models import Organization, KnowledgeServer

def forwards_func(apps, schema_editor):
    test_onu_org = Organization();test_onu_org.name="United Nations";test_onu_org.website='http://www.un.org';test_onu_org.description="Test United Nations";test_onu_org.save()
    
    root_ks = KnowledgeServer.objects.get(pk=1)
    root_ks.this_ks = False
    root_ks.save()

    test_onu_org_ks = KnowledgeServer(name="Test ONU Knowledge Server", scheme="http", netloc="testonuks.thekoa.org", description="Test ONU Knowledge Server", organization=test_onu_org, this_ks=True)
    test_onu_org_ks.save()
    



class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0003_auto_20150617_1440'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

