# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from entity.models import Organization, KnowledgeServer, EntityInstance, EntityStructure, SimpleEntity, EntityStructureNode
from license.models import License

def forwards_func(apps, schema_editor):
    this_ks = KnowledgeServer.this_knowledge_server('default')
    seLicense=SimpleEntity();seLicense.name="License";seLicense.module="license";seLicense.save(using='default')
    m_seLicense=seLicense
    id_on_default_db = seLicense.id
    m_seLicense.id=None
    m_seLicense.save(using='ksm')
    # The following line is needed to make sure that seLicense._state.db is 'default'; 
    # before the following line it would be 'ksm'
    seLicense = SimpleEntity.objects.using('default').get(pk=id_on_default_db)
    
    en1=EntityStructureNode();en1.simple_entity=seLicense;en1.save(using='default')
    esLicense=EntityStructure();esLicense.multiple_releases=True;esLicense.is_shallow = True;
    esLicense.entry_point=en1;esLicense.name="License";esLicense.description="License information";esLicense.namespace="license";
    esLicense.save(using='default')
    m_es = EntityStructure.objects.using('ksm').get(name=EntityStructure.entity_structure_entity_structure_name)
    es = EntityStructure.objects.using('default').get(URIInstance=m_es.URIInstance)
    ei = EntityInstance(description='-License- data set structure',owner_knowledge_server=this_ks,entity_structure=es, entry_point_instance_id=esLicense.id, version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using='default');ei.root_id=ei.id;ei.save(using='default')
    ei.set_released() #here materialization happens
    
    
    seLicense.entity_structure = esLicense; seLicense.save(using='default')
    
    # EntityStructure di tipo view per la lista di licenze;  
    en1=EntityStructureNode();en1.simple_entity=seLicense;en1.save(using='default')
    esLicenseList=EntityStructure();esLicenseList.is_a_view = True;
    esLicenseList.entry_point=en1;esLicenseList.name="List of licenses";esLicenseList.description="List of all released licenses";esLicenseList.namespace="license";
    esLicenseList.save(using='default')
    # EntityInstance of the above EntityStructure
    ei = EntityInstance(description='-List of licenses- data set structure',owner_knowledge_server=this_ks,entity_structure=es, entry_point_instance_id=esLicenseList.id, version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using='default');ei.root_id=ei.id;ei.save(using='default')
    ei.set_released() #here materialization happens


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0003_auto_20150617_1440'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

