# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from entity.models import Organization, KnowledgeServer, DataSet, DataSetStructure, SimpleEntity, StructureNode
from license.models import License

def forwards_func(apps, schema_editor):
    test_license_org = Organization();test_license_org.name = "A test Organization hosting license information";test_license_org.website = 'http://license_org.example.com';test_license_org.description = "This is just a test Organization.";
    test_license_org.save(using='default')
    id_on_default_db = test_license_org.id
    test_license_org.id = None
    test_license_org.save(using='ksm')
    m_test_license_org = test_license_org
    test_license_org = Organization.objects.get(pk=id_on_default_db)
    
    root_ks = KnowledgeServer.this_knowledge_server('default')
    root_ks.this_ks = False
    root_ks.save()
    root_ks = KnowledgeServer.this_knowledge_server()
    root_ks.this_ks = False
    root_ks.save()
    
    m_test_license_org_ks = KnowledgeServer(name="A test Open Knowledge Server using some data from opendefinition.org.", scheme="http", netloc="licenses.thekoa.org", description="Please not that this site not affiliated with opendefinition.org. It is just a test some opendefinition.org data.", organization=test_license_org, this_ks=True, html_home="licenses html_home", html_disclaimer="This web site is solely for test purposes; information provided is taken from sources that make it available with opendefinition.org conformant licenses. If you think that part of this information should not be provided here or that any information is somehow misleading please contact us.")
    m_test_license_org_ks.save(using='ksm')
    test_license_org_ks = m_test_license_org_ks
    test_license_org_ks.id = None
    test_license_org_ks.URIInstance = ""
    test_license_org_ks.save(using='default')
    
    # m_test_license_org and test_license_org have the wrong URIInstance because they where created before their Knowledge Server
    # I fix this:
    m_test_license_org.URIInstance = ""
    m_test_license_org.save()
    test_license_org.URIInstance = ""
    test_license_org.save()
    
    
    
    
    # it was in 0004_common
    
    this_ks = KnowledgeServer.this_knowledge_server('default')
    seLicense = SimpleEntity.objects.using('default').get(name="License")
    
    en1 = StructureNode();en1.simple_entity = seLicense;en1.save(using='default')
    esLicense = DataSetStructure();esLicense.multiple_releases = True;esLicense.is_shallow = True;
    esLicense.entry_point = en1;esLicense.name = "License";esLicense.description = "License information";esLicense.namespace = "license";
    esLicense.save(using='default')
    m_es = DataSetStructure.objects.using('ksm').get(name=DataSetStructure.dataset_structure_name)
    es = DataSetStructure.objects.using('default').get(URIInstance=m_es.URIInstance)
    ei = DataSet(description='-License- data set structure', owner_knowledge_server=this_ks, dataset_structure=es, entry_point_instance_id=esLicense.id, version_major=0, version_minor=1, version_patch=0, version_description="", version_released=True)
    ei.save(using='default');ei.root_id = ei.id;ei.save(using='default')
    ei.set_released()  # here materialization happens
    
    seLicense.dataset_structure = esLicense; seLicense.save(using='default')
    
    # DataSetStructure di tipo view per la lista di licenze;  
    en1 = StructureNode();en1.simple_entity = seLicense;en1.save(using='default')
    esLicenseList = DataSetStructure();esLicenseList.is_a_view = True;
    esLicenseList.entry_point = en1;esLicenseList.name = "List of licenses";esLicenseList.description = "List of all released licenses";esLicenseList.namespace = "license";
    esLicenseList.save(using='default')
    # DataSet of the above DataSetStructure
    ei = DataSet(description='-List of licenses- data set structure', owner_knowledge_server=this_ks, dataset_structure=es, entry_point_instance_id=esLicenseList.id, version_major=0, version_minor=1, version_patch=0, version_description="", version_released=True)
    ei.save(using='default');ei.root_id = ei.id;ei.save(using='default')
    ei.set_released()  # here materialization happens
    # it was in 0004_common
    
    
    
    
    m_es = DataSetStructure.objects.using('ksm').get(name=DataSetStructure.organization_dataset_structure_name)
    es = DataSetStructure.objects.get(URIInstance=m_es.URIInstance)
    ei = DataSet(owner_knowledge_server=test_license_org_ks, entry_point_instance_id=test_license_org.id, dataset_structure=es, description="A test Organization and their KSs", version_major=0, version_minor=1, version_patch=0)
    ei.save(using='default');ei.root_id = ei.id;ei.save(using='default')
    # let's materialize the ei; I cannot release it as I saved manually the ks in ksm (I cannot do otherwise as it 
    # is needed to generateURIInstance every time something is saved)
    ei.materialize(ei.shallow_dataset_structure().entry_point, processed_instances=[])
    
    # temporarily created in 0004
    esLicense = DataSetStructure.objects.get(name="License") 
    
    ######## BEGIN LICENSES DATA
    
    # Against DRM 
    adrm = License()
    adrm.name = "Against DRM"
    adrm.short_name = ""
    adrm.attribution = True
    adrm.share_alike = True
    adrm.url_info = "http://opendefinition.org/licenses/against-drm"
    adrm.reccomended_by_opendefinition = False
    adrm.conformant_for_opendefinition = True
    adrm.legalcode = ''
    adrm.save(using='default')
    ei = DataSet(owner_knowledge_server=test_license_org_ks, dataset_structure=esLicense, entry_point_instance_id=adrm.id, version_major=2, version_minor=0, version_patch=0, version_description="", version_released=True)
    ei.save(using='default');ei.root_id = ei.id;ei.save(using='default')
    ei.set_released()  # here materialization happens

    # Creative Commons Attribution 1.0
    ccby10 = License()
    ccby10.name = "Creative Commons Attribution 1.0"
    ccby10.short_name = "CC-BY-1.0"
    ccby10.attribution = True
    ccby10.share_alike = False
    ccby10.url_info = "http://creativecommons.org/licenses/by/1.0"
    ccby10.reccomended_by_opendefinition = False
    ccby10.conformant_for_opendefinition = True
    ccby10.legalcode = ''
    ccby10.save(using='default')
    ei_ccby10 = DataSet(owner_knowledge_server=test_license_org_ks, dataset_structure=esLicense, entry_point_instance_id=ccby10.id, version_major=1, version_minor=0, version_patch=0, version_description="", version_released=True)
    ei_ccby10.save(using='default');ei_ccby10.root_id = ei_ccby10.id;ei_ccby10.save(using='default')
    ei.set_released()  # here materialization happens

    # above reccomended; below other conformant
    
    # Creative Commons CCZero
    cczero = License()
    cczero.name = "Creative Commons CCZero"
    cczero.short_name = "CC0"
    cczero.attribution = False
    cczero.share_alike = False
    cczero.url_info = "http://opendefinition.org/licenses/cc-zero"
    cczero.reccomended_by_opendefinition = True
    cczero.conformant_for_opendefinition = True
    cczero.legalcode = ''
    cczero.save(using='default')
    ei = DataSet(owner_knowledge_server=test_license_org_ks, dataset_structure=esLicense, entry_point_instance_id=cczero.id, version_major=1, version_minor=0, version_patch=0, version_description="", version_released=True)
    ei.save(using='default');ei.root_id = ei.id;ei.save(using='default')
    ei.set_released()  # here materialization happens

    # Open Data Commons Public Domain Dedication and Licence
    pddl = License()
    pddl.name = "Open Data Commons Public Domain Dedication and Licence"
    pddl.short_name = "PDDL"
    pddl.attribution = False
    pddl.share_alike = False
    pddl.url_info = "http://opendefinition.org/licenses/odc-pddl"
    pddl.reccomended_by_opendefinition = True
    pddl.conformant_for_opendefinition = True
    pddl.legalcode = ''
    pddl.save(using='default')
    ei = DataSet(owner_knowledge_server=test_license_org_ks, dataset_structure=esLicense, entry_point_instance_id=pddl.id, version_major=1, version_minor=0, version_patch=0, version_description="", version_released=True)
    ei.save(using='default');ei.root_id = ei.id;ei.save(using='default')
    ei.set_released()  # here materialization happens

    # Creative Commons Attribution 4.0
    ccby40 = License()
    ccby40.name = "Creative Commons Attribution 4.0"
    ccby40.short_name = "CC-BY-4.0"
    ccby40.attribution = True
    ccby40.share_alike = False
    ccby40.url_info = "http://creativecommons.org/licenses/by/4.0"
    ccby40.reccomended_by_opendefinition = True
    ccby40.conformant_for_opendefinition = True
    ccby40.legalcode = ''
    ccby40.save(using='default')
    # note that version_released=False
    ei = DataSet(owner_knowledge_server=test_license_org_ks, root_id=ei_ccby10.id, dataset_structure=esLicense, entry_point_instance_id=ccby40.id, version_major=4, version_minor=0, version_patch=0, version_description="", version_released=False)
    ei.save(using='default')
    # I do not set it as released; it will be done to demonstrate the notification and update process
#     ei.set_released() #here materialization happens

    # Open Data Commons Attribution License 
    odcby = License()
    odcby.name = "Open Data Commons Attribution License"
    odcby.short_name = "ODC-BY"
    odcby.attribution = True
    odcby.share_alike = False
    odcby.url_info = "http://opendefinition.org/licenses/odc-by"
    odcby.reccomended_by_opendefinition = True
    odcby.conformant_for_opendefinition = True
    odcby.legalcode = ''
    odcby.save(using='default')
    ei = DataSet(owner_knowledge_server=test_license_org_ks, dataset_structure=esLicense, entry_point_instance_id=odcby.id, version_major=1, version_minor=0, version_patch=0, version_description="", version_released=True)
    ei.save(using='default');ei.root_id = ei.id;ei.save(using='default')
    ei.set_released()  # here materialization happens

    # Creative Commons Attribution Share-Alike 4.0  
    ccbysa40 = License()
    ccbysa40.name = "Creative Commons Attribution Share-Alike 4.0"
    ccbysa40.short_name = "CC-BY-SA-4.0"
    ccbysa40.attribution = True
    ccbysa40.share_alike = True
    ccbysa40.url_info = "http://opendefinition.org/licenses/cc-by-sa"
    ccbysa40.reccomended_by_opendefinition = True
    ccbysa40.conformant_for_opendefinition = True
    ccbysa40.legalcode = ''
    ccbysa40.save(using='default')
    ei = DataSet(owner_knowledge_server=test_license_org_ks, dataset_structure=esLicense, entry_point_instance_id=ccbysa40.id, version_major=4, version_minor=0, version_patch=0, version_description="", version_released=True)
    ei.save(using='default');ei.root_id = ei.id;ei.save(using='default')
    ei.set_released()  # here materialization happens

    # Open Data Commons Open Database License 
    odbl = License()
    odbl.name = "Open Data Commons Open Database License"
    odbl.short_name = "ODbL"
    odbl.attribution = True
    odbl.share_alike = False
    odbl.url_info = "http://opendefinition.org/licenses/odc-odbl"
    odbl.reccomended_by_opendefinition = True
    odbl.conformant_for_opendefinition = True
    odbl.legalcode = ''
    odbl.save(using='default')
    ei = DataSet(owner_knowledge_server=test_license_org_ks, dataset_structure=esLicense, entry_point_instance_id=odbl.id, version_major=1, version_minor=0, version_patch=0, version_description="", version_released=True)
    ei.save(using='default');ei.root_id = ei.id;ei.save(using='default')
    ei.set_released()  # here materialization happens

    ######## END LICENSES DATA

    esLicenseList = DataSetStructure.objects.get(name="List of licenses")
    
    # 2 DataSet with the above DataSetStructure
    # opendefinition.org conformant
    ei = DataSet(owner_knowledge_server=test_license_org_ks, filter_text="conformant_for_opendefinition=True", dataset_structure=esLicenseList, description="All opendefinition.org conformant licenses.")
    ei.save(using='default');ei.root_id = ei.id;ei.save(using='default')
    # let's materialize the ei that is a view so it doesn't need to be set to released
    ei.materialize(ei.shallow_dataset_structure().entry_point, processed_instances=[])
    # opendefinition.org conformant and reccomended
    ei = DataSet(owner_knowledge_server=test_license_org_ks, filter_text="reccomended_by_opendefinition=True", dataset_structure=esLicenseList, description="All opendefinition.org conformant and reccomended licenses.")
    ei.save(using='default');ei.root_id = ei.id;ei.save(using='default')
    # let's materialize the ei that is a view so it doesn't need to be set to released
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

