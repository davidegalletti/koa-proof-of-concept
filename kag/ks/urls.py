#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'david'

from django.conf.urls import patterns, url

from ks import views

urlpatterns = patterns('',
    url(r'^debug/$', views.debug),
    url(r'^cron/$', views.cron, name='cron'),
    url(r'^ks_explorer_form/$', views.ks_explorer_form, name='ks_explorer_form'),
    url(r'^ks_explorer/$', views.ks_explorer, name='ks_explorer'),
    url(r'^browse_entity_instance/(?P<ks_url>[\w|=|%|.]+)/(?P<base64URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.browse_entity_instance, name='browse_entity_instance'),
    url(r'^disclaimer/$', views.disclaimer, name="disclaimer"),
    url(r'^subscriptions/$', views.subscriptions, name="subscriptions"),
    url(r'^this_ks_subscribes_to/(?P<base64_URIInstance>[\w|=|%|.]+)/$', views.this_ks_subscribes_to, name='this_ks_subscribes_to'),
    url(r'^this_ks_unsubscribes_to/(?P<base64_URIInstance>[\w|=|%|.]+)/$', views.this_ks_unsubscribes_to, name='this_ks_unsubscribes_to'),
    
                       ###################   API   ####################
    url(r'^api/root_uri/(?P<base64_URIInstance>[\w|=|%|.]+)/$', views.api_root_uri, name='api_root_uri'),
    #33:
    url(r'^api/simple_entity_definition/(?P<base64_SimpleEntity_URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.api_simple_entity_definition, name='api_simple_entity_definition'), 
    #36:
    url(r'^api/entity_instance/(?P<base64_EntityInstance_URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.api_entity_instance, name='api_entity_instance'),
    #64: 
    url(r'^api/entity_instances/(?P<base64_EntityStructure_URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.api_entity_instances, name='api_entity_instances'),
    #46:
    url(r'^api/entity_structures/(?P<format>.*)/$', views.api_entity_structures, name='api_entity_structures'), 
    #52
    url(r'^api/entity_instance_info/(?P<base64_EntityInstance_URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.api_entity_instance_info, name='api_entity_instance_info'),
    #80:
    url(r'^api/ks_info/(?P<format>.*)/$', views.api_ks_info, name='api_ks_info'), 
    #110
    url(r'^api/export_instance/(?P<base64_EntityInstance_URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.api_export_instance, name='api_export_instance'),
    #35 
    url(r'^api/subscribe/(?P<base64_URIInstance>[\w|=|%|.]+)/(?P<base64_remote_url>[\w|=|%|.]+)/$', views.api_subscribe, name='api_subscribe'),
    #123
    url(r'^api/unsubscribe/(?P<base64_URIInstance>[\w|=|%|.]+)/(?P<base64_URL>[\w|=|%|.]+)/$', views.api_unsubscribe, name='api_unsubscribe'),
    #37 
    url(r'^api/notify/$', views.api_notify, name='api_notify'),
                       ###################   API ^ ####################
    
)
