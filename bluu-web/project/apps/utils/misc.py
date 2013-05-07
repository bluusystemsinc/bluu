import json
from datetime import datetime
from time import mktime
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def remove_orphaned_obj_perms(sender, instance, **kwargs):
    from guardian.models import UserObjectPermission
    from guardian.models import GroupObjectPermission
    from grontextual.models import UserObjectGroup

    filters = Q(content_type=ContentType.objects.get_for_model(instance),
        object_pk=instance.pk)
    UserObjectGroup.objects.filter(filters).delete()
    UserObjectPermission.objects.filter(filters).delete()
    GroupObjectPermission.objects.filter(filters).delete()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',', 1)[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class DateTimeEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)


class BluuMessage:
    """
    Simple wrapper for EmailMessage class
    """
    def __init__(self, subject, body, to):
        self.msg = EmailMessage(subject, body, to)
        #self.msg.content_subtype = 'html'

    def send(self):
        return self.msg.send()
