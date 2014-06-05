from django.http import HttpResponse
from entity.models import Entity
from django.shortcuts import render, get_object_or_404, redirect
from application.models import Application, Method
from userauthorization.models import KUser, PermissionHolder
from django.db import models
from django import forms


def index(request):
    return HttpResponse("Entity index.")

def detail(request, entity_id, application_id):
    if not request.user.is_authenticated():
        return redirect('/application/')
    else:
        entity = get_object_or_404(Entity, pk=entity_id)
        application = get_object_or_404(Application, pk=application_id)
        authenticated_user = request.user
        kuser = KUser.objects.get(login = request.user.username)
        methods = []
        for method in kuser.permission_holder.methods.all():
            try:
                method.application_set.get(id=application.id)
                methods.append(method)
            except:
                pass
    
#    entity_list = []
#    for m in application.methods.all():
#        for a in m.attributes.all():
#            entity_list.append(a.entity)
    # following line makes entries unique
#    entity_list = list(set(entity_list))
    return render(request, 'entity/detail.html', {'entity': entity, 'application': application, 'authenticated_user': authenticated_user, 'methods': methods})


def FormAlVolo(mod):
    class FAV(forms.ModelForm):
        class Meta:
            model = mod
    return FAV

def getForm(method, name="FlyModel"):
    attris = {
        '__module__': Method.__module__,
    }
    for attr in method.attributes.all():
        attris[attr.name] = models.CharField(attr.name, max_length=200, blank=True)
    try:
        cmod = type(name, (models.Model,), attris)
    except Exception as ex:
        print ex

    return FormAlVolo(cmod)



def method(request, entity_id, application_id, method_id):
    entity = get_object_or_404(Entity, pk=entity_id)
    application = get_object_or_404(Application, pk=application_id)
    method = get_object_or_404(Method, pk=method_id)
    authenticated_user = request.user

    attrib_form = getForm(method)
    return render(request, 'entity/method.html', {'entity': entity, 'application': application, 'authenticated_user': authenticated_user, 'method': method, 'form': attrib_form})
