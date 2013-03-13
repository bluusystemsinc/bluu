from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^$', views.DashboardView.as_view(),name='dashboard'),
    url(r'^(?P<site_slug>[\w.@+-]+)/$', views.BluuSiteDashboardView.as_view(),
        name='bluusite_dashboard'),
)
