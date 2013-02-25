from django.conf import settings
from django.shortcuts import (render, redirect)
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext as _

from registration.views import register as registration_register
from registration.backends import get_backend

from accounts.forms import RegistrationForm
from .models import InvitationKey
from .forms import InvitationKeyForm
from .backends import InvitationBackend

is_key_valid = InvitationKey.objects.is_key_valid
get_key = InvitationKey.objects.get_key


#def invited(request, invitation_key=None, extra_context=None):
#    if getattr(settings, 'INVITE_MODE', False):
#        if invitation_key and is_key_valid(invitation_key):
#            return HttpResponseRedirect(reverse('registration_register'))
#            template_name = 'invitations/invited.html'
#        else:
#            template_name = 'invitation/wrong_invitation_key.html'
#        extra_context = extra_context is not None and extra_context.copy() or {}
#        extra_context.update({'invitation_key': invitation_key})
#        return render(request, template_name, extra_context)
#    else:
#        return HttpResponseRedirect(reverse('registration_register'))
#

def invited_register(request, backend, invitation_key, success_url=None,
            form_class=RegistrationForm,
            disallowed_url='registration_disallowed',
            post_registration_redirect=None,
            template_name='registration/registration_form.html',
            wrong_template_name='invitations/wrong_invitation_key.html',
            extra_context=None):
    extra_context = extra_context is not None and extra_context.copy() or {}
    if getattr(settings, 'INVITE_MODE', False):
        if invitation_key:
            extra_context.update({'invitation_key': invitation_key})
            # if key is valid
            if is_key_valid(invitation_key):
                key_object = get_key(invitation_key)
                # if email is assigned to an access content_object 
                # but not user - if user is assigned then this invitation has
                # already been accepted
                if ((key_object.content_object and \
                        key_object.content_object.email) and not \
                        key_object.content_object.user):

                    extra_context.update(
                            {'email': key_object.content_object.email})

                    if request.POST:
                        backend = get_backend(backend)
                        form = form_class(data=request.POST, files=request.FILES)
                        if form.is_valid():
                            new_user = backend.register(request, **extra_context)
                            to, args, kwargs = backend.post_registration_redirect(
                                    request,
                                    new_user,
                                    invitation_key=invitation_key)

                            messages.success(request, _("You've been registered and logged in."))                            
                            return redirect(to, *args, **kwargs)
                    else:
                        form = form_class()
                    extra_context.update({'form': form})

                    return render(request, template_name, extra_context)

                #return registration_register(request, backend, success_url,
                #                            form_class, disallowed_url,
                #                            template_name, extra_context)
            extra_context.update({'invalid_key': True})
        else:
            extra_context.update({'no_key': True})
        return render(request, wrong_template_name, extra_context)
    else:
        return registration_register(request, backend, success_url, form_class,
                                     disallowed_url, template_name, extra_context)

def invite(request, success_url=None,
            form_class=InvitationKeyForm,
            template_name='invitation/invitation_form.html',
            extra_context=None):
    extra_context = extra_context is not None and extra_context.copy() or {}
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            invitation = InvitationKey.objects.create_invitation(request.user)
            invitation.send_to(form.cleaned_data["email"])
            # success_url needs to be dynamically generated here; setting a
            # a default value using reverse() will cause circular-import
            # problems with the default URLConf for this application, which
            # imports this file.
            return HttpResponseRedirect(success_url or reverse('invitation_complete'))
    else:
        form = form_class()
    extra_context.update({
            'form': form,
        })
    return render(request, template_name, extra_context)
invite = login_required(invite)
