from django.conf.urls.defaults import patterns, include, url
from djangorestframework.resources import ModelResource
from djangorestframework.views import ListOrCreateModelView, InstanceModelView
from bluuserver.clients.models import Client

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

class ClientResource(ModelResource):
	model = Client

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bluuserver.views.home', name='home'),
    # url(r'^bluuserver/', include('bluuserver.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('djangorestframework.urls', namespace='djangorestframework')),
    url(r'^$', ListOrCreateModelView.as_view(resource=ClientResource)),
    url(r'^(?P<pk>[^/]+)/$', InstanceModelView.as_view(resource=ClientResource)),
)
