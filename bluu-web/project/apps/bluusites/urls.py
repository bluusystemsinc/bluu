from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^sites/$', views.SiteListView.as_view(), name='site-list'),
    url(r'^sites/add/$', views.SiteCreateView.as_view(), name='site-add'),
    url(r'^sites/(?P<pk>\d+)/$',\
            views.SiteUpdateView.as_view(), name='site-edit'),
    url(r'^sites/(?P<pk>\d+)/access/$',\
            views.SiteAccessManagementView.as_view(), name='site-access'),
    url(r'^sites/(?P<pk>\d+)/delete/$', views.site_delete, name='site-delete'),
)

