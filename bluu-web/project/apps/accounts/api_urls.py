from django.conf.urls.defaults import *
from views import register, UserProfileUpdateView,\
                  UserProfileCreateView, AccountUpdateView,\
                  AccountDeleteView, CompanyListView, CompanyCreateView,\
                  CompanyUpdateView, company_delete,\
                  SiteListView, SiteCreateView,\
                  SiteUpdateView, site_delete,\
                  SiteUserListView, SiteUserCreateView,\
                  SiteUserUpdateView
from accounts.api_views import SiteList, CompanyList, CompanyDetail,\
        CompanyAccessList, CompanyAccessGroups
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = format_suffix_patterns(patterns('accounts.api_views',
    url(r'^sites/$', SiteList.as_view(), name='api-site-list'),
    url(r'^companies[/]$', CompanyList.as_view(), name='api-company-list'),
    url(r'^companies/(?P<pk>[0-9]+)[/]?$', CompanyDetail.as_view(),
        name='api-company-details'),
    url(r'^companies/(?P<pk>[0-9]+)/access[/]?$', CompanyAccessList.as_view(),
        name='api-company-access'),
    url(r'^companies/(?P<pk>[0-9]+)/access/groups[/]?$', CompanyAccessGroups.as_view(),
        name='api-company-access-groups'),
), allowed=['jsonp', 'json', 'html'])
