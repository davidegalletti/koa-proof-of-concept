#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'david'

from django.conf.urls import patterns, url

from ks import views

urlpatterns = patterns('',


                       ###################   API   ####################
    #33:
    url(r'^api/simple_entity_definition/(?P<format>.*)/(?P<base64URISimpleEntity>[\w|=|%|.]+)/$', views.api_simple_entity_definition, name='api_simple_entity_definition'), 
    #36:
    url(r'^api/entity_instance/(?P<format>.*)/(?P<base64URIInstance>[\w|=|%|.]+)/$', views.api_entity_instance, name='api_entity_instance'),
    #64: 
    url(r'^api/entity_instances/(?P<format>.*)/(?P<base64URIInstance>[\w|=|%|.]+)/$', views.api_entity_instances, name='api_entity_instances'),
    #46:
    url(r'^api/entities/(?P<format>.*)/$', views.api_entities, name='api_entities'), 
                       ###################   API ^ ####################

    
    url(r'^ks_explorer_form/$', views.ks_explorer_form, name='ks_explorer_form'),
    url(r'^ks_explorer/$', views.ks_explorer, name='ks_explorer'),
)
#     url(r'^ks_explorer/(?P<ks_url>[\w|=|%|.]+)/$', views.ks_explorer, name='ks_explorer'),
