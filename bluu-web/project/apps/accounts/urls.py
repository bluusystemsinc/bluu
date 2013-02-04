from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from registration.views import activate
from .forms import RegistrationForm, EmailAuthenticationForm
from . import views

urlpatterns = patterns('',
    url(
        regex=r'^users/$', 
        view=views.BluuUserListView.as_view(),
        name='bluuuser-list'
    ),
    url(
        regex=r'^users/add/$',
        view=views.BluuUserCreateView.as_view(),
        name='bluuuser-add'
    ),
    url(
        regex=r'^users/(?P<pk>\d+)/edit/$',
        view=views.BluuUserUpdateView.as_view(),
        name='bluuuser-edit'
    ),

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
       views.register,
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
       login_required(views.AccountUpdateView.as_view()),
       name='account_edit'),
   url('^(?P<pk>\d+)/delete/$',
       views.AccountDeleteView.as_view(),
       name="account_delete"),
   #url(r'^done/$', "accounts.views.fb_done", name='dsa_done'),
   #url(r'^error/$', "accounts.views.fb_error", name='dsa_error'),
   url('^profile/new',
       login_required(views.UserProfileCreateView.as_view()),
       name="profiles_create_profile"),
   url('^profile',
       login_required(views.UserProfileUpdateView.as_view()),
       name="profiles_edit_profile"),
   url(r'^login/$',
        auth_views.login,
        {'template_name': 'registration/login.html',
        'authentication_form': EmailAuthenticationForm},
        name='auth_login'),
   (r'', include('registration.auth_urls')),
)
