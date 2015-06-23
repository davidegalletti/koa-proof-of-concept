# -*- coding: utf-8 -*-

from django.db.models import F, Min
from django.shortcuts import render, get_object_or_404
from entity import models as entity_models
from entity.models import Entity, EntityInstance
from entity import views as entity_views
from xml.dom import minidom
from datetime import datetime
import base64
import kag.utils as utils



def api_simple_entity_definition(request, base64URISimpleEntity):
    '''
    '''
    URISimpleEntity = base64.decodestring(base64URISimpleEntity)
    actual_class = entity_models.SimpleEntity

    se = entity_models.SimpleEntity.retrieve(actual_class, URISimpleEntity, False)
    entity_id = 1
    instance = get_object_or_404(actual_class, pk=se.id)
    e = entity_models.Entity.objects.get(pk = entity_id)
    exported_xml = "<Export EntityName=\"" + e.name + "\" EntityURI=\"" + e.URIInstance + "\" ExportDateTime=\"" + str(datetime.now()) + "\">" + instance.to_xml(e.entry_point, exported_instances = []) + "</Export>"
    xmldoc = minidom.parseString(exported_xml)
    exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
    return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")

def api_entity_instance(request, base64URIInstance):
    '''
        parameter:
        * base64URIInstance: URIInstance of the EntityInstance base64 encoded
        
        Implementation:
        # it creates the SimpleEntity class, 
        # fetches from the DB the one with pk = EntityInstance.entry_point_instance_id
        # it runs to_xml of the SimpleEntity using EntityInstance.entity.entry_point
    '''
    URIInstance = base64.decodestring(base64URIInstance)
    ei = EntityInstance.retrieve(EntityInstance, URIInstance, False)

    exported_xml = "<Export ExportDateTime=\"" + str(datetime.now()) + "\">" + ei.serialize() + "</Export>"
    xmldoc = minidom.parseString(exported_xml)
    exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
    return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")


def api_entities(request):
    '''
        parameters:
            None
        
        Implementation:
            Invoking api_entity_instances with parameter "Entity-EntityNode-Application"
            so that I get all the Entities in a shallow export
    '''
    # devo trovare lo URIInstance di "Entity-EntityNode-Application" cioè di un Entity con entry_point.simple_entity Entity
    # che sia anche released
    entities_id = Entity.objects.filter(name="Entity-EntityNode-Application").values("id")
    ei = EntityInstance.objects.get(version_released=True, pk__in=entities_id)
    e = Entity.objects.get(pk=ei.entry_point_instance_id)
    
    return api_entity_instances(request, base64.encodestring(e.URIInstance))

def api_entity_instances(request, base64URIInstance):
    '''
        http://redmine.davide.galletti.name/issues/64
        parameter:
        * base64URIInstance: URIInstance of the Entity base64 encoded
        
        Implementation:
        # it fetches the Entity from the DB, look for all the EntityInstance
        # of that Entity; it takes the latest version of each versionset
        # it returns the list xml encoded
    '''
    URIInstance = base64.decodestring(base64URIInstance)
    e = Entity.retrieve(Entity, URIInstance, False)
    
    final_ei_list = []
    # Now I need to get all the released EntityInstance of the Entity passed as a parameter
    released_entity_instances = EntityInstance.objects.filter(entity = e, version_released=True)
    xml = ""
    for ei in released_entity_instances:
        xml += ei.serialize(force_external_reference=True)

    exported_xml = "<Export ExportDateTime=\"" + str(datetime.now()) + "\"><EntityInstances>" + xml + "</EntityInstances></Export>"
    xmldoc = minidom.parseString(exported_xml)
    exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
    return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")
