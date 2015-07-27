from django import template
from entity.models import KnowledgeServer 
register = template.Library()

@register.simple_tag
def ks_info(ks, *args, **kwargs):
    return "<p>Name: <a href=\"" + ks.scheme + "://" + ks.netloc + "/\" target=\"_blank\">" + ks.name + "</a><br>Organization: <a href=\"" + ks.organization.website + "\" target=\"_blank\">" + ks.organization.name + "</a></p>"