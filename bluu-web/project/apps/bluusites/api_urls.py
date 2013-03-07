from django.conf.urls import *

from rest_framework.urlpatterns import format_suffix_patterns

from .api_views import (BluuSiteListJson, BluuSiteAccessListJson,
                        BluuSiteAccessCreateView, BluuSiteAccessUpdateView,
                        RoomListJson)
from devices.api_views import (DeviceListJson, DeviceHistoryListJson)

urlpatterns = (patterns('',
     url(
        r'^',
        include('devices.api_urls')),       
     )
)

urlpatterns += format_suffix_patterns(patterns('',
    url(
        r'^\.json[/]*$',
        BluuSiteListJson.as_view(),
        name='api_site_list_json'),
    url(
        r'^(?P<pk>[0-9]+)/access\.json[/]*?$',
        BluuSiteAccessListJson.as_view(),
        name='api_site_access_list_json'),
    url(
        r'^(?P<pk>[0-9]+)/access[/]?$',
        BluuSiteAccessCreateView.as_view(),
        name='api_site_access'),
    url(
        r'^(?P<site_pk>[0-9]+)/access/(?P<pk>[0-9]+)[/]?$',
        BluuSiteAccessUpdateView.as_view(),
        name='api_site_access_json'),
    url(
        r'^(?P<site_pk>[0-9]+)/rooms/$',
        RoomListJson.as_view(),
        name='api_room_list_json'),
    url(
        r'^(?P<site_pk>[0-9]+)/devices/$',
        DeviceListJson.as_view(),
        name='api_device_list_json'),
    url(
        r'^(?P<site_pk>[0-9]+)/devices/(?P<pk>[0-9]+)/$',
        DeviceHistoryListJson.as_view(),
        name='api_device_history_list'),
), allowed=['jsonp', 'json', 'html'])
