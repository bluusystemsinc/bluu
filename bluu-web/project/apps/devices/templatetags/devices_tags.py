import datetime
import re

from django import template
from django.template import Library

from ..models import Device

register = Library()

@register.inclusion_tag('devices/_devices_of_type.html', takes_context=True)
def devices_of_type(context, bluusite, device_type):
    devices = Device.objects.filter(bluusite=bluusite, device_type=device_type)

    context.update({'device_type': device_type,
                    'devices': devices})
    return context
