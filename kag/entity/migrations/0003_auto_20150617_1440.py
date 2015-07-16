# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forwards_func(apps, schema_editor):
    Organization = apps.get_model("entity", "Organization")
    KnowledgeServer = apps.get_model("entity", "KnowledgeServer")
    SimpleEntity = apps.get_model("entity", "SimpleEntity")
    AttributeType = apps.get_model("entity", "AttributeType")
    Attribute = apps.get_model("entity", "Attribute")
    EntityStructureNode = apps.get_model("entity", "EntityStructureNode")
    EntityStructure = apps.get_model("entity", "EntityStructure")
    Workflow = apps.get_model("entity", "Workflow")
    WorkflowStatus = apps.get_model("entity", "WorkflowStatus")
    EntityInstance = apps.get_model("entity", "EntityInstance")
    
    db_alias = schema_editor.connection.alias

    orgs = Organization.objects.using(db_alias).bulk_create([
        Organization(pk=1, name="the Knowledge Oriented Architecture", URIInstance="http://rootks.thekoa.org/entity/Organization/1", website='http://www.theKOA.org', description="the Knowledge Oriented Architecture organization ....."),
    ])
    the_koa_org = orgs[0]
    
    KSs = KnowledgeServer.objects.using(db_alias).bulk_create([
        KnowledgeServer(pk=1, name="theKOA.org root Knowledge Server", scheme="http", netloc="rootks.thekoa.org", URIInstance="http://rootks.thekoa.org/entity/KnowledgeServer/1", description="The main Knowledge Server, defining the main Entities used by any other Knowledge Server", organization=the_koa_org, this_ks=True),
    ])
    the_koa_org_ks = KSs[0]
    

    se = SimpleEntity.objects.using(db_alias).bulk_create([
        SimpleEntity(id=1, name="SimpleEntity",  URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/1", module="entity", description="", table_name="", id_field="id", name_field="name", description_field="description"),
        SimpleEntity(id=2,name="Attribute", URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/2",module="entity",description="",table_name="",id_field="id",name_field="name",description_field=""),
        SimpleEntity(id=3,name="Application", URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/3",module="application",description="",table_name="",id_field="id",name_field="name",description_field="description"),
        SimpleEntity(id=4, name="Workflow", URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/4",module="entity",description="",table_name="",id_field="id",name_field="name",description_field="description"),
        SimpleEntity(id=5, name="WorkflowStatus", URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/5",module="entity",description="",table_name="",id_field="id",name_field="name",description_field="description"),
        SimpleEntity(id=6, name="Method", URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/6",module="application",description="",table_name="",id_field="id",name_field="name",description_field="description"),
        SimpleEntity(id=7, name="AttributeType", URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/7",module="entity",description="",table_name="",id_field="id",name_field="name",description_field=""),
        SimpleEntity(id=8, name="Widget", URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/8",module="application",description="",table_name="",id_field="id",name_field="widgetname",description_field=""),
        SimpleEntity(id=9,name="EntityStructureNode", URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/9",module="entity",description="",table_name="",id_field="id",name_field="attribute",description_field=""),
        SimpleEntity(id=10,name="EntityStructure",     URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/10",module="entity",description="",table_name="",id_field="id",name_field="name",     description_field=""),
        SimpleEntity(id=11,name="AttributeInAMethod", URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/11",module="application",description="",table_name="",id_field="id",name_field="name",description_field=""),
        SimpleEntity(id=12, name="Organization",  URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/12", module="entity", description="", table_name="", id_field="id", name_field="name", description_field="description"),
        SimpleEntity(id=13, name="EntityInstance",  URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/13", module="entity", description="", table_name="", id_field="id", name_field="", description_field=""),
        SimpleEntity(id=14, name="KnowledgeServer",  URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/14", module="entity", description="", table_name="", id_field="id", name_field="name", description_field="description"),
        SimpleEntity(id=15, name="DBConnection",  URIInstance="http://rootks.thekoa.org/entity/SimpleEntity/15", module="entity", description="", table_name="", id_field="id", name_field="name", description_field="description"),
        
    ])
    seSimpleEntity=se[0];seAttribute=se[1];seApplication=se[2];seWorkflow=se[3];seWorkflowStatus=se[4];seMethod=se[5];seAttributeType=se[6];seWidget=se[7];seEntityStructureNode=se[8];seEntityStructure=se[9];seAttributeInAMethod=se[10];seOrganization=se[11];seEntityInstance=se[12];seKnowledgeServer=se[13];seDBConnection=se[14]
        
    at = AttributeType.objects.using(db_alias).bulk_create([
        AttributeType(id=1, name="Text", URIInstance="http://rootks.thekoa.org/entity/AttributeType/1"),
        AttributeType(id=2, name="Date", URIInstance="http://rootks.thekoa.org/entity/AttributeType/2"),
        AttributeType(id=3, name="ForeignKey", URIInstance="http://rootks.thekoa.org/entity/AttributeType/3"),
    ])
    atText=at[0];atDate=at[1];atForeignKey=at[2];
    
#     SimpleEntity
    a = Attribute.objects.using(db_alias).bulk_create([
        Attribute(id=1, name="name", type=atText, simple_entity=seSimpleEntity, URIInstance="http://rootks.thekoa.org/entity/Attribute/1"),

        Attribute(id=3, name="URIInstance", type=atText, simple_entity=seSimpleEntity, URIInstance="http://rootks.thekoa.org/entity/Attribute/4"),

        Attribute(id=5, name="module", type=atText, simple_entity=seSimpleEntity, URIInstance="http://rootks.thekoa.org/entity/Attribute/6"),
        Attribute(id=6, name="table_name", type=atText, simple_entity=seSimpleEntity, URIInstance="http://rootks.thekoa.org/entity/Attribute/7"),
        Attribute(id=7, name="id_field", type=atText, simple_entity=seSimpleEntity, URIInstance="http://rootks.thekoa.org/entity/Attribute/8"),
        Attribute(id=8, name="name_field", type=atText, simple_entity=seSimpleEntity, URIInstance="http://rootks.thekoa.org/entity/Attribute/9"),
        Attribute(id=9, name="description_field", type=atText, simple_entity=seSimpleEntity, URIInstance="http://rootks.thekoa.org/entity/Attribute/10"),
        Attribute(id=10, name="description", type=atText, simple_entity=seSimpleEntity, URIInstance="http://rootks.thekoa.org/entity/Attribute/11"),
    ])
    aname=a[0];aURIInstance=a[1];amodule=a[2];atable_name=a[3];aid_field=a[4];aname_field=a[5];adescription_field=a[6];adescription=a[7]
#     Organization
#     AttributeType
#     Attribute
#     EntityStructureNode
#     EntityStructure
#     Workflow
#     WorkflowStatus
#     EntityInstance

    en = EntityStructureNode.objects.using(db_alias).bulk_create([
    # "SimpleEntity-attributes"     entry_point=en1
        EntityStructureNode(id=1,  simple_entity=seSimpleEntity, URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/1"),
        EntityStructureNode(id=2,  simple_entity=seAttribute,          attribute="attribute_set", is_many=True, URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/2"),
        EntityStructureNode(id=3,  simple_entity=seAttributeType,      attribute="type", URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/3"),
    # "EntityStructure-EntityStructureNode-Application"    entry_point=en22
        EntityStructureNode(id=4,  simple_entity=seEntityStructure,    URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/4"),
        EntityStructureNode(id=5,  simple_entity=seEntityStructureNode,         attribute="entry_point", URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/5"),
        EntityStructureNode(id=6,  simple_entity=seSimpleEntity,       attribute="simple_entity", external_reference=True,URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/6"),
        EntityStructureNode(id=7,  simple_entity=seEntityStructureNode,         attribute="child_nodes", is_many=True,URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/7"),
        EntityStructureNode(id=8,  simple_entity=seAttribute,          attribute="attribute_set", external_reference=True, is_many=True, URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/8"),
        EntityStructureNode(id=9,  simple_entity=seAttributeType,      attribute="type", external_reference=True, URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/9"),
        EntityStructureNode(id=10, simple_entity=seAttributeInAMethod, attribute="attributeinamethod_set", is_many=True, URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/10"),
        EntityStructureNode(id=11, simple_entity=seMethod,             attribute="implementation_method", URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/11"),
        EntityStructureNode(id=12, simple_entity=seWorkflowStatus,     attribute="initial_statuses", external_reference=True, is_many=True, URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/12"),
        EntityStructureNode(id=13, simple_entity=seWorkflow,           attribute="workflow", external_reference=True, URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/13"),
        EntityStructureNode(id=15, simple_entity=seApplication,        attribute="application_set", is_many=True, URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/15"),
    # "Workflow-statuses"     entry_point=en16
        EntityStructureNode(id=16, simple_entity=seWorkflow,     URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/16"),
        EntityStructureNode(id=17, simple_entity=seWorkflowStatus,     attribute="workflowstatus_set", is_many=True,URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/17"),
    # "Organization-KS"     entry_point=en18
        EntityStructureNode(id=18, simple_entity=seOrganization,     URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/18"),
        EntityStructureNode(id=19, simple_entity=seKnowledgeServer,     attribute="knowledgeserver_set", is_many=True,URIInstance="http://rootks.thekoa.org/entity/EntityStructureNode/19"),
    ])
    en1=en[0];en2=en[1];en3=en[2];en4=en[3];en5=en[4];en6=en[5];en7=en[6];en8=en[7];en9=en[8];en10=en[9];en11=en[10];en12=en[11];en13=en[12];
    en15=en[13];en16=en[14];en17=en[15];en18=en[16];en19=en[17];
    
    # eSimpleEntityAttributes
    en1.child_nodes.add(en2); en1.save()
    en2.child_nodes.add(en3); en2.save()
    eSimpleEntityAttributes=EntityStructure(id=1,entry_point=en1,name="SimpleEntity-attributes",namespace="entity",description="",URIInstance="http://rootks.thekoa.org/entity/EntityStructure/1")
    eSimpleEntityAttributes.save()
    seSimpleEntity.entity_structure = eSimpleEntityAttributes; seSimpleEntity.save()
    seAttribute.entity_structure = eSimpleEntityAttributes; seAttribute.save()
    seAttributeType.entity_structure = eSimpleEntityAttributes; seAttributeType.save()
    
    # eEntityStructureEntityStructureNodeApplication
    en4.child_nodes.add(en5); en4.save()
    en5.child_nodes.add(en6); en5.child_nodes.add(en7); en5.save()
    en6.child_nodes.add(en8); en6.save()
    en7.child_nodes.add(en6); en7.child_nodes.add(en7); en7.save()
    en8.child_nodes.add(en9); en8.child_nodes.add(en10); en8.save()
    en10.child_nodes.add(en11); en10.save()
    en11.child_nodes.add(en12); en11.child_nodes.add(en13); en11.save()
    en13.child_nodes.add(en15); en13.save()
    eEntityStructureEntityStructureNodeApplication=EntityStructure(id=2,entry_point=en4,name="EntityStructure-EntityStructureNode-Application",namespace="entity",description="",URIInstance="http://rootks.thekoa.org/entity/EntityStructure/2")
    eEntityStructureEntityStructureNodeApplication.save()
    seEntityStructure.entity_structure = eEntityStructureEntityStructureNodeApplication; seEntityStructure.save()
    seEntityStructureNode.entity_structure = eEntityStructureEntityStructureNodeApplication; seEntityStructureNode.save()
    seAttributeInAMethod.entity_structure = eEntityStructureEntityStructureNodeApplication; seAttributeInAMethod.save()
    seMethod.entity_structure = eEntityStructureEntityStructureNodeApplication; seMethod.save()
    seApplication.entity_structure = eEntityStructureEntityStructureNodeApplication; seApplication.save()

    # eWorkflowStatuses
    en16.child_nodes.add(en17); en16.save()
    eWorkflowStatuses=EntityStructure(id=3,entry_point=en16,name="Workflow-statuses",namespace="entity",description="",URIInstance="http://rootks.thekoa.org/entity/EntityStructure/3")
    eWorkflowStatuses.save()
    seWorkflow.entity_structure = eWorkflowStatuses; seWorkflow.save()
    seWorkflowStatus.entity_structure = eWorkflowStatuses; seWorkflowStatus.save()
    
    # eOrganizationKS
    en18.child_nodes.add(en19); en18.save()
    eOrganizationKS=EntityStructure(id=4,entry_point=en18,name="Organization-KS",namespace="entity",description="",URIInstance="http://rootks.thekoa.org/entity/EntityStructure/4")
    eOrganizationKS.save()
    seOrganization.entity_structure = eOrganizationKS; seOrganization.save()
    seKnowledgeServer.entity_structure = eOrganizationKS; seKnowledgeServer.save()
    
    w = Workflow.objects.using(db_alias).bulk_create([
        Workflow(id=1,name="Generic default workflow",description="",URIInstance="http://rootks.thekoa.org/entity/Workflow/1"),
    ])
    wgeneric = w[0]
    ws = WorkflowStatus.objects.using(db_alias).bulk_create([
        WorkflowStatus(id=1,name="Generic",workflow=wgeneric,description="",URIInstance="http://rootks.thekoa.org/entity/WorkflowStatus/1"),
    ])
    EntityInstance.objects.using(db_alias).bulk_create([
        EntityInstance(id= 1,root_id= 1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws[0],entry_point_instance_id=seSimpleEntity.id,                                version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/1",version_released=True),
        EntityInstance(id= 2,root_id= 2,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws[0],entry_point_instance_id=seAttribute.id,                                   version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/2",version_released=True),
        EntityInstance(id= 3,root_id= 3,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws[0],entry_point_instance_id=seApplication.id,                                 version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/3",version_released=True),
        EntityInstance(id= 4,root_id= 4,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws[0],entry_point_instance_id=seWorkflow.id,                                    version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/4",version_released=True),
        EntityInstance(id= 5,root_id= 5,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws[0],entry_point_instance_id=seWorkflowStatus.id,                              version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/5",version_released=True),
        EntityInstance(id= 6,root_id= 6,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws[0],entry_point_instance_id=seMethod.id,                                      version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/6",version_released=True),
        EntityInstance(id= 7,root_id= 7,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws[0],entry_point_instance_id=seAttributeType.id,                               version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/7",version_released=True),
        EntityInstance(id= 8,root_id= 8,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws[0],entry_point_instance_id=seWidget.id,                                      version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/8",version_released=True),
        EntityInstance(id= 9,root_id= 9,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws[0],entry_point_instance_id=seEntityStructureNode.id,                         version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/9",version_released=True),
        EntityInstance(id=10,root_id=10,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws[0],entry_point_instance_id=seEntityStructure.id,                             version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/10",version_released=True),
        EntityInstance(id=11,root_id=11,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws[0],entry_point_instance_id=seAttributeInAMethod.id,                          version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/11",version_released=True),
        EntityInstance(id=12,root_id=12,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws[0],entry_point_instance_id=seOrganization.id,                                version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/12",version_released=True),
        EntityInstance(id=13,root_id=13,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws[0],entry_point_instance_id=seEntityInstance.id,                              version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/13",version_released=True),
        EntityInstance(id=14,root_id=14,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws[0],entry_point_instance_id=seKnowledgeServer.id,                             version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/14",version_released=True),
        EntityInstance(id=15,root_id=15,owner_knowledge_server=the_koa_org_ks,entity_structure=eEntityStructureEntityStructureNodeApplication, workflow=wgeneric,current_status=ws[0],entry_point_instance_id=eSimpleEntityAttributes.id,                       version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/15",version_released=True),
        EntityInstance(id=16,root_id=16,owner_knowledge_server=the_koa_org_ks,entity_structure=eEntityStructureEntityStructureNodeApplication, workflow=wgeneric,current_status=ws[0],entry_point_instance_id=eEntityStructureEntityStructureNodeApplication.id,version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/16",version_released=True),
        EntityInstance(id=17,root_id=17,owner_knowledge_server=the_koa_org_ks,entity_structure=eEntityStructureEntityStructureNodeApplication, workflow=wgeneric,current_status=ws[0],entry_point_instance_id=eWorkflowStatuses.id,                             version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/17",version_released=True),
        EntityInstance(id=18,root_id=18,owner_knowledge_server=the_koa_org_ks,entity_structure=eEntityStructureEntityStructureNodeApplication, workflow=wgeneric,current_status=ws[0],entry_point_instance_id=eOrganizationKS.id,                               version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/18",version_released=True),
        EntityInstance(id=19,root_id=19,owner_knowledge_server=the_koa_org_ks,entity_structure=eOrganizationKS,                                workflow=wgeneric,current_status=ws[0],entry_point_instance_id=the_koa_org.id,                                   version_major=0,version_minor=1,version_patch=0,version_description="",URIInstance="http://rootks.thekoa.org/entity/EntityInstance/19",version_released=True),
    ])



class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0002_auto_20150617_1440'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

