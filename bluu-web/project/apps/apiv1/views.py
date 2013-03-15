from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from rest_framework.response import Response
from rest_framework import (generics, serializers, status)
from guardian.decorators import permission_required_or_403

from devices.models import Device, Status
from devices.signals import data_received
from bluusites.models import BluuSite
from utils.misc import get_client_ip

#class SDeviceStatusSerializer(serializers.Serializer):
#    serial = serializers.CharField(max_length=200)
#    data = serializers.IntegerField()
#    signal = serializers.IntegerField()
#    action = serializers.BooleanField()
#    battery = serializers.BooleanField()
#    input1 = serializers.BooleanField()
#    input2 = serializers.BooleanField()
#    input3 = serializers.BooleanField()
#    input4 = serializers.BooleanField()
#    supervisory = serializers.BooleanField()
#    tamper = serializers.BooleanField()
#    timestamp = serializers.DateTimeField()
#
#    def restore_object(self, attrs, instance=None):
#        serial = attrs.pop('serial')
#        device = get_object_or_404(Device, serial=serial)
#        attrs['device'] = device
#
#        if instance is not None:
#            instance.update(attrs)
#        return Status(**attrs)
#

class DeviceStatusSerializer(serializers.ModelSerializer):
    serial = serializers.CharField(max_length=200)
    class Meta:
        model = Status
        exclude = (id,)
        depth = 1

    def to_native(self, obj):
        """
        Serialize objects -> primitives.
        """
        ret = self._dict_class()
        ret.fields = {}

        for field_name, field in self.fields.items():
            if field_name == 'serial':
                continue
            field.initialize(parent=self, field_name=field_name)
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field
        return ret


class DeviceStatusCreateView(generics.CreateAPIView):
    #model = Status
    serializer_class = DeviceStatusSerializer

    def create(self, request, *args, **kwargs):
        """
        Checks whether device belongs to the site specified in url
        """
        site_slug = self.kwargs.get('site_slug', None)
        bluusite = get_object_or_404(BluuSite, slug=site_slug)

        data = request.DATA.copy()
        serial = data.get('serial')
        data.pop('serial')
        device = get_object_or_404(Device, serial=serial, bluusite=bluusite)
        data['device'] = device

        serializer = self.get_serializer(data=data, files=request.FILES,
                                         partial=True)
        if serializer.is_valid():
            serializer.object.device = device
            self.pre_save(serializer.object)
            self.object = serializer.save()
            self.post_save(self.object, created=True)

            # send signal with caller ip address
            data_received.send(sender=Status,
                               instance=serializer.object,
                               ip_address=get_client_ip(request))
            headers = self.get_success_headers(data)
            # revert data to be returned to contain serial instead of device
            data.pop('device')
            data['serial'] = serial
            return Response(data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @method_decorator(permission_required_or_403(
        'bluusites.browse_devices',
        (BluuSite, 'slug', 'site_slug'),
        accept_global_perms=True))
    @method_decorator(permission_required_or_403(
        'bluusites.change_device',
        (BluuSite, 'slug', 'site_slug'),
        accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceStatusCreateView, self).dispatch(*args, **kwargs)


