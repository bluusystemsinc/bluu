from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^companies/$', views.CompanyListView.as_view(), name='company-list'),
    url(r'^companies/add/$', views.CompanyCreateView.as_view(), name='company-add'),
    url(r'^companies/(?P<pk>\d+)/edit/$',
            views.CompanyUpdateView.as_view(), name='company-edit'),
    url(r'^companies/(?P<pk>\d+)/access/$',
            views.CompanyAccessManagementView.as_view(), name='company-access'),
    url(r'^companies/(?P<company_pk>\d+)/sites/$',
            views.CompanySiteListView.as_view(), name='company-site-list'),
    url(r'^companies/(?P<company_pk>\d+)/sites/add/$',
            views.CompanySiteCreateView.as_view(), name='company-site-add'),
    url(r'^companies/delete/(?P<pk>\d+)/$', views.company_delete,
        name='company-delete'),
)

