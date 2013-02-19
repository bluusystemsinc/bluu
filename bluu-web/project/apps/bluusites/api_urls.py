from django.conf.urls import *
from rest_framework.urlpatterns import format_suffix_patterns
from .api_views import (BluuSiteListJson, BluuSiteAccessListJson,
                        BluuSiteAccessCreateView, BluuSiteAccessUpdateView)


urlpatterns = format_suffix_patterns(patterns('',
    #url(r'^$', SiteList.as_view(), name='api-site-list'),
    url(r'^\.json[/]*$', BluuSiteListJson.as_view(), name='api_site_list_json'),
    url(r'^(?P<pk>[0-9]+)/access\.json[/]*?$', BluuSiteAccessListJson.as_view(),
        name='api_site_access_list_json'),
    url(r'^(?P<pk>[0-9]+)/access[/]?$', BluuSiteAccessCreateView.as_view(),
        name='api_site_access'),
    url(r'^(?P<site_pk>[0-9]+)/access/(?P<pk>[0-9]+)[/]?$', BluuSiteAccessUpdateView.as_view(),
        name='api_site_access_json'),

), allowed=['jsonp', 'json', 'html'])
