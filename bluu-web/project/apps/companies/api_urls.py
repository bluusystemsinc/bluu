from django.conf.urls import *
from rest_framework.urlpatterns import format_suffix_patterns
from .api_views import (CompanyAccessCreateView, CompanyAccessListJson,
                        CompanySiteListJson, CompanyAccessUpdateView,
                        CompanyAccessListCreateView)


urlpatterns = format_suffix_patterns(patterns('',
    url(r'^(?P<company_pk>[0-9]+)/access\.json[/]?$', CompanyAccessListJson.as_view(),
        name='api_company_access_list_json'),

    #url(r'^(?P<company_pk>[0-9]+)/access\.json[/]?$', CompanyAccessListCreateView.as_view(),
    #    name='api_company_access_list_json'),

    url(r'^(?P<company_pk>[0-9]+)/generic_access/$', CompanyAccessListCreateView.as_view(),
        name='api_company_generic_access_list_json'),
    url(r'^(?P<company_pk>[0-9]+)/access[/]?$', CompanyAccessCreateView.as_view(),
        name='api_company_access'),
    url(r'^(?P<company_pk>[0-9]+)/access/(?P<pk>[0-9]+)[/]?$', CompanyAccessUpdateView.as_view(),
        name='api_company_access_json'),
    url(r'^(?P<company_pk>[0-9]+)/sites\.json[/]?$', CompanySiteListJson.as_view(),
        name='api_company_site_list_json'),
), allowed=['jsonp', 'json', 'html'])
