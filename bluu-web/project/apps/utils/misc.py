import json
import contextlib
import datetime
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
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)


class BluuMessage:
    """
    Simple wrapper for EmailMessage class
    """
    def __init__(self, subject, body, to):
        self.msg = EmailMessage(subject, body, to=[to])
        #self.msg.content_subtype = 'html'

    def send(self):
        return self.msg.send()


@contextlib.contextmanager
def mock_now(dt_value):
    """Context manager for mocking out datetime.now() in unit tests.

    Example:
    with mock_now(datetime.datetime(2011, 2, 3, 10, 11)):
    assert datetime.datetime.now() == datetime.datetime(2011, 2, 3, 10, 11)

    """

    class MockDateTime(datetime.datetime):
        @classmethod
        def now(cls):
            # Create a copy of dt_value.
            return datetime.datetime(
                dt_value.year, dt_value.month, dt_value.day,
                dt_value.hour, dt_value.minute, dt_value.second, dt_value.microsecond,
                dt_value.tzinfo
            )
    real_datetime = datetime.datetime
    datetime.datetime = MockDateTime
    try:
        yield datetime.datetime
    finally:
        datetime.datetime = real_datetime
