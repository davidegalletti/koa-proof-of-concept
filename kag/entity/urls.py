from django.conf.urls import patterns, url

from entity import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<entity_id>\d+)/(?P<application_id>\d+)/$', views.detail, name='detail'),
)

