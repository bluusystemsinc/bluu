from django.conf.urls import patterns, url
from . import views
from utils.views import WorkInProgressView


urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/devices/$',\
            WorkInProgressView.as_view(), name='site_devices'),
)

