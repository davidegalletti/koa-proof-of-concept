from django.conf.urls import patterns, url

from entity import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<entity_id>\d+)/$', views.entity_index, name='entity_index'),
    url(r'^(?P<entity_id>\d+)/(?P<application_id>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<entity_id>\d+)/(?P<application_id>\d+)/(?P<method_id>\d+)/$', views.method, name='method'),
    url(r'^export/(?P<entity_id>\d+)/(?P<entity_instance_id>\d+)/(?P<simple_entity_id>\d+)/$', views.export, name='export'),
    url(r'^export_stub/(?P<entity_id>\d+)/$', views.export_stub, name='export_stub'),
    url(r'^upload_page', views.upload_page, name='upload_page'),
    url(r'^perform_import', views.perform_import, name='perform_import'),
    url(r'^entity_stub/(?P<entity_id>\d+)/$', views.entity_stub, name='entity_stub'),
)
