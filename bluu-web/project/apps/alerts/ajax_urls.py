from django.conf.urls import *

from rest_framework.urlpatterns import format_suffix_patterns

from . import ajax_views

urlpatterns = patterns('',
    # sites
    url(r'^(?P<pk>[0-9]+)/alerts/set[/]?$',
        ajax_views.AlertCfgCreateView.as_view(),
        name='api_site_access'),
)
