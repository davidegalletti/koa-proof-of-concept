import base64
import json
from django import template
from django.core.urlresolvers import reverse
from entity.models import KnowledgeServer 
register = template.Library()

@register.simple_tag
def ks_info(ks, *args, **kwargs):
    ret_html = "<p>" + ks.name
    if hasattr(ks, "organization"):
        ret_html += '<br>Maintained by "<a href="' + ks.organization.website + '" target="_blank">' + ks.organization.name + '</a>"'
    ret_html += '<br><a href="' + ks.uri() + '/" target="_blank">' + ks.uri() + '</a>'
    
    return ret_html

@register.simple_tag
def version_instance_info(dataset, instances, *args, **kwargs):
    base64_DataSet_URIInstance = base64.encodestring(dataset.URIInstance).replace('\n','')
    ret_string = ''
    for instance in instances:
        ret_string +=  '<p>"' + instance.name + '" (<a href="' + reverse('api_dataset', args=(base64_DataSet_URIInstance,"html")) + '">browse the data</a> or'
        ret_string += ' get it in <a href="' + reverse('api_dataset', args=(base64_DataSet_URIInstance,"XML")) + '">XML</a> or '
        ret_string += '<a href="' + reverse('api_dataset', args=(base64_DataSet_URIInstance,"JSON")) + '">JSON</a>)<br>'
        ret_string += 'Version ' + ('' if dataset.version_released else '(<font color="red">not released</font>) ') + str(dataset.version_major) + '.' + str(dataset.version_minor) + '.' + str(dataset.version_patch) + ' - ' + str(dataset.version_date)
        if not dataset.licenses is None:
            ret_string += '<br>Licenses: '
        for l in dataset.licenses.all():
            ret_string += '<br> ' + l.name
        if dataset.version_released:
            ret_string += '</p>'
        else:  
            ret_string += '<br>Click <a href="' + reverse('release_dataset', args=(base64_DataSet_URIInstance,)) + '" target="_blank">here</a> to release it.</p>'
    return ret_string

@register.simple_tag
def browse_json_data(actual_instance, exported_json, esn, *args, **kwargs):
    json_data = json.loads(exported_json)[esn.simple_entity.name]
    
    return json_to_html(actual_instance, json_data, esn)

def json_to_html(actual_instance, json_data, esn, indent_level=0):
    try:
        ret_html = ""
        if esn.attribute == "":
            # no attribute, I am at the entry point
            ret_html = (indent_level * "--&nbsp;") + " " + esn.simple_entity.name + ': "<a href="' + json_data["URIInstance"] + '">' + json_data[esn.simple_entity.name_field] +'</a>"<br>'
            ret_html += actual_instance.serialized_attributes(format = 'HTML')
        else:
            if esn.is_many:
                json_children = json_data[esn.attribute]
                esn.attribute = ""
                for json_child in json_children:
                    ext_json_child = {}
                    ext_json_child[esn.simple_entity.name] = json_child
                    ret_html += json_to_html(ext_json_child, esn, indent_level)
                return ret_html
            else:
                # there exist simple entities with no name
                try:
                    name = json_data[esn.simple_entity.name_field]
                except:
                    name = ""
                if name == "":
                    name = esn.attribute
                ret_html = (indent_level * "--&nbsp;") + " " + esn.simple_entity.name + ': "<a href="' + json_data["URIInstance"] + '">' + name +'</a>"<br>'
        indent_level+=1
        for esn_child_node in esn.child_nodes.all():
            try:
                if esn_child_node.attribute == "":
                    ret_html += json_to_html(json_data, esn_child_node, indent_level)
                else:
                    ret_html += json_to_html(json_data[esn_child_node.attribute], esn_child_node, indent_level)
            except:
                pass
        return ret_html
    except Exception as e:
        return ""