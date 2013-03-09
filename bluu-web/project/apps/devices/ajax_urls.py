from django.conf.urls import patterns, url

from .ajax_views import (DeviceListJson, DeviceHistoryListJson)


urlpatterns = patterns('',
    url(r'^dt/$',
        DeviceListJson.as_view(),
        name='ajax_device_list_dt'),
    url(r'^(?P<pk>[0-9]+)/statuses/dt/$',
        DeviceHistoryListJson.as_view(),
        name='ajax_device_statuses_list_dt'),
)
