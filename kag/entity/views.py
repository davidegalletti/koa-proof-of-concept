from django.http import HttpResponse
from entity.models import Entity
from django.shortcuts import render, get_object_or_404, redirect
from application.models import Application
from userauthorization.models import KUser, PermissionHolder

def index(request):
    return HttpResponse("Hello, world. You're at the entity index.")

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
