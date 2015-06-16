# -*- coding: utf-8 -*-

from django.db.models import F, Max
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


def api_entity_instances(request, base64URIInstance):
    '''
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
    # Now I need to get all the EntityInstance; I start getting all the roots and then loop on them
    root_entity_instances = EntityInstance.objects.filter(root__id = F("id"))
    # I loop and select the latest 
    for rei in root_entity_instances:
        final_ei_list.append(EntityInstance.get_latest(rei))
    xml = ""     
    for ei in final_ei_list:
        xml += ei.serialize(force_external_reference=True)

    exported_xml = "<Export ExportDateTime=\"" + str(datetime.now()) + "\"><EntityInstances>" + xml + "</EntityInstances></Export>"
    xmldoc = minidom.parseString(exported_xml)
    exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
    return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")
