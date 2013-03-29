from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = format_suffix_patterns(patterns('',
    #url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    #url(r'^sites/', include('bluusites.api_urls', namespace='sites')),
    #url(r'^companies/', include('companies.api_urls', namespace='companies')),
    #url(r'^devices/', include('devices.api_urls', namespace='devices')),
    url(r'^sites/(?P<site_slug>[0-9\w.@+-]+)/devices/(?P<device_slug>[0-9\w.@+-]+)/statuses/',
        views.DeviceStatusCreateView.as_view(),
        name='create_status'),
    url(r'^sites/(?P<site_slug>[0-9\w.@+-]+)/',
        views.SiteHeartBeatView.as_view(),
        name='site_heartbeat'),
    ), allowed=['json', 'html']

)

