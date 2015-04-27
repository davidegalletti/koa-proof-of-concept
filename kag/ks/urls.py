#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'david'

from django.conf.urls import patterns, url

from ks import views

urlpatterns = patterns('',
    url(r'^simple_entity_info/(?P<base64URISimpleEntity>[\w|=|%|.]+)/$', views.simple_entity_info, name='simple_entity_info'),
)
