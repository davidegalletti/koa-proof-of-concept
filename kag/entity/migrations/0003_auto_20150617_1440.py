# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from entity.models import Organization, KnowledgeServer, SimpleEntity, AttributeType, Attribute, EntityStructureNode, EntityStructure, Workflow, WorkflowStatus, EntityInstance

def forwards_func(apps, schema_editor):
    the_koa_org = Organization();the_koa_org.id=1;the_koa_org.name="the Knowledge Oriented Architecture";the_koa_org.URIInstance="http://rootks.thekoa.org/entity/Organization/1";the_koa_org.website='http://www.theKOA.org';the_koa_org.description="the Knowledge Oriented Architecture organization .....";the_koa_org.save()
    
    the_koa_org_ks = KnowledgeServer(pk=1, name="theKOA.org root Knowledge Server", scheme="http", netloc="rootks.thekoa.org", URIInstance="http://rootks.thekoa.org/entity/KnowledgeServer/1", description="The main Knowledge Server, defining the main Entities used by any other Knowledge Server", organization=the_koa_org, this_ks=True)
    the_koa_org_ks.save()
    
    #SimpleEntity
    seSimpleEntity=SimpleEntity();seSimpleEntity.name="SimpleEntity";seSimpleEntity.module="entity";seSimpleEntity.save()
    seAttribute=SimpleEntity();seAttribute.name="Attribute";seAttribute.module="entity";seAttribute.description_field="";seAttribute.save()
    seApplication=SimpleEntity();seApplication.name="Application";seApplication.module="application";seApplication.save() 
    seWorkflow=SimpleEntity();seWorkflow.name="Workflow";seWorkflow.module="entity";seWorkflow.save()
    seWorkflowStatus=SimpleEntity();seWorkflowStatus.name="WorkflowStatus";seWorkflowStatus.module="entity";seWorkflowStatus.save()    
    seMethod=SimpleEntity();seMethod.name="Method";seMethod.module="application";seMethod.save()
    seAttributeType=SimpleEntity();seAttributeType.name="AttributeType";seAttributeType.module="entity";seAttributeType.description_field="";seAttributeType.save()
    seWidget=SimpleEntity();seWidget.name="Widget";seWidget.module="application";seWidget.name_field="widgetname";seWidget.description_field="";seWidget.save()
    seEntityStructureNode=SimpleEntity();seEntityStructureNode.name="EntityStructureNode";seEntityStructureNode.module="entity";seEntityStructureNode.name_field="attribute";seEntityStructureNode.description_field="";seEntityStructureNode.save()
    seEntityStructure=SimpleEntity();seEntityStructure.name="EntityStructure";seEntityStructure.module="entity";seEntityStructure.description_field;seEntityStructure.save()
    seAttributeInAMethod=SimpleEntity();seAttributeInAMethod.name="AttributeInAMethod";seAttributeInAMethod.module="application";seAttributeInAMethod.description_field="";seAttributeInAMethod.save()
    seOrganization=SimpleEntity();seOrganization.name="Organization";seOrganization.module="entity";seOrganization.save()
    seEntityInstance=SimpleEntity();seEntityInstance.name="EntityInstance";seEntityInstance.module="entity";seEntityInstance.name_field="";seEntityInstance.description_field="";seEntityInstance.save()
    seKnowledgeServer=SimpleEntity();seKnowledgeServer.name="KnowledgeServer";seKnowledgeServer.module="entity";seKnowledgeServer.save()
    seDBConnection=SimpleEntity();seDBConnection.name="DBConnection";seDBConnection.module="entity";seDBConnection.save()

    #AttributeType
    atText=AttributeType();atText.name="Text";atText.save()
    atDate=AttributeType();atDate.name="Date";atDate.save()
    atForeignKey=AttributeType();atForeignKey.name="ForeignKey";atForeignKey.save()

    
    #Attribute for SimpleEntity
    aname=Attribute();aname.name="name";aname.type=atText;aname.simple_entity=seSimpleEntity;aname.save()
    aURIInstance=Attribute();aURIInstance.name="URIInstance";aURIInstance.type=atText;aURIInstance.simple_entity=seSimpleEntity;aURIInstance.save()
    amodule=Attribute();amodule.name="module";amodule.type=atText;amodule.simple_entity=seSimpleEntity;amodule.save()
    atable_name=Attribute();atable_name.name="table_name";atable_name.type=atText;atable_name.simple_entity=seSimpleEntity;atable_name.save()
    aid_field=Attribute();aid_field.name="id_field";aid_field.type=atText;aid_field.simple_entity=seSimpleEntity;aid_field.save()
    aname_field=Attribute();aname_field.name="name_field";aname_field.type=atText;aname_field.simple_entity=seSimpleEntity;aname_field.save()
    adescription_field=Attribute();adescription_field.name="description_field";adescription_field.type=atText;adescription_field.simple_entity=seSimpleEntity;adescription_field.save()
    adescription=Attribute();adescription.name="description";adescription.type=atText;adescription.simple_entity=seSimpleEntity;adescription.save()
    # TBC Attributes for
    #     Organization
    #     AttributeType
    #     Attribute
    #     EntityStructureNode
    #     EntityStructure
    #     Workflow
    #     WorkflowStatus
    #     EntityInstance
    
    # EntityStructureNode for "SimpleEntity-attributes"     entry_point=en1
    en1=EntityStructureNode();en1.simple_entity=seSimpleEntity;en1.save() 
    en2=EntityStructureNode();en2.simple_entity=seAttribute;en2.attribute="attribute_set";en2.is_many=True;en2.save()
    en3=EntityStructureNode();en3.simple_entity=seAttributeType;en3.attribute="type";en3.save()
    # EntityStructureNode for "EntityStructure-EntityStructureNode-Application"    entry_point=en22
    en4=EntityStructureNode();en4.simple_entity=seEntityStructure;en4.save()
    en5=EntityStructureNode();en5.simple_entity=seEntityStructureNode;en5.attribute="entry_point";en5.save()
    en6=EntityStructureNode();en6.simple_entity=seSimpleEntity;en6.attribute="simple_entity";en6.external_reference=True;en6.save()
    en7=EntityStructureNode();en7.simple_entity=seEntityStructureNode;en7.attribute="child_nodes";en7.is_many=True;en7.save()
    en8=EntityStructureNode();en8.simple_entity=seAttribute;en8.attribute="attribute_set";en8.external_reference=True;en8.is_many=True;en8.save()
    en9=EntityStructureNode();en9.simple_entity=seAttributeType;en9.attribute="type";en9.external_reference=True;en9.save()
    en10=EntityStructureNode();en10.simple_entity=seAttributeInAMethod;en10.attribute="attributeinamethod_set";en10.is_many=True;en10.save()
    en11=EntityStructureNode();en11.simple_entity=seMethod;en11.attribute="implementation_method";en11.save()
    en12=EntityStructureNode();en12.simple_entity=seWorkflowStatus;en12.attribute="initial_statuses";en12.external_reference=True;en12.is_many=True;en12.save()
    en13=EntityStructureNode();en13.simple_entity=seWorkflow;en13.attribute="workflow";en13.external_reference=True;en13.save()
    en15=EntityStructureNode();en15.simple_entity=seApplication;en15.attribute="application_set";en15.is_many=True;en15.save()
    # EntityStructureNode for "Workflow-statuses"     entry_point=en16
    en16=EntityStructureNode();en16.simple_entity=seWorkflow;en16.save()
    en17=EntityStructureNode();en17.simple_entity=seWorkflowStatus;en17.attribute="workflowstatus_set";en17.is_many=True;en17.save()
    # EntityStructureNode for "Organization-KS"     entry_point=en18
    en18=EntityStructureNode();en18.simple_entity=seOrganization;en18.save()
    en19=EntityStructureNode();en19.simple_entity=seKnowledgeServer;en19.attribute="knowledgeserver_set";en19.is_many=True;en19.save()
    
    # eSimpleEntityAttributes
    en1.child_nodes.add(en2); en1.save()
    en2.child_nodes.add(en3); en2.save()
    eSimpleEntityAttributes=EntityStructure();eSimpleEntityAttributes.entry_point=en1;eSimpleEntityAttributes.name="SimpleEntity-attributes";eSimpleEntityAttributes.namespace="entity";eSimpleEntityAttributes.save()
    seSimpleEntity.entity_structure = eSimpleEntityAttributes; seSimpleEntity.save()
    
    seAttribute.entity_structure = eSimpleEntityAttributes; seAttribute.save()
    aname.save();aURIInstance.save();amodule.save();atable_name.save();aid_field.save();aname_field.save();adescription_field.save();adescription.save()
    
    seAttributeType.entity_structure = eSimpleEntityAttributes; seAttributeType.save()
    atText.save();atDate.save();atForeignKey.save(); #saving again to create URIInstance via the post_save signal
    
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
    eSimpleEntityAttributes.save();eEntityStructureEntityStructureNodeApplication.save(); #saving again to create URIInstance via the post_save signal
    
    seEntityStructureNode.entity_structure = eEntityStructureEntityStructureNodeApplication; seEntityStructureNode.save()
    en1.save();en2.save();en3.save();en4.save();en5.save();en6.save();en7.save();en8.save();en9.save();en10.save();en11.save();en12.save();en13.save();en15.save();en16.save();en17.save();en18.save();en19.save()
    
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
    
    wgeneric = Workflow();wgeneric.name="Generic default workflow";wgeneric.description="";wgeneric.save()
    ws = WorkflowStatus();ws.name="Generic";ws.workflow=wgeneric;ws.description="";ws.save()
    
    
    
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws,entry_point_instance_id=seSimpleEntity.id,                                version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    # EntityInstance has no EntityStructure, I create the shallow one so that I can set EntityStructure.namespace 
    # and hence generate the URIInstance for each instance of EntityInstance
    es = ei.shallow_entity_structure()
    es.namespace = "entity"
    es.save()
    seEntityInstance.entity_structure = es
    seEntityInstance.save()
    ei.save()
    
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws,entry_point_instance_id=seAttribute.id,                                   version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws,entry_point_instance_id=seApplication.id,                                 version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws,entry_point_instance_id=seWorkflow.id,                                    version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws,entry_point_instance_id=seWorkflowStatus.id,                              version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws,entry_point_instance_id=seMethod.id,                                      version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws,entry_point_instance_id=seAttributeType.id,                               version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws,entry_point_instance_id=seWidget.id,                                      version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws,entry_point_instance_id=seEntityStructureNode.id,                         version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws,entry_point_instance_id=seEntityStructure.id,                             version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws,entry_point_instance_id=seAttributeInAMethod.id,                          version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws,entry_point_instance_id=seOrganization.id,                                version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws,entry_point_instance_id=seEntityInstance.id,                              version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eSimpleEntityAttributes,                        workflow=wgeneric,current_status=ws,entry_point_instance_id=seKnowledgeServer.id,                             version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eEntityStructureEntityStructureNodeApplication, workflow=wgeneric,current_status=ws,entry_point_instance_id=eSimpleEntityAttributes.id,                       version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eEntityStructureEntityStructureNodeApplication, workflow=wgeneric,current_status=ws,entry_point_instance_id=eEntityStructureEntityStructureNodeApplication.id,version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eEntityStructureEntityStructureNodeApplication, workflow=wgeneric,current_status=ws,entry_point_instance_id=eWorkflowStatuses.id,                             version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eEntityStructureEntityStructureNodeApplication, workflow=wgeneric,current_status=ws,entry_point_instance_id=eOrganizationKS.id,                               version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()
    ei = EntityInstance(root_id=1,owner_knowledge_server=the_koa_org_ks,entity_structure=eOrganizationKS,                                workflow=wgeneric,current_status=ws,entry_point_instance_id=the_koa_org.id,                                   version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
    ei.save();ei.root_id=ei.id;ei.save()



class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0002_auto_20150617_1440'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]

