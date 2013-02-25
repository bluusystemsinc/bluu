from django.conf.urls import *
from django.views.generic.base import TemplateView

from registration.forms import RegistrationFormTermsOfService
from .views import invited_register

urlpatterns = patterns('',
    url(r'^invite/complete/$',
        TemplateView.as_view(),
        {'template': 'invitation/invitation_complete.html'},
        name='invitation_complete'),
#    url(r'^invite/$',
#                invite,
#                name='invitation_invite'),
    url(r'^invited/(?P<invitation_key>\w+)/$', 
        invited_register,
        { 'backend': 'invitations.backends.InvitationBackend' },
        name='invited_register'),
)
