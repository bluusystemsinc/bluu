from django.conf import settings
from accounts.models import BluuUser
from rest_framework.authtoken.models import Token


def run():
    """
    Generate auth tokens for webservice users
    """
    for user in BluuUser.objects.filter(username__startswith=\
                                        settings.WEBSERVICE_USERNAME_PREFIX):
        Token.objects.get_or_create(user=user)
    print 'Tokens generated!'
