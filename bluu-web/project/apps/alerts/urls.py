from django.conf.urls import patterns, url, include

from . import views


urlpatterns = patterns('',
    url(r'^$', views.AlertsConfigurationView.as_view(), name='site_list'),
)
