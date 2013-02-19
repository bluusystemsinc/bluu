from django.conf.urls import patterns, url
from . import views
from utils.views import WorkInProgressView


urlpatterns = patterns('',
    url(r'^$', views.SiteListView.as_view(), name='site_list'),
    url(r'^add/$', views.SiteCreateView.as_view(), name='site_add'),
    url(r'^(?P<pk>\d+)/$',\
            views.SiteUpdateView.as_view(), name='site_edit'),
    #url(r'^(?P<pk>\d+)/access/$',\
    #        views.SiteAccessManagementView.as_view(), name='site_access'),
    url(r'^(?P<pk>\d+)/access/$',\
            views.SiteAccessListView.as_view(), name='site_access'),
    url(r'^(?P<pk>\d+)/sensors/$',\
            WorkInProgressView.as_view(), name='site_sensors'),
    url(r'^(?P<pk>\d+)/delete/$', views.site_delete, name='site_delete'),
)

