#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'david'

from django.conf.urls import patterns, url

from ks import views

urlpatterns = patterns('',



    
    url(r'^ks_explorer_form/$', views.ks_explorer_form, name='ks_explorer_form'),
    url(r'^ks_explorer/$', views.ks_explorer, name='ks_explorer'),
    url(r'^browse_entity_instance/(?P<ks_url>[\w|=|%|.]+)/(?P<base64URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.browse_entity_instance, name='browse_entity_instance'),
    
                       ###################   API   ####################
    #33:
    url(r'^api/simple_entity_definition/(?P<base64_SimpleEntity_URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.api_simple_entity_definition, name='api_simple_entity_definition'), 
    #36:
    url(r'^api/entity_instance/(?P<base64_EntityInstance_URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.api_entity_instance, name='api_entity_instance'),
    #64: 
    url(r'^api/entity_instances/(?P<base64_Entity_URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.api_entity_instances, name='api_entity_instances'),
    #46:
    url(r'^api/entities/(?P<format>.*)/$', views.api_entities, name='api_entities'), 
    #80:
    url(r'^api/ks_info/(?P<base64_KS_URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.api_ks_info, name='ks_info'), 
                       ###################   API ^ ####################
    
)
#     url(r'^ks_explorer/(?P<ks_url>[\w|=|%|.]+)/$', views.ks_explorer, name='ks_explorer'),
