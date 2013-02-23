from django.conf.urls import patterns, url
from . import views
from utils.views import WorkInProgressView
from .views import DeviceListView


urlpatterns = patterns('',
    url(
        r'^(?P<site_pk>\d+)/devices/$',
        DeviceListView.as_view(),
        name='device_list'),
)

