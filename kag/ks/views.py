# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from entity import models as entity_models
from entity import views as entity_views
from xml.dom import minidom
from datetime import datetime



def simple_entity_info(request, URISimpleEntity):

    URISimpleEntity = """http://KnowledgeOrientedArchitecture.org/KS/entity/SimpleEntity/1"""
    actual_class = entity_models.SimpleEntity

    se = entity_models.SimpleEntity.retrieve(actual_class, URISimpleEntity, False)
    #TODO: trovare un modo per togliere 1 cablato e ricavare Attributes in modo più pulito
    entity_id = 1
    instance = get_object_or_404(actual_class, pk=se.id)
    e = entity_models.Entity.objects.get(pk = entity_id)
    exported_xml = "<Export EntityName=\"" + e.name + "\" EntityURI=\"" + e.URIInstance + "\" ExportDateTime=\"" + str(datetime.now()) + "\">" + instance.to_xml(e.entry_point, exported_instances = []) + "</Export>"
    xmldoc = minidom.parseString(exported_xml)
    exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
    return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")
