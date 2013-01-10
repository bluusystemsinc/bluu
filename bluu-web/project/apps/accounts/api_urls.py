from django.conf.urls.defaults import *
from views import register, UserProfileUpdateView,\
                  UserProfileCreateView, AccountUpdateView,\
                  AccountDeleteView, CompanyListView, CompanyCreateView,\
                  CompanyUpdateView, company_delete,\
                  SiteListView, SiteCreateView,\
                  SiteUpdateView, site_delete,\
                  SiteUserListView, SiteUserCreateView,\
                  SiteUserUpdateView
from accounts.api_views import SiteList, CompanyList, CompanyDetail
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = format_suffix_patterns(patterns('accounts.api_views',
    url(r'^api/sites/$', SiteList.as_view(), name='api-site-list'),
    url(r'^api/companies/$', CompanyList.as_view(), name='api-company-list'),
    url(r'^api/companies/(?P<pk>[0-9]+)[/]?$', CompanyDetail.as_view(),
        name='api-company-details'),
), allowed=['jsonp', 'json', 'html'])
