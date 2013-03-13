from django.conf.urls import patterns, url, include
from django.conf import settings
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.contrib.auth import views as auth_views
from accounts.forms import EmailAuthenticationForm
from accounts.views import bluu_login

js_info_dict = {
            #'packages':('photos', 'theme')
        }

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^$',
        bluu_login,
        {'template_name': 'registration/login.html',
        'authentication_form': EmailAuthenticationForm},
        name='auth_login'),
    (r'^dashboard/', include('dashboard.urls')),
    #url(r'^$', TemplateView.as_view(template_name="base.html"), name="homepage"),
    #(r'^accounts/', include('registration.backends.default.urls')),
    (r'^accounts/', include('accounts.urls')),
    (r'^companies/', include('companies.urls')),
    (r'^sites/', include('bluusites.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    (r'^v1/', include('apiv1.urls', namespace='v1')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
