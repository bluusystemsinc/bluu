from django.conf.urls import patterns, url, include
from django.conf import settings
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

js_info_dict = {
            #'packages':('photos', 'theme')
        }

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^$', TemplateView.as_view(template_name="base.html"), name="dashboard"),
    #(r'^accounts/', include('registration.backends.default.urls')),
    (r'^accounts/', include('accounts.urls')),
    (r'^companies/', include('companies.urls')),
    (r'^sites/', include('bluusites.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),

    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/sites/', include('bluusites.api_urls', namespace='sites')),
    url(r'^api/companies/', include('companies.api_urls', namespace='companies')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
