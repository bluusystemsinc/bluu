from django.contrib.auth import authenticate
from django.contrib.auth import login
try:
    from django.contrib.auth import get_user_model
except ImportError: # django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()

from registration.backends.simple import SimpleBackend
from registration import signals
from accounts.forms import RegistrationForm
from .models import InvitationKey

class InvitationBackend(SimpleBackend):

    def register(self, request, **kwargs):
        """
        Create and immediately log in a new user.
        
        """
        invitation_key = kwargs.get('invitation_key', None)
        if request.POST:
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                # nadanie praw
                #grupy - grupa "User" - moze sie przypisuje sama na sygnale
                #email ustawic!
                try:
                    key = InvitationKey.get(key=invitation_key)
                    #for access in key... 
                    # wszystkie acccesy trezba sprawdzic - nie tylko z tej invitki

                except InvitationKey.DoesNotExist:
                    pass

                user.save()
        else:
            form = RegistrationForm()

        username, email, password = kwargs['username'], kwargs['email'], kwargs['password1']
        User.objects.create_user(username, email, password)
        
        # authenticate() always has to be called before login(), and
        # will return the user we just created.
        new_user = authenticate(username=user.username, password=user.password)
        login(request, new_user)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     invitation_key=invitation_key,
                                     request=request)
        return new_user



    def post_registration_redirect(self, request, user, *args, **kwargs):
        """
        Return the name of the URL to redirect to after successful
        user registration.

        """
        invitation_key = request.REQUEST.get('invitation_key')
        key = InvitationKey.objects.get_key(invitation_key)
        if key:
            key.mark_used(user)

        return ('registration_complete', (), {})
