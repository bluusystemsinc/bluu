from __future__ import unicode_literals
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import (Http404, HttpResponse)

from rest_framework.response import Response
from rest_framework import (generics, serializers, status)

from devices.models import Device, Status
from devices.signals import data_received
from bluusites.models import BluuSite
from utils.misc import get_client_ip


class DeviceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        exclude = (id,)
        depth = 1


class DeviceStatusCreateView(generics.CreateAPIView):
    serializer_class = DeviceStatusSerializer

    def create(self, request, *args, **kwargs):
        """
        Stores a message from a specific device.

        Sample command line call:
        curl -i -X POST -H "Content-Type: application/json" \
                -H "Accept: application/json" \
                -d '{"action":false, "battery":true, "data":0, "input1":false,\
                     "input2":false, "input3":false, "input4":false,\
                     "signal":80, "supervisory":false, "tamper":false,\
                     "timestamp":"2013-03-29T13:05:47"}'\
                -u username:password \
                http://localhost:8000/v1/sites/<site_id>/\
                                              devices/<device_serial>/statuses/

        """
        site_slug = self.kwargs.get('site_slug', None)
        bluusite = get_object_or_404(BluuSite, slug=site_slug)
        serial = self.kwargs.get('device_slug', None)
        device = get_object_or_404(Device, bluusite=bluusite, serial=serial)

        # Permissions check has to be called here and not as a dispatch 
        # decorator because of defered user authentication in DRF.
        # DRF authenticates user inside it's dispatch.
        has_permissions = False
        perms = ['bluusites.browse_devices', 'bluusites.change_device']

        # check global perms
        has_permissions = all(request.user.has_perm(perm) for perm in perms)
        # if no permission granted then try object perms
        if not has_permissions:
            has_permissions = all(request.user.has_perm(perm, self.object) \
                                                            for perm in perms)

        if not has_permissions:
            return HttpResponse(status=403)

        data = request.DATA.copy()
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
            return Response(data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SiteHeartBeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = BluuSite
        fields = ('last_seen',)


class SiteHeartBeatView(generics.UpdateAPIView):
    model = BluuSite
    slug_url_kwarg = 'site_slug'
    serializer_class = SiteHeartBeatSerializer

    def update(self, request, *args, **kwargs):
        """
        Updates site's last_seen to the time equal to the heart beat message 
        arrival.

        Sample command line call:
        curl -i -X PUT -H "Accept: application/json" \
            -H "Content-Type: application/json" \
            -d '{"last_seen": "2013-03-29T10:10:18.580701"}' \
            -u username:password http://127.0.0.1:8000/v1/sites/<site_id>/
        """
        self.object = None
        try:
            self.object = self.get_object()
        except Http404:
            return HttpResponse(status=404)

        # Permissions check has to be called here and not as a dispatch 
        # decorator because of defered user authentication in DRF.
        # DRF authenticates user inside it's dispatch.
        has_permissions = False
        perm = 'bluusites.browse_devices'

        # check global perms
        has_permissions = request.user.has_perm(perm)
        # if no permission granted then try object perms
        if not has_permissions:
            has_permissions = request.user.has_perm(perm, self.object)

        if not has_permissions:
            return HttpResponse(status=403)

        serializer = self.get_serializer(self.object, data=request.DATA)
        if serializer.is_valid():
            # we don't want to set last seen to timestamp from site
            # instead we're interested in real last seen - so it's now()
            self.object.last_seen = datetime.now()
            self.object.save()
            success_status_code = status.HTTP_200_OK
            return Response(serializer.data, status=success_status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

