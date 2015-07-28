import json
from django import template
from entity.models import KnowledgeServer 
register = template.Library()

@register.simple_tag
def ks_info(ks, *args, **kwargs):
    return "<p>Name: <a href=\"" + ks.scheme + "://" + ks.netloc + "/\" target=\"_blank\">" + ks.name + "</a><br>Organization: <a href=\"" + ks.organization.website + "\" target=\"_blank\">" + ks.organization.name + "</a></p>"

@register.simple_tag
def browse_json_data(exported_json, etn, *args, **kwargs):
    json_data = json.loads(exported_json)['Export']
    
    return json_to_html(json_data, etn)

def json_to_html(json_data, esn, indent_level=0):
    try:
        ret_html = ""
        if esn.attribute == "":
            # no attribute, I am at the entry point
            ret_html = (indent_level * "--&nbsp;") + " " + esn.simple_entity.name + ': "<a href="' + json_data[esn.simple_entity.name]["URIInstance"] + '">' + json_data[esn.simple_entity.name][esn.simple_entity.name_field] +'</a>"<br>'
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
                ret_html = (indent_level * "--&nbsp;") + " " + esn.simple_entity.name + ': "<a href="' + json_data["URIInstance"] + '">' + name +'</a>"<br>'
        indent_level+=1
        for esn_child_node in esn.child_nodes.all():
            ret_html += json_to_html(json_data[esn.simple_entity.name], esn_child_node, indent_level)
        return ret_html
    except Exception as e:
        return ""