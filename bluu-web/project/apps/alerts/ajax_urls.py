from django.conf.urls import *

from rest_framework.urlpatterns import format_suffix_patterns

from . import ajax_views

urlpatterns = patterns('',
    url(r'^(?P<pk>[0-9]+)/alerts/configure[/]?$',
        ajax_views.UserAlertConfigSetView.as_view(),
        name='user_alert_config_set'),
    url(r'^(?P<pk>[0-9]+)/alerts/set[/]?$',
        ajax_views.UserAlertDeviceSetView.as_view(),
        name='user_alert_device_set'),
)
