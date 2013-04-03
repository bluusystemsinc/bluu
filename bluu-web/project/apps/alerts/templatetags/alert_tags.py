import datetime
import re

from django import template
from django.template import Library
from django.utils.translation import ugettext as _

from devices.models import Device
from ..models import UserAlert

register = Library()


@register.inclusion_tag('alerts/_alerts_of_type.html', takes_context=True)
def alerts_of_type(context, bluusite, device_type):
    devices = Device.objects.filter(bluusite=bluusite, device_type=device_type)
    alerts = UserAlert.ALERT_CHOICES

    # get alerts for current device type
    # for each alert render all devices of this type in this site
    # for each device set value of its current alert setting (if set)

    context.update({'device_type': device_type,
                    'devices': devices})
    return context

def do_alerts_of_type(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        bluusite, device_type = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(_("%(tag_name)s tag requires exactly two arguments") % {'tag_name': token.contents.split()[0]})
    return AlertsOfTypeNode(bluusite, device_type)

class AlertsOfTypeNode(template.Node):
    def __init__(self, bluusite, device_type):
        self.bluusite = template.Variable(bluusite)
        self.device_type = template.Variable(device_type)

    def render(self, context):
        # get alerts for current device type
        # for each alert render all devices of this type in this site
        # for each device set value of its current alert setting (if set)


        t = template.loader.get_template('small_fragment.html')

        ctx = template.Context({'var': obj}, autoescape=context.autoescape)
        return t.render(ctx)
        #except template.VariableDoesNotExist:
        #    return ''

