import os
import random
import datetime
from django.db import models
from django.conf import settings
from django.utils.http import int_to_base36
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from registration.models import SHA1_RE

class InvitationKeyManager(models.Manager):
    def get_key(self, invitation_key):
        """
        Return InvitationKey, or None if it doesn't (or shouldn't) exist.
        """
        # Don't bother hitting database if invitation_key doesn't match pattern.
        if not SHA1_RE.search(invitation_key):
            return None
        
        try:
            key = self.get(key=invitation_key)
        except self.model.DoesNotExist:
            return None
        
        return key
        
    def is_key_valid(self, invitation_key):
        """
        Check if an ``InvitationKey`` is valid or not, returning a boolean,
        ``True`` if the key is valid.
        """
        invitation_key = self.get_key(invitation_key)
        return invitation_key and invitation_key.is_usable()

    def create_invitation(self, user):
        """
        Create an ``InvitationKey`` and returns it.
        
        The key for the ``InvitationKey`` will be a SHA1 hash, generated 
        from a combination of the ``User``'s username and a random salt.
        """
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        key = sha_constructor("%s%s%s" % (datetime.datetime.now(), salt, user.username)).hexdigest()
        return self.create(from_user=user, key=key)

    def delete_expired_keys(self):
        for key in self.all():
            if key.key_expired():
                key.delete()


class InvitationKey(models.Model):
    key = models.CharField(_('invitation key'), max_length=40)
    date_invited = models.DateTimeField(_('date invited'), 
                                        default=datetime.datetime.now)
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                  related_name='invitations_sent')
    registrant = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, 
                                  related_name='invitations_used')
    
    objects = InvitationKeyManager()
    
    def __unicode__(self):
        return u"Invitation from %s on %s" % (self.from_user.username, self.date_invited)
    
    def is_usable(self):
        """
        Return whether this key is still valid for registering a new user.        
        """
        return self.registrant is None and not self.key_expired()
    
    def key_expired(self):
        """
        Determine whether this ``InvitationKey`` has expired, returning 
        a boolean -- ``True`` if the key has expired.
        
        The date the key has been created is incremented by the number of days 
        specified in the setting ``ACCOUNT_INVITATION_DAYS`` (which should be 
        the number of days after invite during which a user is allowed to
        create their account); if the result is less than or equal to the 
        current date, the key has expired and this method returns ``True``.
        
        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_INVITATION_DAYS)
        return self.date_invited + expiration_date <= datetime.datetime.now()
    key_expired.boolean = True
    
    def mark_used(self, registrant):
        """
        Note that this key has been used to register a new user.
        """
        self.registrant = registrant
        self.save()
        
    def send_to(self, email):
        """
        Send an invitation email to ``email``.
        """
        current_site = Site.objects.get_current()
        
        subject = render_to_string('invitation/invitation_email_subject.txt',
                                   { 'site': current_site, 
                                     'invitation_key': self })
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        
        message = render_to_string('invitation/invitation_email.txt',
                                   { 'invitation_key': self,
                                     'expiration_days': settings.ACCOUNT_INVITATION_DAYS,
                                     'site': current_site })
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        
class InvitationUser(models.Model):
    inviter = models.ForeignKey(settings.AUTH_USER_MODEL, unique=True)
    invitations_remaining = models.IntegerField()

    def __unicode__(self):
        return u"InvitationUser for %s" % self.inviter.username

    
def user_post_save(sender, instance, created, **kwargs):
    """Create InvitationUser for user when User is created."""
    if created:
        invitation_user = InvitationUser()
        invitation_user.inviter = instance
        invitation_user.save()

models.signals.post_save.connect(user_post_save, sender=settings.AUTH_USER_MODEL)

