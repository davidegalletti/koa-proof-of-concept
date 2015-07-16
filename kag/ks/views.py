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
from entity.models import EntityStructure, EntityInstance, SerializableSimpleEntity, KnowledgeServer
import kag.utils as utils
import forms as myforms 



def api_simple_entity_definition(request, base64_SimpleEntity_URIInstance, format):
    '''
    '''
    format = format.upper()
    URISimpleEntity = base64.decodestring(base64_SimpleEntity_URIInstance)
    actual_class = entity_models.SimpleEntity

    se = entity_models.SimpleEntity.retrieve(actual_class, URISimpleEntity, False)
    
    instance = get_object_or_404(actual_class, pk=se.id)
    e = entity_models.EntityStructure.objects.get(name = entity_models.EntityStructure.simple_entity_entity_structure_name)
    if format == 'JSON':
        exported_json = '{ "Export" : { "EntityStructureName" : "' + e.name + '", "EntityStructureURI" : "' + e.URIInstance + '", "ExportDateTime" : "' + str(datetime.now()) + '", ' + instance.serialize(e.entry_point, format=format, exported_instances = []) + ' } }'
        return render(request, 'entity/export.json', {'json': exported_json}, content_type="application/json")
    if format == 'XML':
        exported_xml = "<Export EntityStructureName=\"" + e.name + "\" EntityStructureURI=\"" + e.URIInstance + "\" ExportDateTime=\"" + str(datetime.now()) + "\">" + instance.serialize(e.entry_point, format=format, exported_instances = []) + "</Export>"
        xmldoc = minidom.parseString(exported_xml)
        exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
        return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")

def api_entity_instance(request, base64_EntityInstance_URIInstance, format):
    '''
        It returns the EntityInstance with the URIInstance in the parameter 
        
        parameter:
        * base64_EntityInstance_URIInstance: URIInstance of the EntityInstance base64 encoded
        
        Implementation:
        # it creates the SimpleEntity class, 
        # fetches from the DB the one with pk = EntityInstance.entry_point_instance_id
        # it runs to_xml of the SimpleEntity using EntityInstance.entity.entry_point
    '''
    format = format.upper()
    URIInstance = base64.decodestring(base64_EntityInstance_URIInstance)
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
            url: http://rootks.thekoa.org/entity/Attribute/1/xml
            url: http://rootks.thekoa.org/entity/Attribute/1/json
        
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
            this_ks = KnowledgeServer.objects.get(this_ks = True)
            instance = SerializableSimpleEntity.retrieve(actual_class, this_ks.uri() + uri_instance, False)
            if format == 'JSON':
                exported_json = '{ "Export" : { "ExportDateTime" : "' + str(datetime.now()) + '", ' + instance.serialize(format='JSON', exported_instances = []) + ' } }'
                return render(request, 'entity/export.json', {'json': exported_json}, content_type="application/json")
            if format == 'XML':
                exported_xml = "<Export ExportDateTime=\"" + str(datetime.now()) + "\">" + instance.serialize(format='XML', exported_instances = []) + "</Export>"
                xmldoc = minidom.parseString(exported_xml)
                exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
                return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")
        else:
            raise(Exception("The url '" + uri_instance + "' does not match the URIInstance format"))
    except Exception as es:
        if format == 'JSON':
            exported_json = '{ "Export" : { "ExportDateTime" : "' + str(datetime.now()) + '", "Error" : "' + str(es) + '" } }'
            return render(request, 'entity/export.json', {'json': exported_json}, content_type="application/json")
        if format == 'XML':
            exported_xml = "<Export ExportDateTime=\"" + str(datetime.now()) + "\" Error=\"" + str(es) + "\"/>"
            xmldoc = minidom.parseString(exported_xml)
            exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
            return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")

def api_entity_structures(request, format):
    '''
        parameters:
            None
        
        Implementation:
            Invoking api_entity_instances #64 with parameter "EntityStructure-EntityStructureNode-Application"
            so that I get all the Entities in a shallow export
    '''
    # Look for all EntityStructure of type "EntityStructure-EntityStructureNode-Application" ...
    entities_id = EntityStructure.objects.filter(name=EntityStructure.entity_structure_entity_structure_name).values("id")
    # Look for the only EntityInstance whose EntityStructure is *incidentally* of the above type (entity_id__in=entities_id)
    # whose instance is ov the above type entry_point_instance_id__in=entities_id
    # and it is released (there must be exactly one!
    ei = EntityInstance.objects.get(version_released=True, entry_point_instance_id__in=entities_id, entity_structure_id__in=entities_id)
    e = EntityStructure.objects.get(pk=ei.entry_point_instance_id)
    
    return api_entity_instances(request, base64.encodestring(e.URIInstance), format)

def api_entity_instances(request, base64_EntityStructure_URIInstance, format):
    '''
        http://redmine.davide.galletti.name/issues/64
        all the instances of a given structure
        
        parameter:
        * format { 'XML' | 'JSON' }
        * base64_Entity_URIInstance: URIInstance of the EntityStructure base64 encoded
        
        Implementation:
        # it fetches the EntityStructure from the DB, look for all the EntityInstance
        # of that EntityStructure; it takes the latest version of each versionset
        # and returns the list
    '''
    format = format.upper()
    URIInstance = base64.decodestring(base64_EntityStructure_URIInstance)
    e = EntityStructure.retrieve(EntityStructure, URIInstance, False)
    
    # Now I need to get all the released EntityInstance of the EntityStructure passed as a parameter
    released_entity_instances = EntityInstance.objects.filter(entity_structure = e, version_released=True)
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
        ks_url = request.POST['ks_complete_url']
        local_url = reverse ('api_entities', args=("JSON",))
        response = urllib2.urlopen(ks_url + local_url)
        entities_json = response.read()
        # fare il parse
        decoded = json.loads(entities_json)
        entities = []
        for ei in decoded['Export']['EntityInstances']:
            entity = {}
            entity['actual_instance_name'] = ei['ActualInstance']['EntityStructure']['name']
            entity['URIInstance'] = base64.encodestring(ei['ActualInstance']['EntityStructure']['URIInstance']).rstrip('\n')
            entities.append(entity)
    except Exception as es:
        pass
    cont = RequestContext(request, {'entities':entities, 'ks_url':base64.encodestring(ks_url).rstrip('\n')})
    return render_to_response('ks/ks_explorer_entities.html', context_instance=cont)


def ks_explorer_form(request):
    form = myforms.ExploreOtherKSForm()

    cont = RequestContext(request, {'form':form})
    return render_to_response('ks/ks_explorer_form.html', context_instance=cont)

def browse_entity_instance(request, ks_url, base64URIInstance, format):
    ks_url = base64.decodestring(ks_url)
    format = format.upper()
    #base64URIInstance = base64.decodestring(base64URIInstance)
    if format == 'XML':
        local_url = reverse ('api_entity_instances', args=(base64URIInstance,format))
    if format == 'JSON' or format == 'BROWSE':
        local_url = reverse ('api_entity_instances', args=(base64URIInstance,'JSON'))
    response = urllib2.urlopen(ks_url + local_url)
    entities = response.read()
    if format == 'XML':
        return render(request, 'entity/export.xml', {'xml': entities}, content_type="application/xhtml+xml")
    if format == 'JSON':
        return render(request, 'entity/export.json', {'json': entities}, content_type="application/json")
    if format == 'BROWSE':
        # fare il parse
        decoded = json.loads(entities)
        entities = []
        for ei in decoded['Export']['EntityInstances']:
            entity = {}
            actual_instance_class = ei['ActualInstance'].keys()[0]
            entity['actual_instance_name'] = ei['ActualInstance'][actual_instance_class]['name']
            entity['URIInstance'] = base64.encodestring(ei['ActualInstance'][actual_instance_class]['URIInstance']).rstrip('\n')
            entities.append(entity)
        cont = RequestContext(request, {'entities':entities})
        return render_to_response('ks/browse_entity_instance.html', context_instance=cont)
    
def home(request):
    this_ks = KnowledgeServer.objects.get(this_ks = True)
    cont = RequestContext(request, {'this_ks':this_ks})
    return render(request, 'ks/home.html', context_instance=cont)

def api_ks_info(request, base64_KS_URIInstance, format):
    '''
        http://redmine.davide.galletti.name/issues/80

        parameter:
        * format { 'XML' | 'JSON' }
        * base64_Entity_URIInstance: URIInstance of the EntityStructure base64 encoded
        
        Implementation:
        # it fetches the KS from the DB, takes its Oragnization and exports
        # it with the structure "Organization-KS" 
    '''
    format = format.upper()
    URIInstance = base64.decodestring(base64_KS_URIInstance)
    ks = KnowledgeServer.retrieve(EntityStructure, URIInstance, False)
    
    ks.organization
    
    final_ei_list = []
    # Now I need to get all the released EntityInstance of the EntityStructure passed as a parameter
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
