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
    url(r'^browse_dataset/(?P<ks_url>[\w|=|%|.]+)/(?P<base64URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.browse_dataset, name='browse_dataset'),
    url(r'^disclaimer/$', views.disclaimer, name="disclaimer"),
    url(r'^subscriptions/$', views.subscriptions, name="subscriptions"),
    url(r'^this_ks_subscribes_to/(?P<base64_URIInstance>[\w|=|%|.]+)/$', views.this_ks_subscribes_to, name='this_ks_subscribes_to'),
    url(r'^this_ks_unsubscribes_to/(?P<base64_URIInstance>[\w|=|%|.]+)/$', views.this_ks_unsubscribes_to, name='this_ks_unsubscribes_to'),
    url(r'^redirect_to_base64_oks_url/(?P<base64_oks_URIInstance>[\w|=|%|.]+)/$', views.redirect_to_base64_oks_url, name='redirect_to_base64_oks_url'),
    url(r'^release_dataset/(?P<base64_Dataset_URIInstance>[\w|=|%|.]+)/$', views.release_dataset, name='release_dataset'),

                       ###################   API   ####################
    url(r'^api/root_uri/(?P<base64_URIInstance>[\w|=|%|.]+)/$', views.api_root_uri, name='api_root_uri'),
    #33:
    url(r'^api/simple_entity_definition/(?P<base64_SimpleEntity_URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.api_simple_entity_definition, name='api_simple_entity_definition'), 
    #36:
    url(r'^api/dataset/(?P<base64_DataSet_URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.api_dataset, name='api_dataset'),
    #64: 
    url(r'^api/datasets/(?P<base64_DataSetStructure_URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.api_datasets, name='api_datasets'),
    #46:
    url(r'^api/dataset_types/(?P<format>.*)/$', views.api_dataset_types, name='api_dataset_types'), 
    #52
    url(r'^api/dataset_info/(?P<base64_DataSet_URIInstance>[\w|=|%|.]+)/(?P<format>.*)/$', views.api_dataset_info, name='api_dataset_info'),
    #80:
    url(r'^api/ks_info/(?P<format>.*)/$', views.api_ks_info, name='api_ks_info'), 
    #35 
    url(r'^api/subscribe/(?P<base64_URIInstance>[\w|=|%|.]+)/(?P<base64_remote_url>[\w|=|%|.]+)/$', views.api_subscribe, name='api_subscribe'),
    #123
    url(r'^api/unsubscribe/(?P<base64_URIInstance>[\w|=|%|.]+)/(?P<base64_URL>[\w|=|%|.]+)/$', views.api_unsubscribe, name='api_unsubscribe'),
    #37 
    url(r'^api/notify/$', views.api_notify, name='api_notify'),
                       ###################   API ^ ####################
    
)
