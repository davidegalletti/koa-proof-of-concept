# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from entity.models import Organization, KnowledgeServer, DataSet, DataSetStructure

def forwards_func(apps, schema_editor):
    test_eu_projects_org = Organization();test_eu_projects_org.name = "A test Organization hosting EU funded projects information";test_eu_projects_org.website = 'http://eu_projects_org.example.com';test_eu_projects_org.description = "This is just a test Organization.";
    test_eu_projects_org.save(using='default')
    id_on_default_db = test_eu_projects_org.id
    test_eu_projects_org.id = None
    test_eu_projects_org.save(using='ksm')
    m_test_eu_projects_org = test_eu_projects_org
    test_eu_projects_org = Organization.objects.get(pk=id_on_default_db)
    
    root_ks = KnowledgeServer.this_knowledge_server('default')
    root_ks.this_ks = False
    root_ks.save()
    root_ks = KnowledgeServer.this_knowledge_server()
    root_ks.this_ks = False
    root_ks.save()
    
    m_test_eu_projects_org_ks = KnowledgeServer(name="A test Open Knowledge Server using some data from Cordis.", scheme="http", netloc="euks.thekoa.org", description="Please not that this site not affiliated with cordis.europa.eu.", organization=test_eu_projects_org, this_ks=True, html_home="", html_disclaimer="This web site is solely for test purposes. Feel free to contact us.")
    m_test_eu_projects_org_ks.save(using='ksm')
    test_eu_projects_org_ks = m_test_eu_projects_org_ks
    test_eu_projects_org_ks.id = None
    test_eu_projects_org_ks.URIInstance = ""
    test_eu_projects_org_ks.save(using='default')
    
    # m_test_eu_projects_org and test_eu_projects_org have the wrong URIInstance because they where created before their Knowledge Server
    # I fix this:
    m_test_eu_projects_org.URIInstance = ""
    m_test_eu_projects_org.save()
    test_eu_projects_org.URIInstance = ""
    test_eu_projects_org.save()
    
    m_es = DataSetStructure.objects.using('ksm').get(name=DataSetStructure.organization_dataset_structure_name)
    es = DataSetStructure.objects.get(URIInstance=m_es.URIInstance)
    ei = DataSet(owner_knowledge_server=test_eu_projects_org_ks, entry_point_instance_id=test_eu_projects_org.id, dataset_structure=es, description="A test Organization and their KSs", version_major=0, version_minor=1, version_patch=0)
    ei.save(using='default');ei.root_id = ei.id;ei.save(using='default')
    # let's materialize the ei; I cannot release it as I saved manually the ks in ksm (I cannot do otherwise as it 
    # is needed to generateURIInstance every time something is saved)
    ei.materialize(ei.shallow_dataset_structure().entry_point, processed_instances=[])
    



class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0004_common_to_other_ks'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

