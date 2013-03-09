from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = format_suffix_patterns(patterns('',
    #url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    #url(r'^sites/', include('bluusites.api_urls', namespace='sites')),
    #url(r'^companies/', include('companies.api_urls', namespace='companies')),
    #url(r'^devices/', include('devices.api_urls', namespace='devices')),
    url(r'^sites/(?P<site_slug>[\w.@+-]+)/devices/(?P<device_pk>[0-9]+)/statuses/',
        views.DeviceStatusCreateView.as_view(),
        name='create_status'),
    ), allowed=['json', 'html']
)

