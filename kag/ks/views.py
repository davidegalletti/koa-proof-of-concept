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
            this_ks = KnowledgeServer.this_knowledge_server()
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
            so that I get all the EntitieStructures in this_ks in a shallow export
    '''
    # Look for all EntityStructure of type "EntityStructure-EntityStructureNode-Application" ...
    entities_id = EntityStructure.objects.filter(name=EntityStructure.entity_structure_entity_structure_name).values("id")
    # Look for the only EntityInstance whose EntityStructure is *incidentally* of the above type (entity_id__in=entities_id)
    # whose instance is ov the above type entry_point_instance_id__in=entities_id
    # and it is released (there must be exactly one!
    ei = EntityInstance.objects.get(version_released=True, entry_point_instance_id__in=entities_id, entity_structure_id__in=entities_id)
    e = EntityStructure.objects.get(pk=ei.entry_point_instance_id)
    
    return api_entity_instances(request, base64.encodestring(e.URIInstance), format)


def api_entity_instance_info(request, base64_EntityInstance_URIInstance, format):
    '''
        #52 
        
        Parameters:
        * format { 'XML' | 'JSON' | 'HTML' = 'BROWSE' }
        * base64_EntityInstance_URIInstance: URIInstance of the EntityInstance base64 encoded
        
        Implementation:
        it fetches the EntityInstance, then the list of all that share the same root
        it returns EntityInstance.serialize_with_simple_entity(format) and for each on the above list:
            the URIInstance of the ErtityInstance
            the version status {working | released | obsolete}
            the version number (e.g. 0.1.0)
            the version date
            the version description
            other version metadata

    '''
    format = format.upper()
    URIInstance = base64.decodestring(base64_EntityInstance_URIInstance)
    entity_instance = EntityInstance.retrieve(EntityInstance, URIInstance, False)
    all_versions = EntityInstance.objects.filter(root = entity_instance.root)
    all_versions_serialized = ""
    comma = ""
    if format != 'HTML' and format != 'BROWSE':
        for v in all_versions:
            if format == 'JSON':
                all_versions_serialized += comma
            all_versions_serialized += v.serialize_with_simple_entity(format = format, force_external_reference=True)
            comma = ", "
    if format == 'XML':
        exported_xml = "<Export ExportDateTime=\"" + str(datetime.now()) + "\"><EntityInstance>" + entity_instance.serialize_with_simple_entity(format = format, force_external_reference=True) + "</EntityInstance><Versions>" + all_versions_serialized + "</Versions></Export>"
        xmldoc = minidom.parseString(exported_xml)
        exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
        return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")
    if format == 'JSON':
        exported_json = '{ "Export" : { "ExportDateTime" : "' + str(datetime.now()) + '", "EntityInstance" : ' + entity_instance.serialize_with_simple_entity(format = format, force_external_reference=True) + ', "Versions" : [' + all_versions_serialized + '] } }'
        return render(request, 'entity/export.json', {'json': exported_json}, content_type="application/json")
    if format == 'HTML' or format == 'BROWSE':
        instance = entity_instance.get_instance()
        all_versions_with_instances = []
        for v in all_versions:
            version_with_instance = {}
            version_with_instance['entity_instance'] = v
            version_with_instance['simple_entity'] = v.get_instance()
            all_versions_with_instances.append(version_with_instance)
        cont = RequestContext(request, {'base64_EntityInstance_URIInstance': base64_EntityInstance_URIInstance, 'entity_instance': entity_instance, 'all_versions_with_instances': all_versions_with_instances, 'ks': entity_instance.owner_knowledge_server, 'instance': instance})
        return render_to_response('ks/api_entity_instance_info.html', context_instance=cont)
    
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
        ks_url = base64.decodestring(request.GET['ks_complete_url'])
    except:
        ks_url = request.POST['ks_complete_url']
    try:
        # info on the remote ks
        local_url = reverse ('api_ks_info', args=("JSON",))
        response = urllib2.urlopen(ks_url + local_url)
        ks_info_json_stream = response.read()
        # parsing json
        ks_info_json = json.loads(ks_info_json_stream)
        organization = ks_info_json['Export']['Organization']
        for ks in ks_info_json['Export']['Organization']['knowledgeserver_set']:
            if ks['this_ks'] == 'True':
                external_ks = ks
            
        # info about structures on the remote ks
        local_url = reverse ('api_entity_structures', args=("JSON",))
        response = urllib2.urlopen(ks_url + local_url)
        entities_json = response.read()
        # parsing json
        decoded = json.loads(entities_json)
        entities = []
        for ei in decoded['Export']['EntityInstances']:
            entity = {}
            entity['actual_instance_name'] = ei['ActualInstance']['EntityStructure']['name']
            entity['URIInstance'] = base64.encodestring(ei['ActualInstance']['EntityStructure']['URIInstance']).rstrip('\n')
            entities.append(entity)
    except Exception as es:
        pass #TODO: view.ks_explorer manage exception 
    cont = RequestContext(request, {'entities':entities, 'organization': organization, 'external_ks': external_ks, 'ks_url':base64.encodestring(ks_url).rstrip('\n')})
    return render_to_response('ks/ks_explorer_entities.html', context_instance=cont)


def ks_explorer_form(request):
    form = myforms.ExploreOtherKSForm()

    cont = RequestContext(request, {'form':form})
    return render_to_response('ks/ks_explorer_form.html', context_instance=cont)

def browse_entity_instance(request, ks_url, base64URIInstance, format):
    ks_url = base64.decodestring(ks_url)
    format = format.upper()

    # info on the remote ks{{  }}
    local_url = reverse ('api_ks_info', args=("JSON",))
    response = urllib2.urlopen(ks_url + local_url)
    ks_info_json_stream = response.read()
    # parsing json
    ks_info_json = json.loads(ks_info_json_stream)
    organization = ks_info_json['Export']['Organization']
    for ks in ks_info_json['Export']['Organization']['knowledgeserver_set']:
        if ks['this_ks'] == 'True':
            external_ks = ks

    #info on the EntityStructure
    response = urllib2.urlopen(base64.decodestring(base64URIInstance) + "/json")
    es_info_json_stream = response.read()
    # parsing json
    es_info_json = json.loads(es_info_json_stream)
    
    
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
            entity['base64URIInstance'] = base64.encodestring(ei['URIInstance']).rstrip('\n')
            entity['URIInstance'] = ei['URIInstance']
            entities.append(entity)
        cont = RequestContext(request, {'entities':entities, 'organization': organization, 'external_ks': external_ks, 'es_info_json': es_info_json})
        return render_to_response('ks/browse_entity_instance.html', context_instance=cont)
    
def home(request):
    this_ks = KnowledgeServer.this_knowledge_server()
    cont = RequestContext(request, {'this_ks':this_ks, 'this_ks_base64_url':this_ks.uri(True)})
    return render(request, 'ks/home.html', context_instance=cont)

def api_ks_info(request, format):
    '''
        http://redmine.davide.galletti.name/issues/80

        parameter:
        * format { 'XML' | 'JSON' }
        
        Implementation:
          it fetches this KS from the DB, takes its Organization and exports
          it with the structure "Organization-KS" 
    '''
    format = format.upper()
    this_ks = KnowledgeServer.this_knowledge_server()    
    es = entity_models.EntityStructure.objects.get(name = entity_models.EntityStructure.organization_entity_structure_name)
    
    if format == 'XML':
        exported_xml = "<Export EntityStructureName=\"" + es.name + "\" EntityStructureURI=\"" + es.URIInstance + "\" ExportDateTime=\"" + str(datetime.now()) + "\">" + this_ks.organization.serialize(es.entry_point, exported_instances = []) + "</Export>"
        xmldoc = minidom.parseString(exported_xml)
        exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
        return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")
    if format == 'JSON':
        exported_json = '{ "Export" : { "EntityStructureName" : "' + es.name + '", "EntityStructureURI" : "' + es.URIInstance + '", "ExportDateTime" : "' + str(datetime.now()) + '", ' + this_ks.organization.serialize(es.entry_point, format=format, exported_instances = []) + ' } }'
        return render(request, 'entity/export.json', {'json': exported_json}, content_type="application/json")



def api_export_instance(request, base64_EntityInstance_URIInstance, format):
    '''
        #110 
        
        Parameters:
        * format { 'XML' | 'JSON' | 'HTML' = 'BROWSE' }
        * base64_EntityInstance_URIInstance: URIInstance of the EntityInstance base64 encoded
        
        Implementation:
        it fetches the EntityInstance, then the SimpleEntity
        it returns SimpleEntity.serialize according to the EntityStructure and the format

    '''
    format = format.upper()
    URIInstance = base64.decodestring(base64_EntityInstance_URIInstance)
    entity_instance = EntityInstance.retrieve(EntityInstance, URIInstance, False)
    simple_entity = entity_instance.get_instance()

    if format == 'XML':
        exported_xml = "<Export ExportDateTime=\"" + str(datetime.now()) + "\">" + simple_entity.serialize(etn = entity_instance.entity_structure.entry_point, exported_instances = [], format = format) + "</Export>"
        xmldoc = minidom.parseString(exported_xml)
        exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
        return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")
    if format == 'JSON' or format == 'HTML' or format == 'BROWSE':
        exported_json = '{ "Export" : { "ExportDateTime" : "' + str(datetime.now()) + '", ' + simple_entity.serialize(etn = entity_instance.entity_structure.entry_point, exported_instances = [], format = "JSON") + ' } }'
        if format == 'JSON':
            return render(request, 'entity/export.json', {'json': exported_json}, content_type="application/json")
        else:
            cont = RequestContext(request, {'etn': entity_instance.entity_structure.entry_point, 'base64_EntityInstance_URIInstance': base64_EntityInstance_URIInstance, 'entity_instance': entity_instance, 'exported_json': exported_json, 'simple_entity': simple_entity})
            return render_to_response('ks/api_export_instance.html', context_instance=cont)
    
def api_subscribe(request, base64_URIInstance, base64_URL):
    '''
        #35 
        parameters:
        base64_URIInstance the base64 encoded URIInstance to which I want to subscribe
        base64_URL the URL this KS has to invoke to notify
    '''
    
    
def api_notify(request, base64_URIInstance):
    '''
        #35 
        parameters:
        base64_URIInstance the base64 encoded URIInstance to which I want to subscribe
        base64_URL the URL this KS has to invoke to notify
    '''
    
    
