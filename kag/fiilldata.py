#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'david'

from django.contrib.auth.models import User
from userauthorization.models import KUser, PermissionHolder
from application.models import Application, Method, Widget

from entity.models import SimpleEntity, Attribute, WorkflowStatus, Workflow, AttributeType, EntityStructure, EntityStructureNode, EntityInstance, Organization






# # creiamo un'applicazione, con due metodi
ks = Application(name="Knowledge server", description="The prototype of the knowledge server")
ks.save()
# 
ws = WorkflowStatus.objects.get(pk=1)
w = Workflow.objects.get(pk=1)
m1 = Method(name='Foo: a method of ks', description='It does absolutely nothing', final_status=ws, workflow=w)
m1.save()
# ks.methods.add(m1)
# ks.save()
# e1 = SimpleEntity(name='foo entity for ks', version=1)
# e1.save()
# at = AttributeType(name="Text")
# at.save()
# attr1 = Attribute(name='foo attr', entity=e1, type=at)
# attr1.save()
# m1.attributes.add(attr1)
# m1.save()
# 
# 
# bt = Application(name="Bug tracking system", description="Yet another bug tracking system")
# bt.save()
# 
# create_bug = Method(name='Create a bug', description='It creates a bug', create_instance = True, final_status=ws, workflow=w)
# create_bug.save()
# resolve_bug = Method(name='Resolve a bug', description='It resolves a bug', final_status=ws, workflow=w)
# resolve_bug.save()
# # aggiungiamo i metodi all'applicazione
# bt.methods.add(create_bug)
# bt.methods.add(resolve_bug)
# bt.save()
# # creiamo un'entità con un attributo
# bug = SimpleEntity(name='bug', version=1)
# bug.save()
# attr1 = Attribute(name='status', entity=bug, type=at)
# attr1.save()
# at2 = AttributeType(name="Date")
# at2.save()
# attr2 = Attribute(name='created', entity=bug, type=at2)
# attr2.save()
# # aggiungiamo gli attributi ai metodi
# create_bug.attributes.add(attr1)
# create_bug.attributes.add(attr2)
# create_bug.save()
# #aggiungiamo due attributi all'entità "SimpleEntity"
# e = SimpleEntity.objects.get(name="SimpleEntity")
# attr1 = Attribute(name='Name', entity=e, type=at)
# attr1.save()
# attr2 = Attribute(name='Version', entity=e, type=at)
# attr2.save()


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




create_bug =Method.objects.get(name="Create")
add_note_bug =Method.objects.get(name="Add a note")

# assegnamo dei permessi del nostro modello
sara.permission_holder.methods.add(create_bug)
sara.permission_holder.methods.add(add_note_bug)
sara.permission_holder.save()
davide.permission_holder.methods.add(add_note_bug)
davide.permission_holder.save()



ei = EntityInstance()
ei.owner_organization = Organization.objects.get(pk=1)
ei.entity = EntityStructure.objects.get(pk=1)
ei.entry_point_instance_id = 1
ei.workflow = w
ei.current_status = ws
ei.root = self
ei.set_version()
ei.version_description = "Initial version"
ei.version_released = True
ei.save()
ei.URIInstance = "http://rootks.thekoa.org/entity/EntityInstance/1"
ei.save()
    