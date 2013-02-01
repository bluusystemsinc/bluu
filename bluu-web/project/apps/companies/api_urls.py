from django.conf.urls.defaults import *
from rest_framework.urlpatterns import format_suffix_patterns
from .api_views import CompanyList, CompanyDetail,\
        CompanyAccessList, CompanyAccessGroups,\
        CompanySiteList


urlpatterns = format_suffix_patterns(patterns('',
    url(r'^$', CompanyList.as_view(), name='api-company-list'),
    url(r'^(?P<pk>[0-9]+)[/]?$', CompanyDetail.as_view(),
        name='api-company-details'),
    url(r'^(?P<pk>[0-9]+)/access[/]?$', CompanyAccessList.as_view(),
        name='api-company-access'),
    url(r'^(?P<pk>[0-9]+)/access/groups[/]?$', CompanyAccessGroups.as_view(),
        name='api-company-access-groups'),
    url(r'^(?P<company>[0-9]+)/sites[/]?$', CompanySiteList.as_view(),
        name='api-company-site-list'),
), allowed=['jsonp', 'json', 'html'])
