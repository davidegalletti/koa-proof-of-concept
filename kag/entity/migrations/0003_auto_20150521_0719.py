# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forwards_func(apps, schema_editor):
    Organization = apps.get_model("entity", "Organization")
    SimpleEntity = apps.get_model("entity", "SimpleEntity")
    AttributeType = apps.get_model("entity", "AttributeType")
    Attribute = apps.get_model("entity", "Attribute")
    EntityNode = apps.get_model("entity", "EntityNode")
    Entity = apps.get_model("entity", "Entity")
    Workflow = apps.get_model("entity", "Workflow")
    WorkflowStatus = apps.get_model("entity", "WorkflowStatus")
    EntityInstance = apps.get_model("entity", "EntityInstance")
    
    db_alias = schema_editor.connection.alias

    orgs = Organization.objects.using(db_alias).bulk_create([
        Organization(pk=1, name="Knowledge Oriented Architecture Foundation", URIInstance="http://thekoa.org/KS/entity/Organization/1", description="", ks_uri="http://thekoa.org/KS"),
    ])
    the_koa_org = orgs[0]

    se = SimpleEntity.objects.using(db_alias).bulk_create([
        SimpleEntity(id=1, name="SimpleEntity", owner_organization=the_koa_org, namespace="entity", URIInstance="http://thekoa.org/KS/entity/SimpleEntity/1", name_in_this_namespace="SimpleEntity", module="entity", description="", table_name="", id_field="id", name_field="name", description_field="description"),
        SimpleEntity(id=2,name="Attribute",owner_organization=the_koa_org,namespace="entity",URIInstance="http://thekoa.org/KS/entity/SimpleEntity/2",name_in_this_namespace="Attribute",module="entity",description="",table_name="",id_field="id",name_field="name",description_field=""),
        SimpleEntity(id=3,name="Application",owner_organization=the_koa_org,namespace="entity",URIInstance="http://thekoa.org/KS/entity/SimpleEntity/3",name_in_this_namespace="Application",module="application",description="",table_name="",id_field="id",name_field="name",description_field="description"),

        SimpleEntity(id=5, name="Workflow",owner_organization=the_koa_org,namespace="entity",URIInstance="http://thekoa.org/KS/entity/SimpleEntity/5",name_in_this_namespace="Workflow",module="entity",description="",table_name="",id_field="id",name_field="name",description_field="description"),
        SimpleEntity(id=6, name="WorkflowStatus",owner_organization=the_koa_org,namespace="entity",URIInstance="http://thekoa.org/KS/entity/SimpleEntity/6",name_in_this_namespace="WorkflowStatus",module="entity",description="",table_name="",id_field="id",name_field="name",description_field="description"),
        SimpleEntity(id=7, name="Method",owner_organization=the_koa_org,namespace="entity",URIInstance="http://thekoa.org/KS/entity/SimpleEntity/7",name_in_this_namespace="Method",module="application",description="",table_name="",id_field="id",name_field="name",description_field="description"),
        SimpleEntity(id=8, name="AttributeType",owner_organization=the_koa_org,namespace="entity",URIInstance="http://thekoa.org/KS/entity/SimpleEntity/8",name_in_this_namespace="AttributeType",module="entity",description="",table_name="",id_field="id",name_field="name",description_field=""),
        SimpleEntity(id=9, name="Widget",owner_organization=the_koa_org,namespace="entity",URIInstance="http://thekoa.org/KS/entity/SimpleEntity/9",name_in_this_namespace="Widget",module="application",description="",table_name="",id_field="id",name_field="widgetname",description_field=""),
        SimpleEntity(id=10,name="EntityNode",owner_organization=the_koa_org,namespace="entity",URIInstance="http://thekoa.org/KS/entity/SimpleEntity/10",name_in_this_namespace="EntityNode",module="entity",description="",table_name="",id_field="id",name_field="attribute",description_field=""),
        SimpleEntity(id=11,name="Entity",    owner_organization=the_koa_org,namespace="entity",URIInstance="http://thekoa.org/KS/entity/SimpleEntity/11",name_in_this_namespace="Entity",    module="entity",description="",table_name="",id_field="id",name_field="name",     description_field=""),

        SimpleEntity(id=14,name="AttributeInAMethod",owner_organization=the_koa_org,namespace="application",URIInstance="http://thekoa.org/KS/entity/SimpleEntity/14",name_in_this_namespace="AttributeInAMethod",module="application",description="",table_name="",id_field="id",name_field="name",description_field=""),
        SimpleEntity(id=15, name="Organization", owner_organization=the_koa_org, namespace="entity", URIInstance="http://thekoa.org/KS/entity/SimpleEntity/15", name_in_this_namespace="Organization", module="entity", description="", table_name="", id_field="id", name_field="name", description_field="description"),
    ])
    seSimpleEntity=se[0];seAttribute=se[1];seApplication=se[2];seWorkflow=se[3];seWorkflowStatus=se[4];seMethod=se[5];seAttributeType=se[6];seWidget=se[7];seEntityNode=se[8];seEntity=se[9];seAttributeInAMethod=se[10];seOrganization=se[11];
        
    at = AttributeType.objects.using(db_alias).bulk_create([
        AttributeType(id=1, name="Text", URIInstance="http://thekoa.org/KS/entity/AttributeType/1"),
        AttributeType(id=2, name="Date", URIInstance="http://thekoa.org/KS/entity/AttributeType/2"),
        AttributeType(id=3, name="ForeignKey", URIInstance="http://thekoa.org/KS/entity/AttributeType/3"),
    ])
    atText=at[0];atDate=at[1];atForeignKey=at[2];
    
#     SimpleEntity
    a = Attribute.objects.using(db_alias).bulk_create([
        Attribute(id=1, name="name", type=atText, simple_entity=seSimpleEntity, URIInstance="http://thekoa.org/KS/entity/Attribute/1"),
        Attribute(id=2, name="owner_organization", type=atForeignKey, simple_entity=seSimpleEntity, URIInstance="http://thekoa.org/KS/entity/Attribute/2"),
        Attribute(id=3, name="namespace", type=atText, simple_entity=seSimpleEntity, URIInstance="http://thekoa.org/KS/entity/Attribute/3"),
        Attribute(id=4, name="URIInstance", type=atText, simple_entity=seSimpleEntity, URIInstance="http://thekoa.org/KS/entity/Attribute/4"),
        Attribute(id=5, name="name_in_this_namespace", type=atText, simple_entity=seSimpleEntity, URIInstance="http://thekoa.org/KS/entity/Attribute/5"),
        Attribute(id=6, name="module", type=atText, simple_entity=seSimpleEntity, URIInstance="http://thekoa.org/KS/entity/Attribute/6"),
        Attribute(id=7, name="table_name", type=atText, simple_entity=seSimpleEntity, URIInstance="http://thekoa.org/KS/entity/Attribute/7"),
        Attribute(id=8, name="id_field", type=atText, simple_entity=seSimpleEntity, URIInstance="http://thekoa.org/KS/entity/Attribute/8"),
        Attribute(id=9, name="name_field", type=atText, simple_entity=seSimpleEntity, URIInstance="http://thekoa.org/KS/entity/Attribute/9"),
        Attribute(id=10, name="description_field", type=atText, simple_entity=seSimpleEntity, URIInstance="http://thekoa.org/KS/entity/Attribute/10"),
        Attribute(id=11, name="description", type=atText, simple_entity=seSimpleEntity, URIInstance="http://thekoa.org/KS/entity/Attribute/11"),
    ])
    aname=a[0];aowner_organization=a[1];anamespace=a[2];aURIInstance=a[3];aname_in_this_namespace=a[4];amodule=a[5];atable_name=a[6];aid_field=a[7];aname_field=a[8];adescription_field=a[9];adescription=a[10]
#     Organization
#     AttributeType
#     Attribute
#     EntityNode
#     Entity
#     Workflow
#     WorkflowStatus
#     EntityInstance

    en = EntityNode.objects.using(db_alias).bulk_create([
    # e1="SimpleEntity-attributes"     entry_point=en1
        EntityNode(id=1,   simple_entity=seSimpleEntity, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/1"),
        EntityNode(id=2,   simple_entity=seAttribute,      attribute="attribute_set", is_many=True, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/2"),
        EntityNode(id=3,   simple_entity=seAttributeType,  attribute="type", URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/3"),
    # e2="Entity-EntityNode-Application"    entry_point=en22
        EntityNode(id=4, simple_entity=seEntity, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/4"),
        EntityNode(id=5, simple_entity=seEntityNode,     attribute="entry_point", URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/5"),
        EntityNode(id=6, simple_entity=seSimpleEntity,   attribute="simple_entity", external_reference=True,URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/6"),
        EntityNode(id=7, simple_entity=seEntityNode,     attribute="child_nodes", is_many=True,URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/7"),
        EntityNode(id=8, simple_entity=seAttribute,      attribute="attribute_set", is_many=True, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/8"),
        EntityNode(id=9, simple_entity=seAttributeType,  attribute="type", external_reference=True, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/9"),
        EntityNode(id=10, simple_entity=seAttributeInAMethod,  attribute="attributeinamethod_set", is_many=True, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/10"),
        EntityNode(id=11, simple_entity=seMethod,  attribute="implementation_method", URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/11"),
        EntityNode(id=12, simple_entity=seWorkflowStatus,  attribute="initial_statuses", is_many=True, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/12"),
        EntityNode(id=13, simple_entity=seWorkflow,  attribute="workflow", URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/13"),
        EntityNode(id=14, simple_entity=seWorkflowStatus,  attribute="final_status", URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/14"),
        EntityNode(id=15, simple_entity=seApplication,  attribute="application_set", is_many=True, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/15"),
    # e3="Workflow-statuses"     entry_point=en16
        EntityNode(id=16, simple_entity=seWorkflow, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/16"),
        EntityNode(id=17, simple_entity=seWorkflowStatus, attribute="workflowstatus_set", is_many=True,URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/17"),
    ])
    en1=en[0];en2=en[1];en3=en[2];en4=en[3];en5=en[4];en6=en[5];en7=en[6];en8=en[7];en9=en[8];en10=en[9];en11=en[10];en12=en[11];en13=en[12];en14=en[13];en15=en[14];en16=en[15];en17=en[16];
    
    # eSimpleEntityAttributes
    en1.child_nodes.add(en2); en1.save()
    en2.child_nodes.add(en3); en2.save()
    eSimpleEntityAttributes=Entity(id=1,entry_point=en1,name="SimpleEntity-attributes",description="",URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/Entity/1")
    eSimpleEntityAttributes.save()

    # eEntityEntityNodeApplication
    en4.child_nodes.add(en5); en4.save()
    en5.child_nodes.add(en6); en5.child_nodes.add(en7); en5.save()
    en6.child_nodes.add(en8); en6.save()
    en7.child_nodes.add(en6); en7.child_nodes.add(en7); en7.save()
    en8.child_nodes.add(en9); en8.child_nodes.add(en10); en8.save()
    en10.child_nodes.add(en11); en10.save()
    en11.child_nodes.add(en12); en11.child_nodes.add(en13); en11.child_nodes.add(en14); en11.save()
    en13.child_nodes.add(en15); en13.save()
    eEntityEntityNodeApplication=Entity(id=2,entry_point=en4,name="Entity-EntityNode-Application",description="",URIInstance="http://thekoa.org/KS/entity/Entity/2")
    eEntityEntityNodeApplication.save()


    # eWorkflowStatuses
    en16.child_nodes.add(en17); en16.save()
    eWorkflowStatuses=Entity(id=3,entry_point=en16,name="Workflow-statuses",description="",URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/Entity/3")
    eWorkflowStatuses.save()
    
    w = Workflow.objects.using(db_alias).bulk_create([
        Workflow(id=1,name="Generic default workflow",description="",URIInstance="http://thekoa.org/KS/entity/Workflow/1"),
    ])
    wgeneric = w[0]
    ws = WorkflowStatus.objects.using(db_alias).bulk_create([
        WorkflowStatus(id=1,name="Generic",workflow=wgeneric,description="",URIInstance="http://thekoa.org/KS/entity/WorkflowStatus/1"),
    ])
    EntityInstance.objects.using(db_alias).bulk_create([
        EntityInstance(id=1,entity=eSimpleEntityAttributes,workflow=wgeneric,current_status=ws[0],entry_point_instance_id=1,version_major=0,version_minor=0,version_patch=1,URIInstance="http://thekoa.org/KS/entity/EntityInstance/1"),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0002_workflowtransition_user'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
    ]



def script_from_shell():
    from entity.models import Organization
    from entity.models import SimpleEntity, AttributeType, Attribute, EntityNode, Entity, Workflow
    from entity.models import WorkflowStatus, EntityInstance

    seSimpleEntity=SimpleEntity.objects.get(pk=1)
    seAttribute=SimpleEntity.objects.get(pk=2)
    seAttributeType=SimpleEntity.objects.get(pk=8)
    seEntity=SimpleEntity.objects.get(pk=11)
    seEntityNode=SimpleEntity.objects.get(pk=10)
    seAttributeInAMethod=SimpleEntity.objects.get(pk=14)
    seMethod=SimpleEntity.objects.get(pk=7)
    seWorkflowStatus=SimpleEntity.objects.get(pk=6)
    seWorkflow=SimpleEntity.objects.get(pk=5)
    seApplication=SimpleEntity.objects.get(pk=3)

    # e1="SimpleEntity-attributes"     entry_point=en1
    en1=EntityNode(id=1,   simple_entity=seSimpleEntity, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/1")
    en2=EntityNode(id=2,   simple_entity=seAttribute,      attribute="attribute_set", is_many=True, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/2")
    en3=EntityNode(id=3,   simple_entity=seAttributeType,  attribute="type", URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/3")
    en1.save();en2.save();en3.save();
    en1.child_nodes.add(en2); en1.save()
    en2.child_nodes.add(en3); en2.save()
    e1=Entity(id=1,entry_point=en1,name="SimpleEntity-attributes",description="",URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/Entity/1")
    e1.save()

        
    # e2="Entity-EntityNode-Application"    entry_point=en22
    en4=EntityNode(id=4, simple_entity=seEntity, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/4")
    en5=EntityNode(id=5, simple_entity=seEntityNode,     attribute="entry_point", URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/5")
    en6=EntityNode(id=6, simple_entity=seSimpleEntity,   attribute="simple_entity", external_reference=True,URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/6")
    en7=EntityNode(id=7, simple_entity=seEntityNode,     attribute="child_nodes", is_many=True,URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/7")
    en8=EntityNode(id=8, simple_entity=seAttribute,      attribute="attribute_set", is_many=True, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/8")
    en9=EntityNode(id=9, simple_entity=seAttributeType,  attribute="type", external_reference=True, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/9")
    en10=EntityNode(id=10, simple_entity=seAttributeInAMethod,  attribute="attributeinamethod_set", is_many=True, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/10")
    en11=EntityNode(id=11, simple_entity=seMethod,  attribute="implementation_method", URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/11")
    en12=EntityNode(id=12, simple_entity=seWorkflowStatus,  attribute="initial_statuses", is_many=True, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/12")
    en13=EntityNode(id=13, simple_entity=seWorkflow,  attribute="workflow", URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/13")
    en14=EntityNode(id=14, simple_entity=seWorkflowStatus,  attribute="final_status", URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/14")
    en15=EntityNode(id=15, simple_entity=seApplication,  attribute="application_set", is_many=True, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/15")


    en4.save();en5.save();en6.save();en7.save();en8.save();en9.save();en10.save();en11.save();en12.save();en13.save();en14.save();en15.save();

    en4.child_nodes.add(en5); en4.save()
    en5.child_nodes.add(en6); en5.child_nodes.add(en7); en5.save()
    en6.child_nodes.add(en8); en6.save()
    en7.child_nodes.add(en6); en7.child_nodes.add(en7); en7.save()
    en8.child_nodes.add(en9); en8.child_nodes.add(en10); en8.save()
    en10.child_nodes.add(en11); en10.save()
    en11.child_nodes.add(en12); en11.child_nodes.add(en13); en11.child_nodes.add(en14); en11.save()
    en13.child_nodes.add(en15); en13.save()

    e2=Entity(id=2,entry_point=en4,name="Entity-EntityNode-Application",description="",URIInstance="http://thekoa.org/KS/entity/Entity/2")
    e2.save()


    # e3="Workflow-statuses"     entry_point=en16
    en16=EntityNode(id=16, simple_entity=seWorkflow, URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/16")
    en17=EntityNode(id=17, simple_entity=seWorkflowStatus, attribute="workflowstatus_set", is_many=True,URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/EntityNode/17")
    en16.save();en17.save();
    en16.child_nodes.add(en17); en16.save()
    e3=Entity(id=3,entry_point=en16,name="Workflow-statuses",description="",URIInstance="http://KnowledgeOrientedArchitecture.org/KS/entity/Entity/3")
    e3.save()
