from django.conf.urls import *
from rest_framework.urlpatterns import format_suffix_patterns
from .api_views import DeviceListJson


urlpatterns = format_suffix_patterns(patterns('',
    url(
        r'^(?P<site_pk>[0-9]+)/devices/$',
        DeviceListJson.as_view(),
        name='api_device_list_json'),
), allowed=['jsonp', 'json', 'html'])
