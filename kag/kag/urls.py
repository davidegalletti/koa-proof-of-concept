from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'ks.views.home', name='home'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^application/', include('application.urls')),
    url(r'^ks/', include('ks.urls')),
    url(r'^entity/', include('entity.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<uri_instance>.*)/$', 'ks.views.api_catch_all', name='api_catch_all'), 
)
