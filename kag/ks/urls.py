#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'david'

from django.conf.urls import patterns, url

from ks import views

urlpatterns = patterns('',
    url(r'^api/simple_entity_definition/(?P<base64URISimpleEntity>[\w|=|%|.]+)/$', views.api_simple_entity_definition, name='api_simple_entity_definition'),
    url(r'^api/entity_instance/(?P<base64URIInstance>[\w|=|%|.]+)/$', views.api_entity_instance, name='api_entity_instance'),
    url(r'^api/entity_instances/(?P<base64URIInstance>[\w|=|%|.]+)/$', views.api_entity_instances, name='api_entity_instances'),
    url(r'^api/entities/$', views.api_entities, name='api_entities'),
)
