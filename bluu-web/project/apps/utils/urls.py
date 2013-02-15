from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^$', views.WorkInProgress.as_view(), name='work_in_progress'),
) 
