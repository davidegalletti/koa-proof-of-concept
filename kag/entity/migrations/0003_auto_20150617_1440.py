# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from entity.models import Organization, KnowledgeServer, SimpleEntity, AttributeType, Attribute, StructureNode, EntityStructure, Workflow, WorkflowStatus, DataSet

def forwards_func(apps, schema_editor):
    
    db_alias = schema_editor.connection.alias
    
    the_koa_org = Organization();the_koa_org.id=1;the_koa_org.name="the Knowledge Oriented Architecture";the_koa_org.URIInstance="http://rootks.thekoa.org/entity/Organization/1";the_koa_org.website='http://www.theKOA.org';the_koa_org.description="the Knowledge Oriented Architecture organization .....";the_koa_org.save(using=db_alias)
    
    the_koa_org_ks = KnowledgeServer(pk=1, name="theKOA.org root Open Knowledge Server", scheme="http", netloc="rootks.thekoa.org", URIInstance="http://rootks.thekoa.org/entity/KnowledgeServer/1", description="The main OKS, defining the main structures and datasets used by any other Knowledge Server.", organization=the_koa_org, this_ks=True,html_home="<i><strong>rootks html_home</strong></i>", html_disclaimer="<i><strong>rootks html_disclaimer</strong></i>")
    the_koa_org_ks.save(using=db_alias)
    
    #SimpleEntity
    seSimpleEntity=SimpleEntity();seSimpleEntity.name="SimpleEntity";seSimpleEntity.module="entity";seSimpleEntity.save(using=db_alias)
    seAttribute=SimpleEntity();seAttribute.name="Attribute";seAttribute.module="entity";seAttribute.description_field="";seAttribute.save(using=db_alias)
    seApplication=SimpleEntity();seApplication.name="Application";seApplication.module="application";seApplication.save(using=db_alias) 
    seWorkflow=SimpleEntity();seWorkflow.name="Workflow";seWorkflow.module="entity";seWorkflow.save(using=db_alias)
    seWorkflowStatus=SimpleEntity();seWorkflowStatus.name="WorkflowStatus";seWorkflowStatus.module="entity";seWorkflowStatus.save(using=db_alias)    
    seMethod=SimpleEntity();seMethod.name="Method";seMethod.module="application";seMethod.save(using=db_alias)
    seAttributeType=SimpleEntity();seAttributeType.name="AttributeType";seAttributeType.module="entity";seAttributeType.description_field="";seAttributeType.save(using=db_alias)
    seWidget=SimpleEntity();seWidget.name="Widget";seWidget.module="application";seWidget.name_field="widgetname";seWidget.description_field="";seWidget.save(using=db_alias)
    seStructureNode=SimpleEntity();seStructureNode.name="StructureNode";seStructureNode.module="entity";seStructureNode.name_field="attribute";seStructureNode.description_field="";seStructureNode.save(using=db_alias)
    seEntityStructure=SimpleEntity();seEntityStructure.name="EntityStructure";seEntityStructure.module="entity";seEntityStructure.description_field;seEntityStructure.save(using=db_alias)
    seAttributeInAMethod=SimpleEntity();seAttributeInAMethod.name="AttributeInAMethod";seAttributeInAMethod.module="application";seAttributeInAMethod.description_field="";seAttributeInAMethod.save(using=db_alias)
    seOrganization=SimpleEntity();seOrganization.name="Organization";seOrganization.module="entity";seOrganization.save(using=db_alias)
    seDataSet=SimpleEntity();seDataSet.name="DataSet";seDataSet.module="entity";seDataSet.name_field="";seDataSet.description_field="";seDataSet.save(using=db_alias)
    seKnowledgeServer=SimpleEntity();seKnowledgeServer.name="KnowledgeServer";seKnowledgeServer.module="entity";seKnowledgeServer.save(using=db_alias)
    seDBConnection=SimpleEntity();seDBConnection.name="DBConnection";seDBConnection.module="entity";seDBConnection.save(using=db_alias)
    seLicense=SimpleEntity();seLicense.name="License";seLicense.module="license";seLicense.save(using=db_alias)
 
    #AttributeType
    atText=AttributeType();atText.name="Text";atText.save(using=db_alias)
    atDate=AttributeType();atDate.name="Date";atDate.save(using=db_alias)
    atForeignKey=AttributeType();atForeignKey.name="ForeignKey";atForeignKey.save(using=db_alias)
 
     
    #Attribute for SimpleEntity
    aname=Attribute();aname.name="name";aname.type=atText;aname.simple_entity=seSimpleEntity;aname.save(using=db_alias)
    aURIInstance=Attribute();aURIInstance.name="URIInstance";aURIInstance.type=atText;aURIInstance.simple_entity=seSimpleEntity;aURIInstance.save(using=db_alias)
    amodule=Attribute();amodule.name="module";amodule.type=atText;amodule.simple_entity=seSimpleEntity;amodule.save(using=db_alias)
    atable_name=Attribute();atable_name.name="table_name";atable_name.type=atText;atable_name.simple_entity=seSimpleEntity;atable_name.save(using=db_alias)
    aid_field=Attribute();aid_field.name="id_field";aid_field.type=atText;aid_field.simple_entity=seSimpleEntity;aid_field.save(using=db_alias)
    aname_field=Attribute();aname_field.name="name_field";aname_field.type=atText;aname_field.simple_entity=seSimpleEntity;aname_field.save(using=db_alias)
    adescription_field=Attribute();adescription_field.name="description_field";adescription_field.type=atText;adescription_field.simple_entity=seSimpleEntity;adescription_field.save(using=db_alias)
    adescription=Attribute();adescription.name="description";adescription.type=atText;adescription.simple_entity=seSimpleEntity;adescription.save(using=db_alias)
    # TBC Attributes for
    #     Organization
    #     AttributeType
    #     Attribute
    #     StructureNode
    #     EntityStructure
    #     Workflow
    #     WorkflowStatus
    #     DataSet
     
    # StructureNode for "SimpleEntity-attributes"     entry_point=en1
    en1=StructureNode();en1.simple_entity=seSimpleEntity;en1.save(using=db_alias) 
    en2=StructureNode();en2.simple_entity=seAttribute;en2.attribute="attribute_set";en2.is_many=True;en2.save(using=db_alias)
    en3=StructureNode();en3.simple_entity=seAttributeType;en3.attribute="type";en3.save(using=db_alias)
    # StructureNode for "EntityStructure-StructureNode-Application"    entry_point=en22
    en4=StructureNode();en4.simple_entity=seEntityStructure;en4.save(using=db_alias)
    en5=StructureNode();en5.simple_entity=seStructureNode;en5.attribute="entry_point";en5.save(using=db_alias)
    en6=StructureNode();en6.simple_entity=seSimpleEntity;en6.attribute="simple_entity";en6.external_reference=True;en6.save(using=db_alias)
    en7=StructureNode();en7.simple_entity=seStructureNode;en7.attribute="child_nodes";en7.is_many=True;en7.save(using=db_alias)
#     en8=StructureNode();en8.simple_entity=seAttribute;en8.attribute="attribute_set";en8.external_reference=True;en8.is_many=True;en8.save(using=db_alias)
#     en9=StructureNode();en9.simple_entity=seAttributeType;en9.attribute="type";en9.external_reference=True;en9.save(using=db_alias)
#     en10=StructureNode();en10.simple_entity=seAttributeInAMethod;en10.attribute="attributeinamethod_set";en10.is_many=True;en10.save(using=db_alias)
#     en11=StructureNode();en11.simple_entity=seMethod;en11.attribute="implementation_method";en11.save(using=db_alias)
#     en12=StructureNode();en12.simple_entity=seWorkflowStatus;en12.attribute="initial_statuses";en12.external_reference=True;en12.is_many=True;en12.save(using=db_alias)
#     en13=StructureNode();en13.simple_entity=seWorkflow;en13.attribute="workflow";en13.external_reference=True;en13.save(using=db_alias)
#     en15=StructureNode();en15.simple_entity=seApplication;en15.attribute="application_set";en15.is_many=True;en15.save(using=db_alias)
    # StructureNode for "Workflow-statuses"     entry_point=en16
    en16=StructureNode();en16.simple_entity=seWorkflow;en16.save(using=db_alias)
    en17=StructureNode();en17.simple_entity=seWorkflowStatus;en17.attribute="workflowstatus_set";en17.is_many=True;en17.save(using=db_alias)
    # StructureNode for "Organization-KS"     entry_point=en18
    en18=StructureNode();en18.simple_entity=seOrganization;en18.save(using=db_alias)
    en19=StructureNode();en19.simple_entity=seKnowledgeServer;en19.attribute="knowledgeserver_set";en19.is_many=True;en19.save(using=db_alias)
     
    # esSimpleEntityAttributes
    en1.child_nodes.add(en2); en1.save(using=db_alias)
    en2.child_nodes.add(en3); en2.save(using=db_alias)
    esSimpleEntityAttributes=EntityStructure();esSimpleEntityAttributes.multiple_releases=False;esSimpleEntityAttributes.entry_point=en1;esSimpleEntityAttributes.name=EntityStructure.simple_entity_entity_structure_name;esSimpleEntityAttributes.description="Metadata describing an entity, i.e. something closely related to what is stored in a database table, and its attributes.";esSimpleEntityAttributes.namespace="entity";esSimpleEntityAttributes.save(using=db_alias)
    seSimpleEntity.entity_structure = esSimpleEntityAttributes; seSimpleEntity.save(using=db_alias)
     
    seAttribute.entity_structure = esSimpleEntityAttributes; seAttribute.save(using=db_alias)
    aname.save(using=db_alias);aURIInstance.save(using=db_alias);amodule.save(using=db_alias);atable_name.save(using=db_alias);aid_field.save(using=db_alias);aname_field.save(using=db_alias);adescription_field.save(using=db_alias);adescription.save(using=db_alias)
     
    seAttributeType.entity_structure = esSimpleEntityAttributes; seAttributeType.save(using=db_alias)
    atText.save(using=db_alias);atDate.save(using=db_alias);atForeignKey.save(using=db_alias); #saving again to create URIInstance via the post_save signal
     
    # esEntityStructureStructureNodeApplication
    en4.child_nodes.add(en5); en4.save(using=db_alias)
    en5.child_nodes.add(en6); en5.child_nodes.add(en7); en5.save(using=db_alias)
#     en6.child_nodes.add(en8); en6.save(using=db_alias)
    en7.child_nodes.add(en6); en7.child_nodes.add(en7); en7.save(using=db_alias)
#     en8.child_nodes.add(en9); en8.child_nodes.add(en10); en8.save(using=db_alias)
#     en10.child_nodes.add(en11); en10.save(using=db_alias)
#     en11.child_nodes.add(en12); en11.child_nodes.add(en13); en11.save(using=db_alias)
#     en13.child_nodes.add(en15); en13.save(using=db_alias)
    esEntityStructureStructureNodeApplication=EntityStructure(id=2,multiple_releases=False,entry_point=en4,name=EntityStructure.dataset_structure_name,description="A graph of simple entities that have relationships with one another and whose instances share the same version, status, ...",namespace="entity",URIInstance="http://rootks.thekoa.org/entity/EntityStructure/2")
    esEntityStructureStructureNodeApplication.save(using=db_alias)
    seEntityStructure.entity_structure = esEntityStructureStructureNodeApplication; seEntityStructure.save(using=db_alias)
    esSimpleEntityAttributes.save(using=db_alias);esEntityStructureStructureNodeApplication.save(using=db_alias); #saving again to create URIInstance via the post_save signal
     
    seStructureNode.entity_structure = esEntityStructureStructureNodeApplication; seStructureNode.save(using=db_alias)
    en1.save(using=db_alias);en2.save(using=db_alias);en3.save(using=db_alias);en4.save(using=db_alias);en5.save(using=db_alias);en6.save(using=db_alias);en7.save(using=db_alias);en16.save(using=db_alias);en17.save(using=db_alias);en18.save(using=db_alias);en19.save(using=db_alias)
     
    seAttributeInAMethod.entity_structure = esEntityStructureStructureNodeApplication; seAttributeInAMethod.save(using=db_alias)
    seMethod.entity_structure = esEntityStructureStructureNodeApplication; seMethod.save(using=db_alias)
    seApplication.entity_structure = esEntityStructureStructureNodeApplication; seApplication.save(using=db_alias)
 
 
    # esWorkflowStatuses
    en16.child_nodes.add(en17); en16.save(using=db_alias)
    esWorkflowStatuses=EntityStructure(id=3,multiple_releases=True,entry_point=en16,name=EntityStructure.workflow_entity_structure_name,namespace="entity",description="A workflow and its statuses",URIInstance="http://rootks.thekoa.org/entity/EntityStructure/3")
    esWorkflowStatuses.save(using=db_alias)
    seWorkflow.entity_structure = esWorkflowStatuses; seWorkflow.save(using=db_alias)
    seWorkflowStatus.entity_structure = esWorkflowStatuses; seWorkflowStatus.save(using=db_alias)
     
    # eOrganizationKS
    en18.child_nodes.add(en19); en18.save(using=db_alias)
    eOrganizationKS=EntityStructure(id=4,multiple_releases=False,entry_point=en18,name=EntityStructure.organization_entity_structure_name,namespace="entity",description="An Organization and its Knowledge Servers",URIInstance="http://rootks.thekoa.org/entity/EntityStructure/4")
    eOrganizationKS.save(using=db_alias)
    seOrganization.entity_structure = eOrganizationKS; seOrganization.save(using=db_alias)
    seKnowledgeServer.entity_structure = eOrganizationKS; seKnowledgeServer.save(using=db_alias)
     
    # DataSet
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esSimpleEntityAttributes,entry_point_instance_id=seSimpleEntity.id,version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    # DataSet has no EntityStructure, I create the shallow one so that I can set EntityStructure.namespace 
    # and hence generate the URIInstance for each instance of DataSet
    es = ei.shallow_entity_structure(db_alias)
    es.namespace = "entity"
    es.save(using=db_alias)
    seDataSet.entity_structure = es
    seDataSet.save(using=db_alias)
    ei.save(using=db_alias)
     
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esSimpleEntityAttributes,                        entry_point_instance_id=seAttribute.id,                                   version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esSimpleEntityAttributes,                        entry_point_instance_id=seApplication.id,                                 version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esSimpleEntityAttributes,                        entry_point_instance_id=seWorkflow.id,                                    version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esSimpleEntityAttributes,                        entry_point_instance_id=seWorkflowStatus.id,                              version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esSimpleEntityAttributes,                        entry_point_instance_id=seMethod.id,                                      version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esSimpleEntityAttributes,                        entry_point_instance_id=seAttributeType.id,                               version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esSimpleEntityAttributes,                        entry_point_instance_id=seWidget.id,                                      version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esSimpleEntityAttributes,                        entry_point_instance_id=seStructureNode.id,                         version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esSimpleEntityAttributes,                        entry_point_instance_id=seEntityStructure.id,                             version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esSimpleEntityAttributes,                        entry_point_instance_id=seAttributeInAMethod.id,                          version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esSimpleEntityAttributes,                        entry_point_instance_id=seOrganization.id,                                version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esSimpleEntityAttributes,                        entry_point_instance_id=seDataSet.id,                              version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esSimpleEntityAttributes,                        entry_point_instance_id=seKnowledgeServer.id,                             version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esEntityStructureStructureNodeApplication, entry_point_instance_id=esSimpleEntityAttributes.id,                       version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esEntityStructureStructureNodeApplication, entry_point_instance_id=esEntityStructureStructureNodeApplication.id,version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esEntityStructureStructureNodeApplication, entry_point_instance_id=esWorkflowStatuses.id,                             version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=esEntityStructureStructureNodeApplication, entry_point_instance_id=eOrganizationKS.id,                               version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)
    ei = DataSet(owner_knowledge_server=the_koa_org_ks,entity_structure=eOrganizationKS,                                 entry_point_instance_id=the_koa_org.id,                                   version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save(using=db_alias);ei.root_id=ei.id;ei.save(using=db_alias)



class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0002_auto_20150617_1440'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

