# -*- coding: utf-8 -*-

import base64
from datetime import datetime
import json
import urllib2
from xml.dom import minidom

from django.db import transaction
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import F, Min
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext

from entity.models import SimpleEntity, EntityStructure, EntityInstance, SerializableSimpleEntity, KnowledgeServer
from ks.models import SubscriptionToOther, SubscriptionToThis, ApiReponse
import kag.utils as utils
import forms as myforms 

#DEBUG
#DEBUG


def api_simple_entity_definition(request, base64_SimpleEntity_URIInstance, format):
    '''
    '''
    format = format.upper()
    URISimpleEntity = base64.decodestring(base64_SimpleEntity_URIInstance)
    actual_class = SimpleEntity

    se = SimpleEntity.retrieve(actual_class, URISimpleEntity, False)
    
    instance = get_object_or_404(actual_class, pk=se.id)
    e = EntityStructure.objects.get(name = EntityStructure.simple_entity_entity_structure_name)
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
            instance = SerializableSimpleEntity.retrieve(actual_class, this_ks.uri() + "/" + uri_instance, False)
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
            if v.URIInstance != entity_instance.URIInstance:
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
    if e.is_a_view:
        released_entity_instances = EntityInstance.objects.filter(entity_structure = e, version_released=False)
    else:
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
            entity['URIInstance'] = base64.encodestring(ei['ActualInstance']['EntityStructure']['URIInstance']).replace('\n','')
            entities.append(entity)
    except Exception as es:
        pass #TODO: view.ks_explorer manage exception 
    cont = RequestContext(request, {'entities':entities, 'organization': organization, 'external_ks': external_ks, 'ks_url':base64.encodestring(ks_url).replace('\n','')})
    return render_to_response('ks/ks_explorer_entities.html', context_instance=cont)


def ks_explorer_form(request):
    form = myforms.ExploreOtherKSForm()

    cont = RequestContext(request, {'form':form})
    return render_to_response('ks/ks_explorer_form.html', context_instance=cont)

def browse_entity_instance(request, ks_url, base64URIInstance, format):
    ks_url = base64.decodestring(ks_url)
    this_ks = KnowledgeServer.this_knowledge_server()
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
            external_ks_json = ks
    external_ks = KnowledgeServer()
    external_ks.name = external_ks_json['name']
    external_ks.scheme = external_ks_json['scheme']
    external_ks.netloc = external_ks_json['netloc']
    external_ks.description = external_ks_json['description']
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
        # parse
        decoded = json.loads(entities)
        entities = []
        for ei in decoded['Export']['EntityInstances']:
            entity = {}
            actual_instance_class = ei['ActualInstance'].keys()[0]
            entity['actual_instance_name'] = ei['ActualInstance'][actual_instance_class]['name']
            entity['base64URIInstance'] = base64.encodestring(ei['URIInstance']).replace('\n','')
            entity['URIInstance'] = ei['URIInstance']
            entities.append(entity)
        cont = RequestContext(request, {'entities':entities, 'organization': organization, 'this_ks': this_ks, 'external_ks': external_ks, 'es_info_json': es_info_json})
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
    es = EntityStructure.objects.get(name = EntityStructure.organization_entity_structure_name)
    
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
    
def api_root_uri(request, base64_URIInstance):
    '''
    base64_URIInstance is the URI of an EntityInstance
    Simply return the URIinstance of the root
    '''
    try:
        URIInstance = base64.decodestring(base64_URIInstance)
        ei = EntityInstance.objects.get(URIInstance=URIInstance)
        return HttpResponse('{ "URI" : "' + ei.root.URIInstance + '" }')
    except:
        return HttpResponse('{ "URI" : "" }')

def this_ks_subscribes_to(request, base64_URIInstance):
    '''
    This ks is subscribing to a data set in another ks
    First I store the subscription locally
    Then I invoke remotely api_subscribe
    If it works I commit locally
    '''
    URIInstance = base64.decodestring(base64_URIInstance)
    other_ks_uri = URIInstance[:str.find(URIInstance, '/', str.find(URIInstance, '/', str.find(URIInstance, '/')+1)+1)]  # TODO: make it a method of a helper class to find the URL of the KS from a URIInstance
    try:
        with transaction.atomic():
            # am I already subscribed? We check also whether we have subscribed to another version 
            # (with an API to get the root URIInstance and the attribute root_URI of SubscriptionToOther)
            local_url = reverse('api_root_uri', args=(base64_URIInstance,))
            response = urllib2.urlopen(other_ks_uri + local_url)
            root_URIInstance_json = json.loads(response.read())
            root_URIInstance = root_URIInstance_json['URI']
            others = SubscriptionToOther.objects.filter(root_URI=root_URIInstance)
            if len(others) > 0:
                return render(request, 'entity/export.json', {'json': ApiReponse("failure", "Already subscribed").json()}, content_type="application/json")
            # save locally
            sto = SubscriptionToOther()
            sto.URI = URIInstance
            sto.root_URI = root_URIInstance
            sto.save()
            # invoke remote API to subscribe
            this_ks = KnowledgeServer.this_knowledge_server()
            url_to_invoke = base64.encodestring(this_ks.uri() + reverse ('api_notify')).replace('\n','')
            local_url = reverse ('api_subscribe', args=(base64_URIInstance,url_to_invoke,))
            response = urllib2.urlopen(other_ks_uri + local_url)
            return render(request, 'entity/export.json', {'json': response.read()}, content_type="application/json")
    except:
        pass
    
def api_subscribe(request, base64_URIInstance, base64_remote_url):
    '''
        #35 
        parameters:
        base64_URIInstance the base64 encoded URIInstance to which I want to subscribe
        base64_URL the URL this KS has to invoke to notify
    '''
    # check the client KS has already subscribed
    URIInstance = base64.decodestring(base64_URIInstance)
    ei = EntityInstance.objects.get(URIInstance=URIInstance)
    root_instance_uri = ei.root.URIInstance
    remote_url = base64.decodestring(base64_remote_url)
    existing_subscriptions = SubscriptionToThis.objects.filter(root_instance_uri=root_instance_uri, remote_url=remote_url)
    if len(existing_subscriptions) > 0:
        return render(request, 'entity/export.json', {'json': ApiReponse("failure", "Already subscribed").json()}, content_type="application/json")
    stt = SubscriptionToThis()
    stt.root_instance_uri=root_instance_uri
    stt.remote_url=remote_url
    stt.save()
    return render(request, 'entity/export.json', {'json': ApiReponse("success", "Subscribed sucessfully").json()}, content_type="application/json")
    
def api_unsubscribe(request, base64_URIInstance, base64_URL):
    '''
        #123
        parameters:
        base64_URIInstance the base64 encoded URIInstance to which I want to subscribe
        base64_URL the URL this KS has to invoke to notify
    '''
    
def api_notify(request):
    '''
        #35 it receives a notification; the verb is POST
        parameters:
        URIInstance: the base64 encoded URIInstance of the EntityInstance for which the event has happened
        event_type: the URInstance of the EventType
        extra_info_json: a JSON structure with info specific to an EventType (optional)
    '''
    URIInstance = request.POST.get("URIInstance", "")
    event_type = request.POST.get("event_type", "")
    extra_info_json = request.POST.get("extra_info_json", "")
    
def cron(request):
    '''
        to run tasks that have to be executed periodically on this ks; e.g. 
        * send messages
        * process notifications
        * ...
    '''
    this_ks = KnowledgeServer.this_knowledge_server()
    this_ks.run_cron()

def disclaimer(request):
    '''
    '''
    this_ks = KnowledgeServer.this_knowledge_server()
    cont = RequestContext(request, {'this_ks': this_ks})
    return render_to_response('ks/disclaimer.html', context_instance=cont)

def subscriptions(request):
    '''
    '''
    this_ks = KnowledgeServer.this_knowledge_server()
    cont = RequestContext(request, {'this_ks': this_ks})
    return render_to_response('ks/subscriptions.html', context_instance=cont)

def debug(request):
    '''
    created to debug code
    '''
    from django.db import models, migrations
    from entity.models import Organization, KnowledgeServer, EntityInstance, EntityStructure, SimpleEntity, EntityStructureNode
    from license.models import License

    try:
        # 0004
#         this_ks = KnowledgeServer.this_knowledge_server('default')
#         seLicense=SimpleEntity();seLicense.name="License";seLicense.module="license";seLicense.save(using='default')
#         m_seLicense=seLicense
#         id_on_default_db = seLicense.id
#         m_seLicense.id=None
#         m_seLicense.save(using='ksm')
#         # The following line is needed to make sure that seLicense._state.db is 'default'; 
#         # before the following line it would be 'ksm'
#         seLicense = SimpleEntity.objects.using('default').get(pk=id_on_default_db)
#         
#         en1=EntityStructureNode();en1.simple_entity=seLicense;en1.save(using='default')
#         esLicense=EntityStructure();esLicense.multiple_releases=True;esLicense.is_shallow = True;
#         esLicense.entry_point=en1;esLicense.name="License";esLicense.description="License information";esLicense.namespace="license";
#         esLicense.save(using='default')
#         m_es = EntityStructure.objects.using('ksm').get(name=EntityStructure.entity_structure_entity_structure_name)
#         es = EntityStructure.objects.using('default').get(URIInstance=m_es.URIInstance)
#         ei = EntityInstance(owner_knowledge_server=this_ks,entity_structure=es, entry_point_instance_id=esLicense.id, version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
#         ei.save(using='default');ei.root_id=ei.id;ei.save(using='default')
#         ei.set_released() #here materialization happens
#         
#         
#         seLicense.entity_structure = esLicense; seLicense.save(using='default')
#         
#         # EntityStructure di tipo view per la lista di licenze;  
#         en1=EntityStructureNode();en1.simple_entity=seLicense;en1.save(using='default')
#         esLicenseList=EntityStructure();esLicenseList.is_a_view = True;
#         esLicenseList.entry_point=en1;esLicenseList.name="List of licenses";esLicenseList.description="List of all released licenses";esLicenseList.namespace="license";
#         esLicenseList.save(using='default')
#         # EntityInstance of the above EntityStructure
#         ei = EntityInstance(owner_knowledge_server=this_ks,entity_structure=es, entry_point_instance_id=esLicenseList.id, version_major=0,version_minor=1,version_patch=0,version_description="",version_released=True)
#         ei.save(using='default');ei.root_id=ei.id;ei.save(using='default')
#         ei.set_released() #here materialization happens
#         return HttpResponse("OK")
    
        # 0005        
#         test_license_org = Organization();test_license_org.name="A test Organization hosting license information";test_license_org.website='http://license_org.example.com';test_license_org.description="This is just a test Organization.";
#         test_license_org.save(using='default')
#         id_on_default_db = test_license_org.id
#         test_license_org.id = None
#         test_license_org.save(using='ksm')
#         m_test_license_org = test_license_org
#         test_license_org = Organization.objects.get(pk=id_on_default_db)
#         
#         root_ks = KnowledgeServer.this_knowledge_server('default')
#         root_ks.this_ks = False
#         root_ks.save()
#         root_ks = KnowledgeServer.this_knowledge_server()
#         root_ks.this_ks = False
#         root_ks.save()
#         
#         m_test_license_org_ks = KnowledgeServer(name="A test Open Knowledge Server using some data from opendefinition.org.", scheme="http", netloc="licenses.thekoa.org", description="WARNING: THIS IS NOT AFFILIATED WITH opendefinition.org. IT IS JUST A TEST USING opendefinition.org DATA.", organization=test_license_org, this_ks=True)
#         m_test_license_org_ks.save(using='ksm')
#         test_license_org_ks = m_test_license_org_ks
#         test_license_org_ks.id = None
#         test_license_org_ks.URIInstance = ""
#         test_license_org_ks.save(using='default')
#         
#         # temporarily created in 0004
#         esLicense=EntityStructure.objects.get(name="License") 
#         
#         ######## BEGIN LICENSES DATA
#         
#         #Against DRM 
#         adrm = License()
#         adrm.name = "Against DRM"
#         adrm.short_name = ""
#         adrm.attribution = True
#         adrm.share_alike = True
#         adrm.url_info = "http://opendefinition.org/licenses/against-drm"
#         adrm.reccomended_by_opendefinition = False
#         adrm.conformant_for_opendefinition = True
#         adrm.legalcode = '''
#         '''
#         adrm.save(using='default')
#         ei = EntityInstance(owner_knowledge_server=test_license_org_ks,entity_structure=esLicense, entry_point_instance_id=adrm.id, version_major=2,version_minor=0,version_patch=0,version_description="",version_released=True)
#         ei.save(using='default');ei.root_id=ei.id;ei.save(using='default')
#         ei.set_released() #here materialization happens
#     
#         #Creative Commons Attribution 1.0
#         ccby10 = License()
#         ccby10.name = "Creative Commons Attribution 1.0"
#         ccby10.short_name = "CC-BY-1.0"
#         ccby10.attribution = True
#         ccby10.share_alike = False
#         ccby10.url_info = "http://creativecommons.org/licenses/by/1.0"
#         ccby10.reccomended_by_opendefinition = False
#         ccby10.conformant_for_opendefinition = True
#         ccby10.legalcode = '''
#         '''
#         ccby10.save(using='default')
#         ei_ccby10 = EntityInstance(owner_knowledge_server=test_license_org_ks,entity_structure=esLicense, entry_point_instance_id=ccby10.id, version_major=1,version_minor=0,version_patch=0,version_description="",version_released=True)
#         ei_ccby10.save(using='default');ei_ccby10.root_id=ei_ccby10.id;ei_ccby10.save(using='default')
#         ei.set_released() #here materialization happens
#     
#         # above reccomended; below other conformant
#         
#         #Creative Commons CCZero
#         cczero = License()
#         cczero.name = "Creative Commons CCZero"
#         cczero.short_name = "CC0"
#         cczero.attribution = False
#         cczero.share_alike = False
#         cczero.url_info = "http://opendefinition.org/licenses/cc-zero"
#         cczero.reccomended_by_opendefinition = True
#         cczero.conformant_for_opendefinition = True
#         cczero.legalcode = '''
#         '''
#         cczero.save(using='default')
#         ei = EntityInstance(owner_knowledge_server=test_license_org_ks,entity_structure=esLicense, entry_point_instance_id=cczero.id, version_major=1,version_minor=0,version_patch=0,version_description="",version_released=True)
#         ei.save(using='default');ei.root_id=ei.id;ei.save(using='default')
#         ei.set_released() #here materialization happens
#     
#         #Open Data Commons Public Domain Dedication and Licence
#         pddl = License()
#         pddl.name = "Open Data Commons Public Domain Dedication and Licence"
#         pddl.short_name = "PDDL"
#         pddl.attribution = False
#         pddl.share_alike = False
#         pddl.url_info = "http://opendefinition.org/licenses/odc-pddl"
#         pddl.reccomended_by_opendefinition = True
#         pddl.conformant_for_opendefinition = True
#         pddl.legalcode = '''
#         '''
#         pddl.save(using='default')
#         ei = EntityInstance(owner_knowledge_server=test_license_org_ks,entity_structure=esLicense, entry_point_instance_id=pddl.id, version_major=1,version_minor=0,version_patch=0,version_description="",version_released=True)
#         ei.save(using='default');ei.root_id=ei.id;ei.save(using='default')
#         ei.set_released() #here materialization happens
#     
#         #Creative Commons Attribution 4.0
#         ccby40 = License()
#         ccby40.name = "Creative Commons Attribution 4.0"
#         ccby40.short_name = "CC-BY-4.0"
#         ccby40.attribution = True
#         ccby40.share_alike = False
#         ccby40.url_info = "http://creativecommons.org/licenses/by/4.0"
#         ccby40.reccomended_by_opendefinition = True
#         ccby40.conformant_for_opendefinition = True
#         ccby40.legalcode = '''
#         '''
#         ccby40.save(using='default')
#         ei = EntityInstance(owner_knowledge_server=test_license_org_ks,root_id=ei_ccby10.id,entity_structure=esLicense, entry_point_instance_id=ccby40.id, version_major=4,version_minor=0,version_patch=0,version_description="",version_released=True)
#         ei.save(using='default')
#         ei.set_released() #here materialization happens
#     
#         #Open Data Commons Attribution License 
#         odcby = License()
#         odcby.name = "Open Data Commons Attribution License"
#         odcby.short_name = "ODC-BY"
#         odcby.attribution = True
#         odcby.share_alike = False
#         odcby.url_info = "http://opendefinition.org/licenses/odc-by"
#         odcby.reccomended_by_opendefinition = True
#         odcby.conformant_for_opendefinition = True
#         odcby.legalcode = '''
#         '''
#         odcby.save(using='default')
#         ei = EntityInstance(owner_knowledge_server=test_license_org_ks,entity_structure=esLicense, entry_point_instance_id=odcby.id, version_major=1,version_minor=0,version_patch=0,version_description="",version_released=True)
#         ei.save(using='default');ei.root_id=ei.id;ei.save(using='default')
#         ei.set_released() #here materialization happens
#     
#         #Creative Commons Attribution Share-Alike 4.0  
#         ccbysa40 = License()
#         ccbysa40.name = "Creative Commons Attribution Share-Alike 4.0"
#         ccbysa40.short_name = "CC-BY-SA-4.0"
#         ccbysa40.attribution = True
#         ccbysa40.share_alike = True
#         ccbysa40.url_info = "http://opendefinition.org/licenses/cc-by-sa"
#         ccbysa40.reccomended_by_opendefinition = True
#         ccbysa40.conformant_for_opendefinition = True
#         ccbysa40.legalcode = '''
#         '''
#         ccbysa40.save(using='default')
#         # note that version_released=False
#         ei = EntityInstance(owner_knowledge_server=test_license_org_ks,entity_structure=esLicense, entry_point_instance_id=ccbysa40.id, version_major=4,version_minor=0,version_patch=0,version_description="",version_released=False)
#         ei.save(using='default');ei.root_id=ei.id;ei.save(using='default')
#         # I do not set it as released; it will be done to demonstrate the notification and update process
#         # ei.set_released() #here materialization happens
#     
#         #Open Data Commons Open Database License 
#         odbl = License()
#         odbl.name = "Open Data Commons Open Database License"
#         odbl.short_name = "ODbL"
#         odbl.attribution = True
#         odbl.share_alike = False
#         odbl.url_info = "http://opendefinition.org/licenses/odc-odbl"
#         odbl.reccomended_by_opendefinition = True
#         odbl.conformant_for_opendefinition = True
#         odbl.legalcode = '''
#         '''
#         odbl.save(using='default')
#         ei = EntityInstance(owner_knowledge_server=test_license_org_ks,entity_structure=esLicense, entry_point_instance_id=odbl.id, version_major=1,version_minor=0,version_patch=0,version_description="",version_released=True)
#         ei.save(using='default');ei.root_id=ei.id;ei.save(using='default')
#         ei.set_released() #here materialization happens
#     
#         ######## END LICENSES DATA
#     
#         esLicenseList = EntityStructure.objects.get(name="List of licenses")
#         
#         # 2 EntityInstance with the above EntityStructure
#         # opendefinition.org conformant
#         ei = EntityInstance(owner_knowledge_server=test_license_org_ks,filter_text="conformant_for_opendefinition=True",entity_structure=esLicenseList,description="All opendefinition.org conformant licenses.")
#         ei.save(using='default');ei.root_id=ei.id;ei.save(using='default')
#         # let's materialize the ei that is a view so it doesn't need to be set to released
#         ei.materialize(ei.shallow_entity_structure().entry_point, processed_instances = [])
#         # opendefinition.org conformant and reccomended
#         ei = EntityInstance(owner_knowledge_server=test_license_org_ks,filter_text="reccomended_by_opendefinition=True",entity_structure=esLicenseList,description="All opendefinition.org conformant and reccomended licenses.")
#         ei.save(using='default');ei.root_id=ei.id;ei.save(using='default')
#         # let's materialize the ei that is a view so it doesn't need to be set to released
#         ei.materialize(ei.shallow_entity_structure().entry_point, processed_instances = [])
    
        return HttpResponse("OK")
    except Exception as es:
        return HttpResponse(es.message)