#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'david'

from application.models import Application, Method
from entity.models import Entity, Attribute, WorkflowStatus, Workflow, AttributeType, EntityTree, EntityTreeNode
from django.contrib.auth.models import User
from userauthorization.models import KUser, PermissionHolder



# wf = Workflow(name= "Default minimal workflow", description= "")
# wf.save()
# ws1 = WorkflowStatus(name = "Initial", description= "", workflow = wf)
# ws1.save()
# ws2 = WorkflowStatus(name = "Final", description= "", workflow = wf)
# ws1.save()
# e1 = Entity(name= "Entity", app= "entity", description= "", table_name= "", id_field= "id", name_field= "name", description_field= "description", version= 1, version_released= 1, workflow= wf)
# e1.save()
# e2 = Entity(name= "Attribute", app= "entity", description= "", table_name= "", id_field= "id", name_field= "name", description_field= "", version= 1, version_released= 1)
# e2.save()
# e3 = Entity(name= "Application", app= "application", description= "", table_name= "", id_field= "id", name_field= "name", description_field= "description", version= 1, version_released= 1, workflow= wf)
# e3.save()
# e4 = Entity(name= "Method", app= "application", description= "", table_name= "", id_field= "id", name_field= "name", description_field= "description", version= 1, version_released= 1)
# e4.save()
# e5 = Entity(name= "Workflow", app= "entity", description= "", table_name= "", id_field= "id", name_field= "name", description_field= "description", version= 1, version_released= 1, workflow= wf)
# e5.save()
# e6 = Entity(name= "WorkflowStatus", app= "entity", description= "", table_name= "", id_field= "id", name_field= "name", description_field= "description", version= 1, version_released= 1)
# e6.save()
# e7 = Entity(name= "Method", app= "application", description= "", table_name= "", id_field= "id", name_field= "name", description_field= "description", version= 1, version_released= 1)
# e7.save()
# e8 = Entity(name= "AttributeType", app= "entity", description= "", table_name= "", id_field= "id", name_field= "name", description_field= "", version= 1, version_released= 1)
# e8.save()
# e9 = Entity(name= "Widget", app= "application", description= "", table_name= "", id_field= "id", name_field= "widgetname", description_field= "", version= 1, version_released= 1)
# e9.save()
# 
# etn11 = EntityTreeNode(entity = e9, attribute = "widgets")
# etn11.child_nodes = []
# etn11.save()
# etn10 = EntityTreeNode(entity = e8, attribute = "type")
# etn10.child_nodes = []
# etn10.child_nodes.add(etn11)
# etn10.save()
# etn9 = EntityTreeNode(entity = e8, attribute = "type")
# etn9.child_nodes = []
# etn9.save()
# etn8 = EntityTreeNode(entity = e3, attribute = "")
# etn8.save()
# etn7 = EntityTreeNode(entity = e7, attribute = "method_set")
# etn8.child_nodes = []
# etn7.child_nodes.add(etn8)
# etn7.child_nodes = []
# etn7.save()
# etn6 = EntityTreeNode(entity = e6, attribute = "workflow_status_set")
# etn6.child_nodes = []
# etn6.save()
# etn5 = EntityTreeNode(entity = e5, attribute = "workflow")
# etn5.child_nodes = []
# etn5.child_nodes.add(etn6)
# etn5.child_nodes.add(etn7)
# etn5.save()
# etn4 = EntityTreeNode(entity = e2, attribute = "attribute_set")
# etn4.child_nodes = []
# etn4.child_nodes.add(etn10)
# etn4.save()
# etn3 = EntityTreeNode(entity = e1, attribute = "")
# etn3.child_nodes = []
# etn3.child_nodes.add(etn4)
# etn3.child_nodes.add(etn5)
# etn3.save()
# etn2 = EntityTreeNode(entity = e2, attribute = "attribute_set")
# etn2.child_nodes = []
# etn2.child_nodes.add(etn9)
# etn2.save()
# etn1 = EntityTreeNode(entity = e1)
# etn1.child_nodes = []
# etn1.child_nodes.add(etn2)
# etn1.save()
# 
# et1 = EntityTree(name = "Entity-attributes", entry_point = etn1)
# et1.save()
# et2 = EntityTree(name = "Entity-...-Application", entry_point = etn3)
# et2.save()







# creiamo un'applicazione, con due metodi
ks = Application(name="Knowledge server", description="The prototype of the knowledge server")
ks.save()

ws = WorkflowStatus.objects.get(pk=2)
w = Workflow.objects.get(pk=1)
m1 = Method(name='Foo: a method of ks', description='It does absolutely nothing', final_status=ws, workflow=w)
m1.save()
ks.methods.add(m1)
ks.save()
e1 = Entity(name='foo entity for ks', version=1)
e1.save()
at = AttributeType(name="Text")
at.save()
attr1 = Attribute(name='foo attr', entity=e1, type=at)
attr1.save()
m1.attributes.add(attr1)
m1.save()


bt = Application(name="Bug tracking system", description="Yet another bug tracking system")
bt.save()

create_bug = Method(name='Create a bug', description='It creates a bug', create_instance = True, final_status=ws, workflow=w)
create_bug.save()
resolve_bug = Method(name='Resolve a bug', description='It resolves a bug', final_status=ws, workflow=w)
resolve_bug.save()
# aggiungiamo i metodi all'applicazione
bt.methods.add(create_bug)
bt.methods.add(resolve_bug)
bt.save()
# creiamo un'entità con un attributo
bug = Entity(name='bug', version=1)
bug.save()
attr1 = Attribute(name='status', entity=bug, type=at)
attr1.save()
at2 = AttributeType(name="Date")
at2.save()
attr2 = Attribute(name='created', entity=bug, type=at2)
attr2.save()
# aggiungiamo gli attributi ai metodi
create_bug.attributes.add(attr1)
create_bug.attributes.add(attr2)
create_bug.save()
#aggiungiamo due attributi all'entità "Entity"
e = Entity.objects.get(name="Entity")
attr1 = Attribute(name='Name', entity=e, type=at)
attr1.save()
attr2 = Attribute(name='Version', entity=e, type=at)
attr2.save()


# creiamo 2 utenti su Django
dj_davide = User.objects.create_user('davide', 'davide.galletti@gmail.com', 'davide')
dj_sara = User.objects.create_user('sara', 'sara@davide.galletti.name', 'sara')

# creiamo 2 utenti su kag
ph1 = PermissionHolder()
ph1.save()
davide = KUser(name='Davide', surname='Galletti', login='davide', password='davide', permission_holder=ph1)
davide.save()
ph2 = PermissionHolder()
ph2.save()
sara = KUser(name='Sara', surname='Galletti', login='sara', password='sara', permission_holder=ph2)
sara.save()
# assegnamo dei permessi del nostro modello
sara.permission_holder.methods.add(create_bug)
sara.permission_holder.methods.add(resolve_bug)
sara.permission_holder.save()
davide.permission_holder.methods.add(resolve_bug)
davide.permission_holder.save()



