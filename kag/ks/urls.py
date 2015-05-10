#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'david'

from django.conf.urls import patterns, url

from ks import views

urlpatterns = patterns('',
    url(r'^api/simple_entity_definition/(?P<base64URISimpleEntity>[\w|=|%|.]+)/$', views.api_simple_entity_info, name='api_simple_entity_definition'),
    url(r'^api/entity_instance/(?P<base64URIInstance>[\w|=|%|.]+)/$', views.api_entity_instance, name='api_entity_instance'),
)
