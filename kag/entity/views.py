from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from entity.models import Entity, EntityTree, EntityTreeNode, UploadedFile
from django.shortcuts import render, get_object_or_404, redirect
from application.models import Application, Method
from userauthorization.models import KUser, PermissionHolder

from django.http import HttpResponse
from xml.dom import minidom
from django.db import models
from django import forms
from django.template import RequestContext
from forms import UploadFileForm, ImportChoice
from django.shortcuts import render_to_response

def index(request):
    instance_list = Entity.objects.order_by('name')
#     entities_and_trees = []
#     for entity_instance in entity_list:
#         e = Entity.objects.get(name=entity_instance.__class__.__name__)
#         entity_trees = EntityTree.objects.filter(entry_point__entity = e)
#         entities_and_trees.append([entity_instance, entity_trees])
    context = {'instance_list': instance_list}
    
    return render(request, 'entity/index.html', context)

def entity_index(request, entity_id):
    e = Entity.objects.get(pk=entity_id)
    instance_list = eval(e.name + ".objects.all()")
    context = {'instance_list': instance_list}
    
    return render(request, 'entity/index.html', context)

def detail(request, entity_id, application_id):
    if not request.user.is_authenticated():
        return redirect('/application/')
    else:
        entity = get_object_or_404(Entity, pk=entity_id)
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

def method(request, entity_id, application_id, method_id):
    # entity_id is 0 when the method creates an instance of entity
    entity = None
    if entity_id>0:
        entity = get_object_or_404(Entity, pk=entity_id)
    application = get_object_or_404(Application, pk=application_id)
    method = get_object_or_404(Method, pk=method_id)
    authenticated_user = request.user

    attrib_form = getForm(method)
    return render(request, 'entity/method.html', {'entity': entity, 'application': application, 'authenticated_user': authenticated_user, 'method': method, 'form': attrib_form})

def export(request, entity_tree_id, entity_instance_id, entity_id):
    e = Entity.objects.get(pk = entity_id)
    instance = eval('get_object_or_404(' + e.name + ', pk=' + str(entity_instance_id) + ')')
    et = EntityTree.objects.get(pk = entity_tree_id)
    exported_xml = instance.to_xml(et.entry_point)
    
    return render(request, 'entity/export.xml', {'xml': exported_xml}, content_type="application/xhtml+xml")
    
def upload_page(request):
    message = ''
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            xml_uploaded = request.FILES['file'].read()
            new_uploaded_file = UploadedFile(docfile = request.FILES['file'])
            # we save it on disk so that we can process it after the user has told us which part to import and how to import it
            new_uploaded_file.save()
            # we parse it so that we check what is on the file against what is on the database and we show this info to the user
            try:
                xmldoc = minidom.parseString(xml_uploaded)
                import_choice_form = ImportChoice(initial={'uploaded_file_id': new_uploaded_file.id, 'new_uploaded_file_relpath': new_uploaded_file.docfile.url})
                print "upload_page  " + xmldoc.toprettyxml(indent="    ") 
                return render(request, 'entity/import_file.html', {'prettyxml': xmldoc.toprettyxml(indent="    "),'file': request.FILES['file'], 'new_uploaded_file': new_uploaded_file, 'import_choice_form': import_choice_form})
            except Exception as ex:
                message = 'Error parsing uploaded file: ' + str(ex)
                print message
    else:
        form = UploadFileForm()
    return render_to_response('entity/upload_page.html', {'form': form, 'message': message}, context_instance=RequestContext(request))

def perform_import(request):
    new_uploaded_file_relpath = request.POST["new_uploaded_file_relpath"]
    # how_to_import = true ==> always_insert 
    always_insert = (int(request.POST.get("how_to_import", "")) == 1)
    import_methodology = request.POST.get("import_methodology", "")
    import_analysis = request.POST.get("import_analysis", "")
    with open(settings.BASE_DIR + "/" + new_uploaded_file_relpath, 'r') as content_file:
        xml_uploaded = content_file.read()
    xmldoc = minidom.parseString(xml_uploaded)
    # I assume there's only one
    methodology_version_xml = xmldoc.getElementsByTagName('MethodologyVersion')[0]
#         mv.from_xml(methodology_version_xml, always_insert)
    return HttpResponse("OK")
