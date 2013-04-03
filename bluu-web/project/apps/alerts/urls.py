from django.conf.urls import patterns, url, include

from . import views


urlpatterns = patterns('',
    url(r'^(?P<site_pk>\d+)/alerts/$',
        views.AlertsConfigurationView.as_view(),
        name='alert_list'),
)
