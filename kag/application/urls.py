from django.conf.urls import patterns, url

from application import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<application_id>\d+)/$', views.detail, name='detail'),
    url(r'^klogin/(?P<username>\w+)/(?P<password>\w+)/$', views.klogin, name='klogin'),
)

