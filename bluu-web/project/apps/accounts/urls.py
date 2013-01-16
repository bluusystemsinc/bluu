from django.conf.urls.defaults import *
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from registration.views import activate
from views import register, UserProfileUpdateView,\
                  UserProfileCreateView, AccountUpdateView,\
                  AccountDeleteView, CompanyListView, CompanyCreateView,\
                  CompanyUpdateView, company_delete,\
                  CompanyAccessManagementView,\
                  SiteListView, SiteCreateView,\
                  SiteUpdateView, site_delete,\
                  SiteUserListView, SiteUserCreateView,\
                  SiteUserUpdateView, SiteAccessManagementView
from forms import RegistrationForm, EmailAuthenticationForm
from django.views.generic import TemplateView
from accounts.api_views import SiteList, CompanyList, CompanyDetail

try:
    from django.core.urlresolvers import reverse_lazy
except ImportError, e:
    from django.core.urlresolvers import reverse
    from django.utils.functional import lazy
    reverse_lazy = lazy(reverse, str)

urlpatterns = patterns('accounts.views',
    url(r'^companies/$', CompanyListView.as_view(), name='company-list'),
    url(r'^companies/add/$', CompanyCreateView.as_view(), name='company-add'),
    url(r'^companies/(?P<pk>\d+)/$',
            CompanyUpdateView.as_view(), name='company-edit'),
    url(r'^companies/(?P<pk>\d+)/access/$',
            CompanyAccessManagementView.as_view(), name='company-access'),
    url(r'^companies/delete/(?P<pk>\d+)/$', 'company_delete',
        name='company-delete'),

    url(r'^sites/$', SiteListView.as_view(), name='site-list'),
    url(r'^sites/add/$', SiteCreateView.as_view(), name='site-add'),
    url(r'^sites/(?P<pk>\d+)/$', SiteUpdateView.as_view(), name='site-edit'),
    url(r'^sites/(?P<pk>\d+)/access/$', SiteAccessManagementView.as_view(), name='site-access'),
    url(r'^sites/(?P<pk>\d+)/delete/$', 'site_delete',
        name='site-delete'),
    #url(r'^sites/(?P<pk>\d+)/access/$', SiteUserListView.as_view(), name='site-users'),
    #url(r'^sites/(?P<pk>\d+)/access/add/$', SiteUserCreateView.as_view(), name='site-user-add'),
    #url(r'^sites/(?P<pk>\d+)/access/(?P<upk>\d+)/$', SiteUserUpdateView.as_view(), name='site-user-edit'),
    #url(r'^sites/(?P<site_id>\d+)/access/(?P<pk>\d+)/delete/$', 'site_user_delete', name='site-user-delete'),
)

urlpatterns += patterns('',
           url(r'^activate/complete/$',
               TemplateView.as_view(
                   template_name='registration/activation_complete.html'),
               name='registration_activation_complete'),
           # Activation keys get matched by \w+ instead of the more specific
           # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
           # that way it can return a sensible "invalid key" message instead of a
           # confusing 404.
           url(r'^activate/(?P<activation_key>\w+)/$',
               activate,
               {'backend': 'accounts.registration_backend.PhotoBackend'},
               name='registration_activate'),
           url(r'^register/$',
               register,
               {'backend': 'accounts.registration_backend.PhotoBackend',
                'form_class': RegistrationForm},
               name='registration_register'),
           url(r'^register/complete/$',
               TemplateView.as_view(
                   template_name='registration/registration_complete.html'),
               name='registration_complete'),
           url(r'^register/closed/$',
               TemplateView.as_view(
                   template_name='registration/registration_closed.html'),
               name='registration_disallowed'),
           url(r'^password/$',
               login_required(AccountUpdateView.as_view()),
               name='account_edit'),
           url('^(?P<pk>\d+)/delete/$',
               AccountDeleteView.as_view(),
               name="account_delete"),
           #url(r'^done/$', "accounts.views.fb_done", name='dsa_done'),
           #url(r'^error/$', "accounts.views.fb_error", name='dsa_error'),
           url('^profile/new',
               login_required(UserProfileCreateView.as_view()),
               name="profiles_create_profile"),
           url('^profile',
               login_required(UserProfileUpdateView.as_view()),
               name="profiles_edit_profile"),
           url(r'^login/$',
                auth_views.login,
                {'template_name': 'registration/login.html',
                'authentication_form': EmailAuthenticationForm},
                name='auth_login'),
           (r'', include('registration.auth_urls')),
           )
