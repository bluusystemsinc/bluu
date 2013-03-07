from django.conf.urls import patterns, url, include

from utils.views import WorkInProgressView
from devices.views import DeviceListView
from . import views


urlpatterns = patterns('',
    url(r'^$', views.SiteListView.as_view(), name='site_list'),
    url(r'^add/$', views.SiteCreateView.as_view(), name='site_add'),
    url(r'^(?P<pk>\d+)/$',\
            views.SiteUpdateView.as_view(), name='site_edit'),
    #url(r'^(?P<pk>\d+)/access/$',\
    #        views.SiteAccessManagementView.as_view(), name='site_access'),
    url(
        r'^(?P<pk>\d+)/access/$',\
        views.SiteAccessListView.as_view(),
        name='site_access'),
    url(
        r'^(?P<pk>\d+)/delete/$',
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
    url(
        r'^(?P<site_pk>\d+)/rooms/(?P<pk>\d+)/delete/$',
        views.room_delete,
        name='room_delete'),
    url(r'^', include('devices.urls', namespace='site_devices')),
)

