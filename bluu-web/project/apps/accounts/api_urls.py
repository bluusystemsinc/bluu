from django.conf.urls.defaults import *
from accounts.api_views import SiteList, CompanyList, CompanyDetail,\
        CompanyAccessList, CompanyAccessGroups, SiteAccessList, SiteAccessGroups
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = format_suffix_patterns(patterns('accounts.api_views',
    url(r'^companies[/]$', CompanyList.as_view(), name='api-company-list'),
    url(r'^companies/(?P<pk>[0-9]+)[/]?$', CompanyDetail.as_view(),
        name='api-company-details'),
    url(r'^companies/(?P<pk>[0-9]+)/access[/]?$', CompanyAccessList.as_view(),
        name='api-company-access'),
    url(r'^companies/(?P<pk>[0-9]+)/access/groups[/]?$', CompanyAccessGroups.as_view(),
        name='api-company-access-groups'),
    url(r'^sites[/]$', SiteList.as_view(), name='api-site-list'),
    url(r'^sites/(?P<pk>[0-9]+)/access[/]?$', SiteAccessList.as_view(),
        name='api-site-access'),
    url(r'^sites/(?P<pk>[0-9]+)/access/groups[/]?$', SiteAccessGroups.as_view(),
        name='api-site-access-groups'),
), allowed=['jsonp', 'json', 'html'])
