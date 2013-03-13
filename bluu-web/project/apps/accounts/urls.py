from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from registration.views import activate
from .forms import RegistrationForm, EmailAuthenticationForm
from . import views

urlpatterns = patterns('',
    url(regex=r'^users/$', 
        view=views.BluuUserListView.as_view(),
        name='bluuuser_list'
    ),
    url(regex=r'^users\.json/$', 
        view=views.BluuUserListJson.as_view(),
        name='bluuuser_list_json'
    ),
    url(regex=r'^users/add/$',
        view=views.BluuUserCreateView.as_view(),
        name='bluuuser_add'
    ),
    url(regex=r'^users/(?P<username>[\w.@+-]+)/edit/$',
        view=views.BluuUserUpdateView.as_view(),
        name='bluuuser_edit'
    ),
    url(r'^users/(?P<username>[\w.@+-]+)/delete/$',
        views.bluuuser_delete,
        name='bluuuser_delete'),
    url(regex=r'^users/(?P<username>[\w.@+-]+)/sites/$',
        view=views.BluuUserSitesView.as_view(),
        name='bluuuser_sites'
    ),
    url(regex=r'^users/(?P<username>[\w.@+-]+)/companies/$',
        view=views.BluuUserCompaniesView.as_view(),
        name='bluuuser_companies'
    ),
    url(r'^password/$',
        login_required(views.AccountUpdateView.as_view()),
        name='account_edit'),
    url(r'^login/$',
        auth_views.login,
        {'template_name': 'registration/login.html',
        'authentication_form': EmailAuthenticationForm},
        name='auth_login'),
    (r'', include('invitations.urls')),
    (r'', include('registration.auth_urls')),
)
