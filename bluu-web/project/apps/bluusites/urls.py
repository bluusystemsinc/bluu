from django.conf.urls import patterns, url, include

from . import views


urlpatterns = patterns('',
    url(r'^$', views.SiteListView.as_view(), name='site_list'),
    url(r'^add/$', views.SiteCreateView.as_view(), name='site_add'),
    url(r'^(?P<pk>\d+)/$',
        views.SiteUpdateView.as_view(), name='site_edit'),
    url(r'^(?P<pk>\d+)/access/$',
        views.SiteAccessListView.as_view(),
        name='site_access'),
    url(r'^(?P<pk>\d+)/delete/$',
        views.site_delete,
        name='site_delete'),
    url(r'^(?P<site_pk>\d+)/rooms/$',
        views.RoomListView.as_view(),
        name='room_list'),
    url(r'^(?P<site_pk>\d+)/rooms/add/$',
        views.RoomCreateView.as_view(),
        name='room_add'),
    url(r'^(?P<site_pk>\d+)/rooms/(?P<pk>\d+)/$',
        views.RoomUpdateView.as_view(),
        name='room_edit'),
    url(r'^(?P<site_pk>\d+)/rooms/(?P<pk>\d+)/delete/$',
        views.room_delete,
        name='room_delete'),
    url(r'^', include('bluusites.ajax_urls')),
    url(r'^', include('devices.urls', namespace='site_devices')),
)

# ajax views
#urlpatterns += patterns('',
#    # sites
#    url(r'^\.json[/]*$',
#        ajax_views.BluuSiteListJson.as_view(),
#        name='api_site_list_json'),
#    url(r'^(?P<pk>[0-9]+)/access\.json[/]*?$',
#        ajax_views.BluuSiteAccessListJson.as_view(),
#        name='api_site_access_list_json'),
#    url(r'^(?P<pk>[0-9]+)/access[/]?$',
#        ajax_views.BluuSiteAccessCreateView.as_view(),
#        name='api_site_access'),
#    url(r'^(?P<site_pk>[0-9]+)/access/(?P<pk>[0-9]+)[/]?$',
#        ajax_views.BluuSiteAccessUpdateView.as_view(),
#        name='api_site_access_json'),
#
#    # rooms
#    url(r'^(?P<site_pk>[0-9]+)/rooms/dt/$',
#        ajax_views.RoomListJson.as_view(),
#        name='ajax_room_list_bt'),
#
#    # devices
#    url(r'^(?P<site_pk>[0-9]+)/devices/',
#        include('devices.ajax_urls', namespace="devices", app_name="devices"))
#
#   #    devices_ajax_views.DeviceListJson.as_view(),
#   #     name='api_device_list_dt'),
#   # url(r'^(?P<site_pk>[0-9]+)/devices/(?P<pk>[0-9]+)/statuses/dt/$',
#   #     devices_ajax_views.DeviceHistoryListJson.as_view(),
#   #     name='api_device_history_list_dt'),
#    #url(r'^(P<site_slug>[\w.@+-]+)/devices/(?P<pk>[0-9]+)/statuses/$',
#    #    devices_ajax_views.DeviceStatusCreateView.as_view(),
#    #    name='api_device_status_add'),
#)        
