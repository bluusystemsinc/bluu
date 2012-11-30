from django.db import transaction
from django.contrib.sites.models import Site
from django.contrib.sites.models import RequestSite
from django.contrib.auth.models import User
from registration import signals
from registration.models import RegistrationProfile
from registration.backends.default import DefaultBackend

def create_inactive_user(username, email, password,
                         first_name, last_name,
                         site, send_email=True):
    """
    Create a new, inactive ``User``, generate a
    ``RegistrationProfile`` and email its activation key to the
    ``User``, returning the new ``User``.

    By default, an activation email will be sent to the new
    user. To disable this, pass ``send_email=False``.
    
    """
    new_user = User.objects.create_user(username, email, password)
    new_user.is_active = False
    new_user.first_name = first_name
    new_user.last_name = last_name
    new_user.save()

    registration_profile = RegistrationProfile.objects.create_profile(new_user)

    if send_email:
        registration_profile.send_activation_email(site)

    return new_user
create_inactive_user = transaction.commit_on_success(create_inactive_user)


class PhotoBackend(DefaultBackend):
    def register(self, request, **kwargs):
        username, email, password, first_name, last_name = \
                kwargs['username'], kwargs['email'], kwargs['password1'],\
                kwargs['first_name'], kwargs['last_name']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = create_inactive_user(username, email, password, 
                                        first_name, last_name, site)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user


