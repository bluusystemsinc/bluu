from django.conf.urls import *

from rest_framework.urlpatterns import format_suffix_patterns

from .ajax_views import (BluuSiteListJson, BluuSiteAccessListJson,
                        BluuSiteAccessCreateView, BluuSiteAccessUpdateView,
                        RoomListJson)
from devices.ajax_views import (DeviceListJson, DeviceHistoryListJson)

from . import ajax_views

urlpatterns = patterns('',
    # sites
    url(r'^\.json[/]*$',
        ajax_views.BluuSiteListJson.as_view(),
        name='api_site_list_json'),
    url(r'^(?P<pk>[0-9]+)/access\.json[/]*?$',
        ajax_views.BluuSiteAccessListJson.as_view(),
        name='api_site_access_list_json'),
    url(r'^(?P<pk>[0-9]+)/access[/]?$',
        ajax_views.BluuSiteAccessCreateView.as_view(),
        name='api_site_access'),
    url(r'^(?P<site_pk>[0-9]+)/access/(?P<pk>[0-9]+)[/]?$',
        ajax_views.BluuSiteAccessUpdateView.as_view(),
        name='api_site_access_json'),

    # rooms
    url(r'^(?P<site_pk>[0-9]+)/rooms/dt/$',
        ajax_views.RoomListJson.as_view(),
        name='ajax_room_list_bt'),

    # devices
    url(r'^(?P<site_pk>[0-9]+)/devices/',
        include('devices.ajax_urls'))

)
