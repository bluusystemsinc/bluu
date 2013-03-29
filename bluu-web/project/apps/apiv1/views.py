from __future__ import unicode_literals
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.http import (Http404, HttpResponse)
from django.views.decorators.csrf import csrf_exempt

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
    serializer_class = DeviceStatusSerializer

    def create(self, request, *args, **kwargs):
        """
        Checks whether device belongs to the site specified in url
        """
        site_slug = self.kwargs.get('site_slug', None)
        bluusite = get_object_or_404(BluuSite, slug=site_slug)
        serial = self.kwargs.get('device_slug', None)
        device = get_object_or_404(Device, bluusite=bluusite, slug=serial)

        data = request.DATA.copy()
        #serial = data.get('serial')
        #data.pop('serial')
        #device = get_object_or_404(Device, serial=serial, bluusite=bluusite)
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
            #data['serial'] = serial
            return Response(data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#    @method_decorator(permission_required_or_403(
#        'bluusites.browse_devices',
#        (BluuSite, 'slug', 'site_slug'),
#        accept_global_perms=True))
#    @method_decorator(permission_required_or_403(
#        'bluusites.change_device',
#        (BluuSite, 'slug', 'site_slug'),
#        accept_global_perms=True))
#    @csrf_exempt
#    def dispatch(self, *args, **kwargs):
#        return super(DeviceStatusCreateView, self).dispatch(*args, **kwargs)


class SiteHeartBeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = BluuSite
        fields = ('last_seen',)


class SiteHeartBeatView(generics.UpdateAPIView):
    model = BluuSite
    slug_url_kwarg = 'site_slug'
    serializer_class = SiteHeartBeatSerializer

    def update(self, request, *args, **kwargs):
        self.object = None
        try:
            self.object = self.get_object()
        except Http404:
            return HttpResponse(status=404)

        serializer = self.get_serializer(self.object, data=request.DATA)
        if serializer.is_valid():
            # we don't want to set last seen to timestamp from site
            # instead we're interested in real last seen - so it's now()
            self.object.last_seen = datetime.now()
            self.object.save()
            success_status_code = status.HTTP_200_OK
            return Response(serializer.data, status=success_status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #@csrf_exempt
    #@method_decorator(permission_required_or_403(
    #    'bluusites.browse_devices',
    #    (BluuSite, 'slug', 'site_slug'),
    #    accept_global_perms=True))
    #def dispatch(self, *args, **kwargs):
    #    return super(SiteHeartBeatView, self).dispatch(*args, **kwargs)


