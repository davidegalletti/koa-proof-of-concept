#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'david'

from application.models import Application, Method
from entity.models import Entity, Attribute
from django.contrib.auth.models import User
from userauthorization.models import KUser, PermissionHolder

# creiamo un'applicazione, con due metodi
ks = Application(name="Knowledge server", description="The prototype of the knowledge server")
ks.save()

m1 = Method(name='Foo: a method of ks', description='It does absolutely nothing')
m1.save()
ks.methods.add(m1)
ks.save()
e1 = Entity(name='foo entity for ks', version=1)
e1.save()
attr1 = Attribute(name='foo attr', entity=e1)
attr1.save()
m1.attributes.add(attr1)
m1.save()


bt = Application(name="Bug tracking system", description="Yet another bug tracking system")
bt.save()

create_bug = Method(name='Create a bug', description='It creates a bug')
create_bug.save()
resolve_bug = Method(name='Resolve a bug', description='It resolves a bug')
resolve_bug.save()
# aggiungiamo i metodi all'applicazione
bt.methods.add(create_bug)
bt.save()
bt.methods.add(resolve_bug)
# creiamo un'entità con un attributo
bug = Entity(name='bug', version=1)
bug.save()
attr1 = Attribute(name='status', entity=bug)
attr1.save()
attr2 = Attribute(name='created', entity=bug)
attr2.save()
# aggiungiamo gli attributi ai metodi
create_bug.attributes.add(attr1)
create_bug.attributes.add(attr2)
create_bug.save()
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