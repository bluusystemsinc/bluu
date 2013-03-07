from django.conf.urls import *
from rest_framework.urlpatterns import format_suffix_patterns
from .api_views import (DeviceListJson, DeviceHistoryListJson,
                        DeviceStatusCreateView)


urlpatterns = format_suffix_patterns(patterns('',
    url(
        r'^(?P<site_pk>[0-9]+)/devices/$',
        DeviceListJson.as_view(),
        name='api_device_list_json'),
    url(
        r'^(?P<site_pk>[0-9]+)/devices/(?P<pk>[0-9]+)/$',
        DeviceHistoryListJson.as_view(),
        name='api_device_history_list'),
    url(r'^(?P<_pk>[0-9]+)/$', DeviceStatusCreateView.as_view(),
        name='api_device_status_add'),
), allowed=['jsonp', 'json', 'html'])
