from django.conf.urls import patterns, url
from . import views
from utils.views import WorkInProgressView
from . import views


urlpatterns = patterns('',
    url(r'^(?P<site_pk>\d+)/devices/$',
        views.DeviceListView.as_view(),
        name='device_list'),
    url(r'^(?P<site_pk>\d+)/devices/add/$',
        views.DeviceCreateView.as_view(),
        name='device_add'),
    url(r'^(?P<site_pk>\d+)/devices/(?P<pk>\d+)/$',
        views.DeviceUpdateView.as_view(),
        name='device_edit'),
    url(
        r'^(?P<site_pk>\d+)/devices/(?P<pk>\d+)/delete/$',
        views.device_delete,
        name='device_delete'),
)

