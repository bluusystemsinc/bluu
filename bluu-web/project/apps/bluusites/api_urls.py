from django.conf.urls.defaults import *
from rest_framework.urlpatterns import format_suffix_patterns
from .api_views import SiteList, SiteAccessList, SiteAccessGroups


urlpatterns = format_suffix_patterns(patterns('',
    url(r'^$', SiteList.as_view(), name='api-site-list'),
    url(r'^(?P<pk>[0-9]+)/access[/]?$', SiteAccessList.as_view(),
        name='api-site-access'),
    url(r'^(?P<pk>[0-9]+)/access/groups[/]?$', SiteAccessGroups.as_view(),
        name='api-site-access-groups'),
), allowed=['jsonp', 'json', 'html'])
