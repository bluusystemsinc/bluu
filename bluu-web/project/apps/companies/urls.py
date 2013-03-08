from django.conf.urls import patterns, url, include
from . import views


urlpatterns = patterns('',
    url(r'^$', views.CompanyListView.as_view(), name='company_list'),
    url(r'^add/$', views.CompanyCreateView.as_view(), name='company_add'),
    url(r'^(?P<pk>\d+)/edit/$',
            views.CompanyUpdateView.as_view(), name='company_edit'),
    url(r'^delete/(?P<pk>\d+)/$', views.company_delete,
        name='company_delete'),
    url(r'^(?P<company_pk>\d+)/access/$',
            views.CompanyAccessListView.as_view(), name='company_access_list'),
    url(r'^(?P<company_pk>\d+)/sites/$',
            views.CompanySiteListView.as_view(), name='company_site_list'),
    #url(r'^(?P<company_pk>\d+)/sites/add/$',
    #        views.CompanySiteCreateView.as_view(), name='company_site_add'),
    url(r'^delete/(?P<pk>\d+)/$', views.company_delete,
        name='company_delete'),
    url(r'^', include('companies.ajax_urls')),
)

