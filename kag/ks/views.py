# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from entity import models as entity_models
from entity.models import EntityInstance
from entity import views as entity_views
from xml.dom import minidom
from datetime import datetime
import base64
import kag.utils as utils



def api_simple_entity_info(request, base64URISimpleEntity):
    '''
    '''
    URISimpleEntity = base64.decodestring(base64URISimpleEntity)
    actual_class = entity_models.SimpleEntity

    se = entity_models.SimpleEntity.retrieve(actual_class, URISimpleEntity, False)
    #TODO: trovare un modo per togliere 1 cablato e ricavare l'entity SimpleEntity-Attributes in modo più pulito
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
    
    se = ei.entity.entry_point.simple_entity
    actual_class = utils.load_class(se.module + ".models", se.name)
    instance = actual_class.objects.get(pk=ei.entry_point_instance_id)
    
    exported_xml = "<Export EntityName=\"" + ei.entity.name + "\" EntityInstanceURI=\"" + ei.URIInstance + "\" ExportDateTime=\"" + str(datetime.now()) + "\">" + instance.to_xml(ei.entity.entry_point, exported_instances = []) + "</Export>"
    xmldoc = minidom.parseString(exported_xml)
    exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
    return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")
