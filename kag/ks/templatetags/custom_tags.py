import base64
import json
from django import template
from django.core.urlresolvers import reverse
from entity.models import KnowledgeServer 
register = template.Library()

@register.simple_tag
def ks_info(ks, *args, **kwargs):
    return "<p>Name: <a href=\"" + ks.scheme + "://" + ks.netloc + "/\" target=\"_blank\">" + ks.name + "</a><br>Organization: <a href=\"" + ks.organization.website + "\" target=\"_blank\">" + ks.organization.name + "</a></p>"

@register.simple_tag
def version_instance_info(entity_instance, instance, *args, **kwargs):
    base64_EntityInstance_URIInstance = base64.encodestring(entity_instance.URIInstance).rstrip('\n')
    ret_string =  '<p>"' + instance.name + '" (<a href="' + reverse('api_export_instance', args=(base64_EntityInstance_URIInstance,"html")) + '">browse</a> the data or'
    ret_string += ' get it in <a href="' + reverse('api_export_instance', args=(base64_EntityInstance_URIInstance,"html")) + '">XML</a> or '
    ret_string += '<a href="' + reverse('api_export_instance', args=(base64_EntityInstance_URIInstance,"html")) + '">JSON</a>)<br>'
    ret_string += 'Version ' + str(entity_instance.version_major) + '.' + str(entity_instance.version_minor) + '.' + str(entity_instance.version_patch) + ' - ' + str(entity_instance.version_date) + '</p>'
    return ret_string

@register.simple_tag
def browse_json_data(exported_json, esn, *args, **kwargs):
    json_data = json.loads(exported_json)['Export'][esn.simple_entity.name]
    
    return json_to_html(json_data, esn)

def json_to_html(json_data, esn, indent_level=0):
    try:
        ret_html = ""
        if esn.attribute == "":
            # no attribute, I am at the entry point
            ret_html = (indent_level * "--&nbsp;") + " " + esn.simple_entity.name + ': "<a href="' + json_data["URIInstance"] + '">' + json_data[esn.simple_entity.name_field] +'</a>"<br>'
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