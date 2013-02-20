from django.conf.urls import patterns, url
from . import views
from utils.views import WorkInProgressView


urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/sensors/$',\
            WorkInProgressView.as_view(), name='site_sensors'),
)

