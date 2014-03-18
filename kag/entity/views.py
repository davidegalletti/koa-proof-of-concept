from django.http import HttpResponse
from entity.models import Entity
from django.shortcuts import render, get_object_or_404

def index(request):
    return HttpResponse("Hello, world. You're at the entity index.")

def detail(request, entity_id):
    entity =  get_object_or_404(Entity, pk=entity_id)
#    entity_list = []
#    for m in application.methods.all():
#        for a in m.attributes.all():
#            entity_list.append(a.entity)
    # following line makes entries unique
#    entity_list = list(set(entity_list))
    return render(request, 'entity/detail.html', {'entity': entity})


