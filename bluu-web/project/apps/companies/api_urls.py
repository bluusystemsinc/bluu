from django.conf.urls import *
from rest_framework.urlpatterns import format_suffix_patterns
from .api_views import CompanyList, CompanyDetail,\
        CompanyAccessList, CompanyAccessListJson, CompanyAccessGroups,\
        CompanySiteListJson


urlpatterns = format_suffix_patterns(patterns('',
    url(r'^$', CompanyList.as_view(), name='api-company-list'),
    url(r'^(?P<pk>[0-9]+)[/]?$', CompanyDetail.as_view(),
        name='api-company-details'),
    url(r'^(?P<company_pk>[0-9]+)/access\.json[/]?$', CompanyAccessListJson.as_view(),
        name='api_company_access_json'),
    url(r'^(?P<pk>[0-9]+)/access[/]?$', CompanyAccessList.as_view(),
        name='api_company_access'),
    url(r'^(?P<pk>[0-9]+)/access/groups[/]?$', CompanyAccessGroups.as_view(),
        name='api-company-access-groups'),
    #url(r'^(?P<company>[0-9]+)/sites[/]?$', CompanySiteList.as_view(),
    #    name='api-company-site-list'),
    url(r'^(?P<company_pk>[0-9]+)/sites\.json[/]?$', CompanySiteListJson.as_view(),
        name='api-company-site-list-json'),
), allowed=['jsonp', 'json', 'html'])
