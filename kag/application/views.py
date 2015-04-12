# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from entity.models import SimpleEntity, Entity, EntityNode
from application.models import Method, Application
from userauthorization.models import KUser, PermissionHolder

def index(request):
    if request.user.is_authenticated():
        authenticated_user = request.user.username
    kuser_list = KUser.objects.all()
    application_list = Application.objects.order_by('name')[:5]
    e = SimpleEntity.objects.get(name="Application")
    entities = Entity.objects.filter(entry_point__entity = e)
    context = {'application_list': application_list, 'kuser_list': kuser_list, 'authenticated_user':authenticated_user, entities: entities }
    return render(request, 'application/index.html', context)

def detail(request, application_id):
    application =  get_object_or_404(Application, pk=application_id)
    entity_list = []
    initial_methods = []
    
    for wf in application.workflows.all():
        entity_list.append(wf.entity)
        for m in wf.method_set.all().filter(create_instance=1):
            initial_methods.append(m)
    # following lines makes entries unique
    entity_list = list(set(entity_list))
    initial_methods = list(set(initial_methods))
    return render(request, 'application/detail.html', {'application': application, 'entity_list': entity_list, 'initial_methods': initial_methods})

def klogin(request, username, password):
    user = authenticate(username=username, password=password)
    if user is not None:
        # the password verified for the user
        if user.is_active:
            login(request, user)
            kuser = KUser.objects.get(login = user.username)
            
            return render(request, 'application/user_detail.html', {'kuser': kuser, 'methods': kuser.permission_holder.methods.all})
        else:
            return HttpResponse("The password is valid, but the account has been disabled!")
    else:
        # the authentication system was unable to verify the username and password
        return HttpResponse("The username and password were incorrect.")
