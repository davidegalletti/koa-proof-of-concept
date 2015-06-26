# -*- coding: utf-8 -*-

import base64
from datetime import datetime
import json
import urllib2
from xml.dom import minidom

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import F, Min
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext

from entity import models as entity_models
from entity.models import Entity, EntityInstance, SerializableSimpleEntity
from entity import views as entity_views
import kag.utils as utils
import forms as myforms 



def api_simple_entity_definition(request, format, base64URISimpleEntity):
    '''
    '''
    format = format.upper()
    URISimpleEntity = base64.decodestring(base64URISimpleEntity)
    actual_class = entity_models.SimpleEntity

    se = entity_models.SimpleEntity.retrieve(actual_class, URISimpleEntity, False)
    entity_id = 1
    instance = get_object_or_404(actual_class, pk=se.id)
    e = entity_models.Entity.objects.get(pk = entity_id)
    if format == 'JSON':
        exported_json = '{ "Export" : { "EntityName" : "' + e.name + '", "EntityURI" : "' + e.URIInstance + '", "ExportDateTime" : "' + str(datetime.now()) + '", ' + instance.serialize(e.entry_point, format=format, exported_instances = []) + ' } }'
        return render(request, 'entity/export.json', {'json': exported_json}, content_type="application/json")
    if format == 'XML':
        exported_xml = "<Export EntityName=\"" + e.name + "\" EntityURI=\"" + e.URIInstance + "\" ExportDateTime=\"" + str(datetime.now()) + "\">" + instance.serialize(e.entry_point, format=format, exported_instances = []) + "</Export>"
        xmldoc = minidom.parseString(exported_xml)
        exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
        return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")

def api_entity_instance(request, format, base64URIInstance):
    '''
        It returns the EntityInstance with the URIInstance in the parameter 
        
        parameter:
        * base64URIInstance: URIInstance of the EntityInstance base64 encoded
        
        Implementation:
        # it creates the SimpleEntity class, 
        # fetches from the DB the one with pk = EntityInstance.entry_point_instance_id
        # it runs to_xml of the SimpleEntity using EntityInstance.entity.entry_point
    '''
    format = format.upper()
    URIInstance = base64.decodestring(base64URIInstance)
    ei = EntityInstance.retrieve(EntityInstance, URIInstance, False)

    if format == 'JSON':
        exported_json = '{ "Export" : { "ExportDateTime" : "' + str(datetime.now()) + '", "EntityInstance" : ' + ei.serialize_with_simple_entity(format = format) + ' } }'
        return render(request, 'entity/export.json', {'json': exported_json}, content_type="application/json")
    if format == 'XML':
        exported_xml = "<Export ExportDateTime=\"" + str(datetime.now()) + "\">" + ei.serialize_with_simple_entity(format = format) + "</Export>"
        xmldoc = minidom.parseString(exported_xml)
        exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
        return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")


def api_catch_all(request, uri_instance):
    '''
        parameters:
            url: http://rootks.thekoa.org/entity/Attribute/1
        
        Implementation:
            I do something only if it is a URIInstance in my database; otherwise I return a not found message
            If there is a trailing string for the format I use it, otherwise I apply the default xml
            The trailing string can be "/xml", "/xml/", "/json", "/json/" where each character can 
            be either upper or lower case   
    '''
    # I search for a format string, a URIInstance has no trailing slash
    format = 'XML' #default
    if uri_instance[-1:] == "/":
        #I remove a trailing slash
        uri_instance = uri_instance[:-1]
    if uri_instance[-3:].lower() == "xml":
        uri_instance = uri_instance[:-4]
    if uri_instance[-4:].lower() == "json":
        format = 'JSON'
        uri_instance = uri_instance[:-5]
        
    try:
        split_path = uri_instance.split('/')
        if len(split_path) == 3:
            module_name = split_path[0]
            simple_entity_name = split_path[1]
            actual_class = utils.load_class(module_name + ".models", simple_entity_name)
            instance = SerializableSimpleEntity.retrieve(actual_class, settings.THIS_KS_URI + uri_instance, False)
            if format == 'JSON':
                exported_json = '{ "Export" : { "ExportDateTime" : "' + str(datetime.now()) + '", ' + instance.serialize(format='JSON', exported_instances = []) + ' } }'
                return render(request, 'entity/export.json', {'json': exported_json}, content_type="application/json")
            if format == 'XML':
                exported_xml = "<Export ExportDateTime=\"" + str(datetime.now()) + "\">" + instance.serialize(format='XML', exported_instances = []) + "</Export>"
                xmldoc = minidom.parseString(exported_xml)
                exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
                return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")
        else:
            raise(Exception('The url "' + uri_instance + '" does not match the URIInstance format'))
    except Exception as es:
        if format == 'JSON':
            exported_json = '{ "Export" : { "ExportDateTime" : "' + str(datetime.now()) + '", "Error" : "' + str(es) + '" } }'
            return render(request, 'entity/export.json', {'json': exported_json}, content_type="application/json")
        if format == 'XML':
            exported_xml = "<Export ExportDateTime=\"" + str(datetime.now()) + "\" Error=\"" + str(es) + "\"/>"
            xmldoc = minidom.parseString(exported_xml)
            exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
            return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")

def api_entities(request, format):
    '''
        parameters:
            None
        
        Implementation:
            Invoking api_entity_instances with parameter "Entity-EntityNode-Application"
            so that I get all the Entities in a shallow export
    '''
    # TODO: devo trovare lo URIInstance di "Entity-EntityNode-Application" cioè di un Entity con entry_point.simple_entity Entity
    # che sia anche released
    entities_id = Entity.objects.filter(name="Entity-EntityNode-Application").values("id")
    ei = EntityInstance.objects.get(version_released=True, pk__in=entities_id)
    e = Entity.objects.get(pk=ei.entry_point_instance_id)
    
    return api_entity_instances(request, format, base64.encodestring(e.URIInstance))

def api_entity_instances(request, format, base64URIInstance):
    '''
        http://redmine.davide.galletti.name/issues/64

        parameter:
        * format { 'XML' | 'JSON' }
        * base64URIInstance: URIInstance of the Entity base64 encoded
        
        Implementation:
        # it fetches the Entity from the DB, look for all the EntityInstance
        # of that Entity; it takes the latest version of each versionset
        # it returns the list xml encoded
    '''
    format = format.upper()
    URIInstance = base64.decodestring(base64URIInstance)
    e = Entity.retrieve(Entity, URIInstance, False)
    
    final_ei_list = []
    # Now I need to get all the released EntityInstance of the Entity passed as a parameter
    released_entity_instances = EntityInstance.objects.filter(entity = e, version_released=True)
    serialized = ""
    comma = ""
    for ei in released_entity_instances:
        if format == 'JSON':
            serialized += comma
        serialized += ei.serialize_with_simple_entity(format = format, force_external_reference=True)
        comma = ", "
    if format == 'XML':
        exported_xml = "<Export ExportDateTime=\"" + str(datetime.now()) + "\"><EntityInstances>" + serialized + "</EntityInstances></Export>"
        xmldoc = minidom.parseString(exported_xml)
        exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
        return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")
    if format == 'JSON':
        exported_json = '{ "Export" : { "ExportDateTime" : "' + str(datetime.now()) + '", "EntityInstances" : [' + serialized + '] } }'
        return render(request, 'entity/export.json', {'json': exported_json}, content_type="application/json")

def ks_explorer(request):
    try:
        try:
            ks_url = request.POST['ks_complete_url']
        except:
            ks_url = "http://127.0.0.1:8000"
        local_url = reverse ('api_entities', args=("JSON",))
        response = urllib2.urlopen(ks_url + local_url)
        entities_json = response.read()
        # fare il parse
        decoded = json.loads(entities_json)
        entities = []
        for ei in decoded['Export']['EntityInstances']:
            entity = {}
            entity['name'] = ei['ActualInstance']['Entity']['name']
            print(ei['ActualInstance']['Entity']['name'])
            entities.append(entity)
    except Exception as es:
        pass
    cont = RequestContext(request, {'entities':entities})
    return render_to_response('ks_explorer_entities.html', context_instance=cont)


def ks_explorer_form(request):
    form = myforms.ExploreOtherKSForm()
#     else:
#         form = myforms.ExploreOtherKSForm(request.POST)
#         if form.is_valid():
#             
#             ks_url = form.cleaned_data['ks_complete_url'].strip()
#             return HttpResponseRedirect(reverse ('ks_explorer', args=(base64.encodestring(ks_url),)))

    cont = RequestContext(request, {'form':form})
    return render_to_response('ks_explorer_form.html', context_instance=cont)






