from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^sites/$', views.SiteListView.as_view(), name='site_list'),
    url(r'^sites/add/$', views.SiteCreateView.as_view(), name='site_add'),
    url(r'^sites/(?P<pk>\d+)/$',\
            views.SiteUpdateView.as_view(), name='site_edit'),
    url(r'^sites/(?P<pk>\d+)/access/$',\
            views.SiteAccessManagementView.as_view(), name='site_access'),
    url(r'^sites/(?P<pk>\d+)/delete/$', views.site_delete, name='site_delete'),
)

