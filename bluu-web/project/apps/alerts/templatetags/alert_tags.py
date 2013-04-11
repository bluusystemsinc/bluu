import datetime
import re

from django import template
from django.template import Library
from django.utils.translation import ugettext as _

from devices.models import Device
from ..models import UserAlert
from ..forms import DurationForm

register = Library()


@register.inclusion_tag('alerts/_alerts_for_device_type.html', takes_context=True)
def alerts_for_device_type(context, bluusite, device_type):

    # get alerts for current device type
    alerts = device_type.alert_set.all()

    context.update({'device_type': device_type,
                    'alerts': alerts,
                    })
    return context


@register.tag(name="alertbox")
def do_alertbox_for_alert(parser, token):
    try:
        tag_name, bluusite, device_type, alert = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(_("%(tag_name)s tag requires exactly three arguments") % {'tag_name': token.contents.split()[0]})
    return AlertBoxNode(bluusite, device_type, alert)

class AlertBoxNode(template.Node):
    def __init__(self, bluusite, device_type, alert):
        self.bluusite_var = template.Variable(bluusite)
        self.device_type_var = template.Variable(device_type)
        self.alert_var = template.Variable(alert)

    def render(self, context):
        # for each alert render all devices of this type in this site
        # for each device set value of its current alert setting (if set)
        request = context['request']
        bluusite = self.bluusite_var.resolve(context)
        device_type = self.device_type_var.resolve(context)
        alert = self.alert_var.resolve(context)
        devices = Device.objects.filter(bluusite=bluusite,
                                        device_type=device_type)
        form = DurationForm(device_type=device_type, alert=alert,
                initial={'time': 0, 'unit': 's'}, prefix=alert.pk)

        t = template.loader.get_template('alerts/_conf_{0}_{1}.html'.\
                   format(device_type.name.lower(), alert.alert_type.lower()))

        ctx = template.Context({'alert': alert,
                                'user': request.user,
                                'form': form,
                                'device_type': device_type,
                                'devices': devices},
                               autoescape=context.autoescape)
        return t.render(ctx)
        #except template.VariableDoesNotExist:
        #    return ''

