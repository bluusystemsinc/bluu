from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns

from . import ajax_views

urlpatterns = patterns('',
    url(r'^(?P<pk>[0-9]+)/alerts/configure[/]?$',
        ajax_views.UserAlertConfigSetView.as_view(),
        name='user_alert_config_set'),
    url(r'^(?P<pk>[0-9]+)/alerts/configure_weight[/]?$',
        ajax_views.UserAlertScaleConfigSetView.as_view(),
        name='user_alert_scale_config_set'),
    url(r'^(?P<pk>[0-9]+)/alerts/set_device[/]?$',
        ajax_views.UserAlertDeviceSetView.as_view(),
        name='user_alert_device_set'),
    url(r'^(?P<pk>[0-9]+)/alerts/set_room[/]?$',
        ajax_views.UserAlertRoomSetView.as_view(),
        name='user_alert_room_set'),
    url(r'^(?P<pk>[0-9]+)/alerts/set_scale[/]?$',
        ajax_views.UserAlertScaleSetView.as_view(),
        name='user_alert_scale_set'),
)
