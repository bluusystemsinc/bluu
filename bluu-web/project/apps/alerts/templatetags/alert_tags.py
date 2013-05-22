import datetime
import re

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.template import Library
from django.utils.translation import ugettext as _
from django.forms.models import modelformset_factory
from django.db.models import Count

from devices.models import Device, DeviceType
from bluusites.models import Room
from ..forms import (AlertDeviceForm, DurationForm, NotificationForm,
                     WeightForm)
from ..models import (UserAlertDevice, UserAlertConfig, UserAlertRoom,
                      UserAlertScale, UserAlertScaleConfig)

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
        tag_name, user, bluusite, device_type, alert = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(_("%(tag_name)s tag requires exactly three arguments") % {'tag_name': token.contents.split()[0]})
    return AlertBoxNode(user, bluusite, device_type, alert)


class AlertBoxNode(template.Node):
    def __init__(self, user, bluusite, device_type, alert):
        self.user_var = template.Variable(user)
        self.bluusite_var = template.Variable(bluusite)
        self.device_type_var = template.Variable(device_type)
        self.alert_var = template.Variable(alert)

    def render(self, context):
        # for each alert render all devices of this type in this site
        # for each device set value of its current alert setting (if set)
        request = context['request']
        user = self.user_var.resolve(context)
        bluusite = self.bluusite_var.resolve(context)
        device_type = self.device_type_var.resolve(context)
        alert = self.alert_var.resolve(context)

        devices = Device.objects.filter(bluusite=bluusite,
                                        device_type=device_type)

        if device_type.name == DeviceType.SCALE:
            cform = WeightForm
            cinitial = {'weight': 0}
            config_class = UserAlertScaleConfig
        else:
            cform = DurationForm
            cinitial = {'duration': 0, 'unit': 'h'}
            config_class = UserAlertConfig

        try:
            instance = config_class.objects.get(
                            bluusite=bluusite.pk,
                            user=user.pk,
                            device_type=device_type.pk,
                            alert=alert.pk)
            cform = cform(instance=instance)
            nform = NotificationForm(instance=instance)
        except ObjectDoesNotExist:
            cform = cform(initial=cinitial)
            nform = NotificationForm(initial={'text_notification': False,
                                              'email_notification': False})

        t = template.loader.get_template('alerts/_conf_{0}_{1}.html'.\
                   format(device_type.name.lower(), alert.alert_type.lower()))

        ctx = template.Context({'request': request,
                                'bluusite': bluusite,
                                'alert': alert,
                                'user': request.user,
                                'cform': cform,
                                'nform': nform,
                                'device_type': device_type,
                                'devices': devices},
                               autoescape=context.autoescape)

        return t.render(ctx)


@register.tag(name="devices_for_alert")
def do_devices_for_alert(parser, token):
    try:
        tag_name, user, bluusite, device_type, alert = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(_("%(tag_name)s tag requires exactly three arguments") % {'tag_name': token.contents.split()[0]})
    return AlertDeviceNode(user, bluusite, device_type, alert)


class AlertDeviceNode(template.Node):

    def __init__(self, user, bluusite, device_type, alert):
        self.user_var = template.Variable(user)
        self.bluusite_var = template.Variable(bluusite)
        self.device_type_var = template.Variable(device_type)
        self.alert_var = template.Variable(alert)

    def render(self, context):
        # for each alert render all devices of this type in this site
        # for each device set value of its current alert setting (if set)
        request = context['request']
        user = self.user_var.resolve(context)
        bluusite = self.bluusite_var.resolve(context)
        device_type = self.device_type_var.resolve(context)
        alert = self.alert_var.resolve(context)

        if device_type.name == DeviceType.MOTION:
            forms = []
            # get all rooms that have devices of type MOTION
            rooms = Room.objects.filter(bluusite=bluusite,
                                        device__device_type=device_type)
            for room in rooms:
                try:
                    UserAlertRoom.objects.get(user=user.pk,
                                              room=room.pk,
                                              alert=alert.pk)
                    selected = True
                except UserAlertRoom.DoesNotExist:
                    selected = False
                
                forms.append({'selected': selected,
                              'room': room,
                              'name': room.name})

            t = template.loader.get_template('alerts/conf_alert_room.html')

            ctx = template.Context({'alert': alert,
                                    'user': request.user,
                                    'forms': forms,
                                    'device_type': device_type,
                                    },
                                   autoescape=context.autoescape)
        else:
            forms = []
            devices = Device.objects.filter(bluusite=bluusite,
                                            device_type=device_type)

            if device_type.name == DeviceType.SCALE:
                for device in devices:
                    try:
                        UserAlertScale.objects.get(user=user.pk,
                                                   device=device.pk,
                                                   alert=alert.pk)
                        selected = True
                    except UserAlertScale.DoesNotExist:
                        selected = False

                    forms.append({'selected': selected,
                                  'device': device,
                                  'name': device.name})

                t = template.loader.get_template('alerts/conf_alert_scale.html')
            else:
                for device in devices:
                    try:
                        UserAlertDevice.objects.get(user=user.pk,
                                                    device=device.pk,
                                                    alert=alert.pk)
                        selected = True
                    except UserAlertDevice.DoesNotExist:
                        selected = False

                    forms.append({'selected': selected,
                                  'device': device,
                                  'name': device.name})

                t = template.loader.get_template('alerts/conf_alert_device.html')

            ctx = template.Context({'alert': alert,
                                    'user': request.user,
                                    'forms': forms,
                                    'device_type': device_type,
                                    },
                                   autoescape=context.autoescape)
        return t.render(ctx)

