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
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from entity.models import SimpleEntity, EntityStructure, EntityInstance, SerializableSimpleEntity, KnowledgeServer
from entity.models import SubscriptionToOther, SubscriptionToThis, ApiReponse, NotificationReceived, KsUri, Notification, Event
import kag.utils as utils
import logging
import forms as myforms 

logger = logging.getLogger(__name__)

def api_simple_entity_definition(request, base64_SimpleEntity_URIInstance, format):
    '''
        #33
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
        #36
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
        exported_json = '{ "Export" : { "ExportDateTime" : "' + str(datetime.now()) + '", "EntityInstance" : ' + ei.serialize_with_actual_instance(format = format) + ' } }'
        return render(request, 'entity/export.json', {'json': exported_json}, content_type="application/json")
    if format == 'XML':
        exported_xml = "<Export ExportDateTime=\"" + str(datetime.now()) + "\">" + ei.serialize_with_actual_instance(format = format) + "</Export>"
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
    
    return api_entity_instances(request, base64.encodestring(e.URIInstance).replace('\n',''), format)

def api_entity_instance_info(request, base64_EntityInstance_URIInstance, format):
    '''
        #52 
        
        Parameters:
        * format { 'XML' | 'JSON' | 'HTML' = 'BROWSE' }
        * base64_EntityInstance_URIInstance: URIInstance of the EntityInstance base64 encoded
        
        Implementation:
        it fetches the EntityInstance, then the list of all that share the same root
        it returns EntityInstance.serialize_with_actual_instance(format) and for each on the above list:
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
            all_versions_serialized += v.serialize_with_actual_instance(format = format, force_external_reference=True)
            comma = ", "
    if format == 'XML':
        exported_xml = "<Export ExportDateTime=\"" + str(datetime.now()) + "\"><EntityInstance>" + entity_instance.serialize_with_actual_instance(format = format, force_external_reference=True) + "</EntityInstance><Versions>" + all_versions_serialized + "</Versions></Export>"
        xmldoc = minidom.parseString(exported_xml)
        exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
        return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")
    if format == 'JSON':
        exported_json = '{ "Export" : { "ExportDateTime" : "' + str(datetime.now()) + '", "EntityInstance" : ' + entity_instance.serialize_with_actual_instance(format = format, force_external_reference=True) + ', "Versions" : [' + all_versions_serialized + '] } }'
        return render(request, 'entity/export.json', {'json': exported_json}, content_type="application/json")
    if format == 'HTML' or format == 'BROWSE':
        if entity_instance.entity_structure.is_a_view:
            instances = entity_instance.get_instances()
        else:
            instances = []
            instances.append(entity_instance.get_instance())
        all_versions_with_instances = []
        for v in all_versions:
            if v.URIInstance != entity_instance.URIInstance:
                version_with_instance = {}
                version_with_instance['entity_instance'] = v
                version_with_instance['simple_entity'] = v.get_instance()
                all_versions_with_instances.append(version_with_instance)
        cont = RequestContext(request, {'base64_EntityInstance_URIInstance': base64_EntityInstance_URIInstance, 'entity_instance': entity_instance, 'all_versions_with_instances': all_versions_with_instances, 'ks': entity_instance.owner_knowledge_server, 'instances': instances})
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
        serialized += ei.serialize_with_actual_instance(format = format, force_external_reference=True)
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
        this_ks = KnowledgeServer.this_knowledge_server()
        # info on the remote ks
        local_url = reverse('api_ks_info', args=("JSON",))
        response = urllib2.urlopen(ks_url + local_url)
        ks_info_json_stream = response.read()
        # parsing json
        ks_info_json = json.loads(ks_info_json_stream)
        organization = ks_info_json['Export']['EntityInstance']['ActualInstance']['Organization']
        for ks in organization['knowledgeserver_set']:
            if ks['this_ks'] == 'True':
                explored_ks = ks
            
        # info about structures on the remote ks
        local_url = reverse('api_entity_structures', args=("JSON",))
        response = urllib2.urlopen(ks_url + local_url)
        entities_json = response.read()
        # parsing json
        decoded = json.loads(entities_json)
        owned_structures = []
        other_structures = []
        for ei in decoded['Export']['EntityInstances']:
            entity = {}
            entity['actual_instance_name'] = ei['ActualInstance']['EntityStructure']['name']
            entity['URIInstance'] = base64.encodestring(ei['ActualInstance']['EntityStructure']['URIInstance']).replace('\n','')
            entity['oks_name'] = ei['owner_knowledge_server']['name']
            entity['oks_URIInstance'] = base64.encodestring(ei['owner_knowledge_server']['URIInstance']).replace('\n','')
            if ei['owner_knowledge_server']['URIInstance'] == explored_ks['URIInstance']:
                owned_structures.append(entity)
            else:
                other_structures.append(entity)
    except Exception as es:
        pass #TODO: view.ks_explorer manage exception
    cont = RequestContext(request, {'owned_structures':owned_structures, 'other_structures':other_structures, 'this_ks':this_ks, 'this_ks_base64_url':this_ks.uri(True), 'organization': organization, 'explored_ks': explored_ks, 'ks_url':base64.encodestring(ks_url).replace('\n','')})
    return render_to_response('ks/ks_explorer_entities.html', context_instance=cont)

def ks_explorer_form(request):
    form = myforms.ExploreOtherKSForm()
    this_ks = KnowledgeServer.this_knowledge_server()
    cont = RequestContext(request, {'form':form, 'this_ks':this_ks, 'this_ks_base64_url':this_ks.uri(True)})
    return render_to_response('ks/ks_explorer_form.html', context_instance=cont)

def browse_entity_instance(request, ks_url, base64URIInstance, format):
    ks_url = base64.decodestring(ks_url)
    this_ks = KnowledgeServer.this_knowledge_server()
    format = format.upper()

    # info on the remote ks{{  }}
    local_url = reverse('api_ks_info', args=("JSON",))
    response = urllib2.urlopen(ks_url + local_url)
    ks_info_json_stream = response.read()
    # parsing json
    ks_info_json = json.loads(ks_info_json_stream)
    organization = ks_info_json['Export']['EntityInstance']['ActualInstance']['Organization']
    for ks in organization['knowledgeserver_set']:
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
        local_url = reverse('api_entity_instances', args=(base64URIInstance,format))
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
        # I prepare a list of URIInstance of root so that I can check which I have subscribed to
        root_URIInstances = []
        for ei in decoded['Export']['EntityInstances']:
            root_URIInstances.append(ei['root']['URIInstance'])
        subscribed = SubscriptionToOther.objects.filter(root_URIInstance__in=root_URIInstances)
        subscribed_root_URIInstances = []
        for s in subscribed:
            subscribed_root_URIInstances.append(s.root_URIInstance)
        entities = []
        for ei in decoded['Export']['EntityInstances']:
            entity = {}
            if 'ActualInstance' in ei.keys():
                actual_instance_class = ei['ActualInstance'].keys()[0]
                entity['actual_instance_name'] = ei['ActualInstance'][actual_instance_class]['name']
            else: #is a view
                entity['actual_instance_name'] = ei['description']
            entity['base64URIInstance'] = base64.encodestring(ei['URIInstance']).replace('\n','')
            entity['URIInstance'] = ei['URIInstance']
            if ei['root']['URIInstance'] in subscribed_root_URIInstances:
                entity['subscribed'] = True
            entities.append(entity)
        cont = RequestContext(request, {'entities':entities, 'organization': organization, 'this_ks': this_ks, 'external_ks': external_ks, 'es_info_json': es_info_json})
        return render_to_response('ks/browse_entity_instance.html', context_instance=cont)
    
def home(request):
    this_ks = KnowledgeServer.this_knowledge_server()
    cont = RequestContext(request, {'this_ks':this_ks, 'this_ks_base64_url':this_ks.uri(True)})
    return render(request, 'ks/home.html', context_instance=cont)

def api_ks_info(request, format):
    '''
        #80

        parameter:
        * format { 'XML' | 'JSON' }
        
        Implementation:
          it fetches this KS from the DB, takes its Organization and exports
          it with the structure "Organization-KS" 
    '''
    format = format.upper()
    this_ks = KnowledgeServer.this_knowledge_server()    
    es = EntityStructure.objects.get(name = EntityStructure.organization_entity_structure_name)
    ei = EntityInstance.objects.get(entity_structure=es, entry_point_instance_id=this_ks.organization.id)
    base64_EntityInstance_URIInstance = base64.encodestring(ei.URIInstance).replace('\n','')
    return api_entity_instance(request, base64_EntityInstance_URIInstance, format)
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
        #110 duplicates #36 = api_entity_instance
        
        Parameters:
        * format { 'XML' | 'JSON' | 'HTML' = 'BROWSE' }
        * base64_EntityInstance_URIInstance: URIInstance of the EntityInstance base64 encoded
        
        Implementation:
        it fetches the EntityInstance, then the SimpleEntity
        it returns SimpleEntity.serialize according to the EntityStructure and the format

    '''
    return api_entity_instance(request, base64_EntityInstance_URIInstance, format)

    format = format.upper()
    URIInstance = base64.decodestring(base64_EntityInstance_URIInstance)
    entity_instance = EntityInstance.retrieve(EntityInstance, URIInstance, False)
    simple_entity = entity_instance.get_instance()
    entity_instance.ser
    if format == 'XML':
        exported_xml = "<Export ExportDateTime=\"" + str(datetime.now()) + "\" EntityStructureURI=\"" + entity_instance.entity_structure.URIInstance + "\">" + simple_entity.serialize(etn = entity_instance.entity_structure.entry_point, exported_instances = [], format = format) + "</Export>"
        xmldoc = minidom.parseString(exported_xml)
        exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
        return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")
    if format == 'JSON' or format == 'HTML' or format == 'BROWSE':
        exported_json = '{ "Export" : { "ExportDateTime" : "' + str(datetime.now()) + '", "EntityStructureURI" : "' + entity_instance.entity_structure.URIInstance + '", ' + simple_entity.serialize(etn = entity_instance.entity_structure.entry_point, exported_instances = [], format = "JSON") + ' } }'
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

def this_ks_unsubscribes_to(request, base64_URIInstance):
    '''
    '''
    pass

def redirect_to_base64_oks_url(request, base64_oks_URIInstance):
    '''
    Used in templates to redirect to a KS URIInstance when I have just the base64 encoding
    '''
    ks_uri = KsUri(base64.decodestring(base64_oks_URIInstance))
    if ks_uri.is_sintactically_correct:
        return redirect(ks_uri.scheme + "://" + ks_uri.netloc)
    else:
        return HttpResponse("The URI is not sintactically correct: " + base64.decodestring(base64_oks_URIInstance))

def this_ks_subscribes_to(request, base64_URIInstance):
    '''
    This ks is subscribing to a data set in another ks
    First I store the subscription locally
    Then I invoke remotely api_subscribe
    If it works I commit locally
    '''
    URIInstance = base64.decodestring(base64_URIInstance)
    other_ks_uri = URIInstance[:str.find(URIInstance, '/', str.find(URIInstance, '/', str.find(URIInstance, '/')+1)+1)]  # TODO: make it a method of a helper class to find the URL of the KS from a URIInstance

    local_url = reverse('api_ks_info', args=("XML",))
    response = urllib2.urlopen(other_ks_uri + local_url)
    ks_info_xml_stream = response.read()
    # from_xml_with_actual_instance creates the entity instance and the actual instance
    ei = EntityInstance()
    local_ei = ei.from_xml_with_actual_instance(ks_info_xml_stream)
    # I have imported a KnowledgeServer with this_ks = True; must set it to False (see this_knowledge_server())
    external_org = local_ei.get_instance()
    for ks in external_org.knowledgeserver_set.all():
        ks.this_ks = False
        ks.save()
    # Now I can materialize it; I can use set released as I have certainly retrieved a released EntityInstance
    local_ei.set_released()
    
    try:
        with transaction.atomic():
            # am I already subscribed? We check also whether we have subscribed to another version 
            # (with an API to get the root URIInstance and the attribute root_URIInstance of SubscriptionToOther)
            local_url = reverse('api_root_uri', args=(base64_URIInstance,))
            response = urllib2.urlopen(other_ks_uri + local_url)
            root_URIInstance_json = json.loads(response.read())
            root_URIInstance = root_URIInstance_json['URI']
            others = SubscriptionToOther.objects.filter(root_URIInstance=root_URIInstance)
            if len(others) > 0:
                return render(request, 'entity/export.json', {'json': ApiReponse("failure", "Already subscribed").json()}, content_type="application/json")
            # save locally
            sto = SubscriptionToOther()
            sto.URI = URIInstance
            sto.root_URIInstance = root_URIInstance
            sto.save()
            # invoke remote API to subscribe
            this_ks = KnowledgeServer.this_knowledge_server()
            url_to_invoke = base64.encodestring(this_ks.uri() + reverse('api_notify')).replace('\n','')
            local_url = reverse('api_subscribe', args=(base64_URIInstance,url_to_invoke,))
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
    root_URIInstance = ei.root.URIInstance
    remote_url = base64.decodestring(base64_remote_url)
    existing_subscriptions = SubscriptionToThis.objects.filter(root_URIInstance=root_URIInstance, remote_url=remote_url)
    if len(existing_subscriptions) > 0:
        return render(request, 'entity/export.json', {'json': ApiReponse("failure", "Already subscribed").json()}, content_type="application/json")
    stt = SubscriptionToThis()
    stt.root_URIInstance=root_URIInstance
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
    
@csrf_exempt
def api_notify(request):
    '''
        #35 it receives a notification; the verb is POST
        parameters:
        URIInstance: the base64 encoded URIInstance of the EntityInstance for which the event has happened
        event_type: the URInstance of the EventType
        extra_info_json: a JSON structure with info specific to an EventType (optional)
    '''
    root_URIInstance = request.POST.get("root_URIInstance", "")
    URL_dataset = request.POST.get("URL_dataset", "")
    URL_structure = request.POST.get("URL_structure", "")
    type = request.POST.get("type", "")
    # Did I subscribe to this?
    sto = SubscriptionToOther.objects.filter(root_URIInstance=root_URIInstance)
    ar = ApiReponse()
    if len(sto) > 0:
        nr = NotificationReceived()
        nr.URL_dataset = URL_dataset
        nr.URL_structure = URL_structure
        nr.save()
        ar.status = "success"
    else:
        ar.status = "failure"
        ar.message = "Not subscribed to this"
    return render(request, 'entity/export.json', {'json': ar.json()}, content_type="application/json")
        
def cron(request):
    '''
        to run tasks that have to be executed periodically on this ks; e.g. 
        * send messages
        * process notifications
        * ...
    '''
    this_ks = KnowledgeServer.this_knowledge_server()
    response = this_ks.run_cron()
    return HttpResponse(response)

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
    subscriptions_to_this = SubscriptionToThis.objects.all()
    events = Event.objects.filter(processed=False)
    notifications_to_be_sent = Notification.objects.filter(sent=False)
    received_notifications = NotificationReceived.objects.filter(processed=False)
    subscriptions_to_other = SubscriptionToOther.objects.all()
    cont = RequestContext(request, {'received_notifications': received_notifications, 'notifications_to_be_sent': notifications_to_be_sent, 'events': events, 'subscriptions_to_other': subscriptions_to_other, 'subscriptions_to_this': subscriptions_to_this, 'this_ks': this_ks, 'this_ks_base64_url':this_ks.uri(True)})
    
    return render_to_response('ks/subscriptions.html', context_instance=cont)

def debug(request):
    '''
    created to debug code
    '''
    from django.db import models, migrations
    from entity.models import KsUri, Organization, KnowledgeServer, EntityInstance, EntityStructure, SimpleEntity, EntityStructureNode
    from license.models import License
    from kag.utils import poor_mans_logger
    
    dataset_xml_stream='''<?xml version="1.0" ?>
<Export ExportDateTime="2015-08-19 11:11:18.156712">
    <EntityInstance URIInstance="http://licenses.thekoa.org/entity/EntityInstance/24" URI_imported_instance="" URI_previous_version="" description="" entry_point_instance_id="2" filter_text="" id="24" version_date="2015-08-19 07:36:30+00:00" version_description="" version_major="1" version_minor="0" version_patch="0" version_released="True">
        <entity_structure URIInstance="http://rootks.thekoa.org/entity/EntityStructure/6" URISimpleEntity="http://rootks.thekoa.org/entity/SimpleEntity/10" id="6" name="License"/>
        <owner_knowledge_server URIInstance="http://licenses.thekoa.org/entity/KnowledgeServer/2" URISimpleEntity="http://rootks.thekoa.org/entity/SimpleEntity/14" id="2" name="A test Open Knowledge Server using some data from opendefinition.org."/>
        <root URIInstance="http://licenses.thekoa.org/entity/EntityInstance/24" URISimpleEntity="http://rootks.thekoa.org/entity/SimpleEntity/13" id="24"/>
        <ActualInstance>
            <License URIInstance="http://licenses.thekoa.org/license/License/2" URISimpleEntity="http://rootks.thekoa.org/entity/SimpleEntity/16" URI_imported_instance="" URI_previous_version="" adaptation_shared="" attribution="True" commercial_use="" conformant_for_opendefinition="True" human_readable="" id="2" image="" image_small="" legalcode="     " name="Creative Commons Attribution 1.0" reccomended_by_opendefinition="False" share_alike="False" short_name="CC-BY-1.0" url_info="http://creativecommons.org/licenses/by/1.0"/>
        </ActualInstance>
    </EntityInstance>
</Export>'''
#     ei = EntityInstance()
#     ei.from_xml_with_actual_instance(dataset_xml_stream)
#     k = KsUri("http://rootks.thekoa.org/entity/SimpleEntity/1/json/")
    
    logger = poor_mans_logger()
    try:
        logger.debug("debug")
        logger.info("info")
        logger.warning("warning")
        logger.error("error")
        logger.critical("critical")
        return HttpResponse("OK")
    except Exception as es:
        return HttpResponse(es.message)