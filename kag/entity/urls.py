from django.conf.urls import patterns, url

from entity import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^index/(?P<entity_id>\d+)/$', views.entity_index, name='entity_index'),
    url(r'^(?P<entity_id>\d+)/(?P<application_id>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<entity_id>\d+)/(?P<application_id>\d+)/(?P<method_id>\d+)/$', views.method, name='method'),
    url(r'^export/(?P<entity_tree_id>\d+)/(?P<entity_instance_id>\d+)/(?P<entity_id>\d+)/$', views.export, name='export'),
)

