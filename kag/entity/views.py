# -*- coding: utf-8 -*-

from datetime import datetime
from django import forms
from django.conf import settings
from django.db import models
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.template import RequestContext

from application.models import Application, Method
from entity.models import SimpleEntity, DataSetStructure, KnowledgeServer, DataSet, StructureNode, UploadedFile, SerializableSimpleEntity
from forms import UploadFileForm, ImportChoice, ImportChoiceNothingOnDB
from lxml import etree
from userauthorization.models import KUser, PermissionHolder
from xml.dom import minidom

import kag.utils as utils

def index(request):
#    instance_list = SimpleEntity.objects.order_by('name')
    instance_list = SimpleEntity.objects.all()
#     entities_and_trees = []
#     for dataset in entity_list:
#         e = SimpleEntity.objects.get(name=dataset.__class__.__name__)
#         entities = DataSetStructure.objects.filter(entry_point__entity = e)
#         entities_and_trees.append([dataset, entities])
    context = {'instance_list': instance_list, "class_name": "SimpleEntity"}
    
    return render(request, 'entity/index.html', context)

def entity_index(request, simple_entity_id):
    e = SimpleEntity.objects.get(pk=simple_entity_id)
    actual_class = utils.load_class(e.module + ".models", e.name)
    instance_list = actual_class.objects.all() # eval(e.name + ".objects.all()")
    context = {'instance_list': instance_list, "class_name": e.name}
    
    return render(request, 'entity/index.html', context)

def detail(request, simple_entity_id, application_id):
    if not request.user.is_authenticated():
        return redirect('/application/')
    else:
        entity = get_object_or_404(SimpleEntity, pk=simple_entity_id)
        application = get_object_or_404(Application, pk=application_id)
        authenticated_user = request.user
        kuser = KUser.objects.get(login = request.user.username)
        methods = []
        for method in kuser.permission_holder.methods.all():
            try:
                method.application_set.get(id=application.id)
                methods.append(method)
            except:
                pass
    return render(request, 'entity/detail.html', {'entity': entity, 'application': application, 'authenticated_user': authenticated_user, 'methods': methods})


def FormAlVolo(mod):
    class FAV(forms.ModelForm):
        class Meta:
            model = mod
    return FAV

def getForm(method, name="FlyModel"):
    attris = {
        '__module__': Method.__module__,
    }
    for attr in method.attributes.all():
        attris[attr.name] = models.CharField(attr.name, max_length=200, blank=True)
    try:
        cmod = type(name, (models.Model,), attris)
    except Exception as ex:
        print ex

    return FormAlVolo(cmod)

def method(request, simple_entity_id, application_id, method_id):
    # simple_entity_id is 0 when the method creates an instance of entity
    entity = None
    if simple_entity_id>0:
        entity = get_object_or_404(SimpleEntity, pk=simple_entity_id)
    application = get_object_or_404(Application, pk=application_id)
    method = get_object_or_404(Method, pk=method_id)
    authenticated_user = request.user

    attrib_form = getForm(method)
    return render(request, 'entity/method.html', {'entity': entity, 'application': application, 'authenticated_user': authenticated_user, 'method': method, 'form': attrib_form})

def export(request, dataset_structure_id, simple_entity_instance_id, simple_entity_id):
    se = SimpleEntity.objects.get(pk = simple_entity_id)
    actual_class = utils.load_class(se.module + ".models", se.name)
    instance = get_object_or_404(actual_class, pk=simple_entity_instance_id)
    e = DataSetStructure.objects.get(pk = dataset_structure_id)
    exported_xml = "<Export DataSetStructureName=\"" + e.name + "\" DataSetStructureURI=\"" + e.URIInstance + "\" ExportDateTime=\"" + str(datetime.now()) + "\">" + instance.serialize(e.entry_point, exported_instances = []) + "</Export>"
    xmldoc = minidom.parseString(exported_xml)
    exported_pretty_xml = xmldoc.toprettyxml(indent="    ")
    return render(request, 'entity/export.xml', {'xml': exported_pretty_xml}, content_type="application/xhtml+xml")
    
def upload_page(request):
    message = ''
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            xml_uploaded = request.FILES['file'].read()
            # http://stackoverflow.com/questions/3310614/remove-whitespaces-in-xml-string 
            p = etree.XMLParser(remove_blank_text=True)
            elem = etree.XML(xml_uploaded, parser=p)
            xml_uploaded = etree.tostring(elem)
            
            new_uploaded_file = UploadedFile(docfile = request.FILES['file'])
            # we save it on disk so that we can process it after the user has told us which part to import and how to import it
            new_uploaded_file.save()
            # we parse it so that we check what is on the file against what is on the database and we show this info to the user
            try:
                # I extract the information I want to show to the user before I actually perform the import
                # The info allows the user to compare what is in the file and what is in the database
                # so that they can decide whether to update or insert
                initial_data = {}
                initial_data['uploaded_file_id'] = new_uploaded_file.id
                initial_data['new_uploaded_file_relpath'] = new_uploaded_file.docfile.url
                xmldoc = minidom.parseString(xml_uploaded)
                URI = xmldoc.childNodes[0].attributes["DataSetStructureURI"].firstChild.data
                e = DataSetStructure.objects.get(URIInstance=URI)
                # I check that the first SimpleEntity is the same simple_entity of the DataSetStructure's entry_point
                if e.entry_point.simple_entity.name != xmldoc.childNodes[0].childNodes[0].tagName:
                    message = "The DataSetStructure structure tells that the first SimpleEntity should be " + e.entry_point.simple_entity.name + " but the first TAG in the file is " + xmldoc.childNodes[0].childNodes[0].tagName
                    raise Exception(message) 
                else:
                    # Is there a URIInstance of the first SimpleEntity;
                    try:
                        simple_entity_uri_instance = xmldoc.childNodes[0].childNodes[0].attributes["URIInstance"].firstChild.data
                    except Exception as ex:
                        # if it's not in the file it means that the data in the file does not come from a KS
                        simple_entity_uri_instance = None
                    initial_data['simple_entity_uri_instance'] = simple_entity_uri_instance
                    try:
                        initial_data['simple_entity_name'] = xmldoc.childNodes[0].childNodes[0].attributes[e.entry_point.simple_entity.name_field].firstChild.data
                    except:
                        initial_data['simple_entity_name'] = None
                    try:
                        initial_data['simple_entity_description'] = xmldoc.childNodes[0].childNodes[0].attributes[e.entry_point.simple_entity.description_field].firstChild.data
                    except:
                        initial_data['simple_entity_description'] = None
                    module_name = e.entry_point.simple_entity.module
                    child_node = xmldoc.childNodes[0].childNodes[0]
                    actual_class_name = module_name + ".models " + child_node.tagName
                    initial_data['actual_class_name'] = actual_class_name
                    actual_class = utils.load_class(module_name + ".models", child_node.tagName)
                    try:
                        '''
                        ?How does the import work wrt URIInstance? A SerializableSimpleEntity has
                            URIInstance
                            URI_imported_instance
                        attributes; the second comes from the imported record (if any); the first is generated
                        upon record creation; so the first always refer to local KS; the second, if present,
                        will tell you where the record comes from via import or fetch (fetch not implemented yet) 
                        '''
                        if not simple_entity_uri_instance is None:
                            simple_entity_on_db = actual_class.retrieve(simple_entity_uri_instance)
                            initial_data['simple_entity_on_db'] = simple_entity_on_db
                            initial_data['simple_entity_on_db_name'] = getattr(simple_entity_on_db, e.entry_point.simple_entity.name_field) if e.entry_point.simple_entity.name_field else ""
                            initial_data['simple_entity_on_db_description'] = getattr(simple_entity_on_db, e.entry_point.simple_entity.description_field) if e.entry_point.simple_entity.description_field else ""
                            initial_data['simple_entity_on_db_URIInstance'] = getattr(simple_entity_on_db, "URIInstance")
                        else:
                            initial_data['simple_entity_on_db'] = None
                    except:
                        # .get returning more than one record would be a logical error (CHECK: ?and should be raised here?) 
                        # it could actually happen if I use an export from this ks to import again into new records
                        # then I modify the file and import again; instead of modifying the file the preferred behavior
                        # should be to export, modify the newly exported file and import again; this last method would work
                        # the first wouldn't yield initial_data['simple_entity_on_db'] = None
                        initial_data['simple_entity_on_db'] = None
                    initial_data['prettyxml'] = xmldoc.toprettyxml(indent="    ")
                    initial_data['file'] = request.FILES['file']
                    initial_data['new_uploaded_file'] = new_uploaded_file
                    if initial_data['simple_entity_on_db'] is None:
                        import_choice_form = ImportChoiceNothingOnDB(initial={'uploaded_file_id': new_uploaded_file.id, 'new_uploaded_file_relpath': new_uploaded_file.docfile.url, 'how_to_import': 1})
                    else:
                        import_choice_form = ImportChoice(initial={'uploaded_file_id': new_uploaded_file.id, 'new_uploaded_file_relpath': new_uploaded_file.docfile.url, 'how_to_import': 0})
                    initial_data['import_choice_form'] = import_choice_form
                    return render(request, 'entity/import_file.html', initial_data)
            except Exception as ex:
                message = 'Error parsing uploaded file: ' + str(ex)
    else:
        form = UploadFileForm()
    return render_to_response('entity/upload_page.html', {'form': form, 'message': message}, context_instance=RequestContext(request))

def perform_import(request):
    '''
    Import is performed according to an DataSetStructure i.e. a structure of SimpleEntity(s)
    The structure allows to have references to a SimpleEntity; use a reference
    when you need to associate to that SimpleEntity but do not want to import/export that
    SimpleEntity. When a SimpleEntity is a reference its ID does not matter; its URI is 
    relevant. The import behavior for reference is:
    it looks for a SimpleEntity with the same URI, if it does exist it takes it's ID and
    uses it for the relationships; otherwise it creates it (which of course happens only once)
    The import behavior when not reference is .................................
    '''
    new_uploaded_file_relpath = request.POST["new_uploaded_file_relpath"]
#     request.POST['how_to_import']
#     0   Update if ID exists, create if ID is empty or non existent
#     1   Always create new records

    # how_to_import = true  ==> always_insert = always create 
    # how_to_import = false ==> Update if ID exists, create if ID is empty or non existent 
    always_insert = (int(request.POST.get("how_to_import", "")) == 1)
    with open(settings.BASE_DIR + "/" + new_uploaded_file_relpath, 'r') as content_file:
        xml_uploaded = content_file.read()
    # http://stackoverflow.com/questions/3310614/remove-whitespaces-in-xml-string 
    p = etree.XMLParser(remove_blank_text=True)
    elem = etree.XML(xml_uploaded, parser=p)
    xml_uploaded = etree.tostring(elem)
    xmldoc = minidom.parseString(xml_uploaded)
    try:
        URIInstance = xmldoc.childNodes[0].attributes["DataSetStructureURI"].firstChild.data
        et = DataSetStructure.objects.get(URIInstance=URIInstance)
    except Exception as ex:
        raise Exception("I cannot find the DataSetStructure in my database or it's DataSetStructureURI in the file you submitted: " + str(ex))
    child_node = xmldoc.childNodes[0].childNodes[0]

    try:
        se = SimpleEntity.objects.get(URIInstance = child_node.attributes["URISimpleEntity"].firstChild.data)
    except Exception as ex:
        raise Exception("I cannot find the SimpleEntity " + child_node.attributes["URISimpleEntity"].firstChild.data + " Error: " + str(ex))
    assert (et.entry_point.simple_entity.name == child_node.tagName == se.name), "child_node.simple_entity.name - child_node.tagName - se.name: " + child_node.simple_entity.name + ' - ' + child_node.tagName + ' - ' + se.name

    module_name = et.entry_point.simple_entity.module
    actual_class = utils.load_class(module_name + ".models", child_node.tagName)
    
    try:
        simple_entity_uri_instance = xmldoc.childNodes[0].childNodes[0].attributes["URIInstance"].firstChild.data
    except Exception as ex:
        # if it's not in the file it means that the data in the file does not come from a KS
        simple_entity_uri_instance = None
    if always_insert or (simple_entity_uri_instance is None):
        instance = actual_class()
    else:
        instance = actual_class.retrieve(simple_entity_uri_instance)
    #At least the first node has full export = True otherwise I would not import anything but just load something from the db 
    instance.from_xml(child_node, et.entry_point, always_insert)
    return HttpResponse("OK")


