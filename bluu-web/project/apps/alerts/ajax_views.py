from __future__ import unicode_literals

from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from rest_framework.response import Response
from rest_framework import (serializers, status, permissions, generics)

from bluusites.models import BluuSite, Room
from devices.models import DeviceType
from .models import (UserAlertDevice, UserAlertConfig, UserAlertScaleConfig,
                     UserAlertRoom, UserAlertScale)


class UserAlertConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAlertConfig
        fields = ('user', 'device_type', 'alert', 'duration', 'unit', 
                  'email_notification', 'text_notification')


class UserAlertScaleConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAlertScaleConfig
        fields = ('user', 'device_type', 'alert', 'weight',
                  'email_notification', 'text_notification')


class UserAlertDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAlertDevice
        fields = ('user', 'device', 'alert', 'duration', 'unit', 
                  'email_notification', 'text_notification')


class UserAlertRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAlertRoom
        fields = ('user', 'room', 'alert', 'duration', 'unit', 
                  'email_notification', 'text_notification')


class UserAlertScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAlertScale
        fields = ('user', 'device', 'alert', 'weight',
                  'email_notification', 'text_notification')


class UserAlertConfigSetView(generics.GenericAPIView):
    """
    Set alert configuration for user
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_site(self, pk):
        try:
            return BluuSite.objects.get(pk=pk)
        except BluuSite.DoesNotExist:
            raise Http404

    def get_object(self, bluusite, data):
        try:
            return UserAlertConfig.objects.get(
                                            bluusite=bluusite,
                                            user=data.get('user'),
                                            device_type=data.get('device_type'),
                                            alert=data.get('alert'))
        except UserAlertConfig.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        """
        Create a new UserAlertConfig
        """
        site = self.get_site(pk)

        self.object = None
        try:
            self.object = self.get_object(site, request.DATA)
        except Http404:
            success_status_code = status.HTTP_201_CREATED
        else:
            success_status_code = status.HTTP_200_OK

        serializer = UserAlertConfigSerializer(self.object, data=request.DATA)
        if serializer.is_valid():
            serializer.object.bluusite = site
            serializer.save()
            return Response(serializer.data, status=success_status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAlertScaleConfigSetView(generics.GenericAPIView):
    """
    Set scale alert configuration for user
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_site(self, pk):
        try:
            return BluuSite.objects.get(pk=pk)
        except BluuSite.DoesNotExist:
            raise Http404

    def get_object(self, bluusite, data):
        try:
            return UserAlertScaleConfig.objects.get(
                                            bluusite=bluusite,
                                            user=data.get('user'),
                                            device_type=data.get('device_type'),
                                            alert=data.get('alert'))
        except UserAlertScaleConfig.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        """
        Create a new UserAlertWeightConfig
        """
        site = self.get_site(pk)

        self.object = None
        try:
            self.object = self.get_object(site, request.DATA)
        except Http404:
            success_status_code = status.HTTP_201_CREATED
        else:
            success_status_code = status.HTTP_200_OK

        serializer = UserAlertScaleConfigSerializer(self.object,
                                                    data=request.DATA)
        if serializer.is_valid():
            serializer.object.bluusite = site
            serializer.save()
            return Response(serializer.data, status=success_status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAlertDeviceSetView(generics.GenericAPIView):
    """
    Set alert for user for specific device
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_site(self, pk):
        try:
            return BluuSite.objects.get(pk=pk)
        except BluuSite.DoesNotExist:
            raise Http404

    def get_object(self, data):
        try:
            return UserAlertDevice.objects.get(user=data.get('user'),
                                               device=data.get('device'),
                                               alert=data.get('alert'))
        except UserAlertDevice.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        """
        Create or delete UserAlertDevice depending on checkbox state
        """
        self.object = None
        try:
            self.object = self.get_object(request.DATA)
        except Http404:
            success_status_code = status.HTTP_201_CREATED
        else:
            if not request.DATA.get('checked', False):
                self.object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            success_status_code = status.HTTP_200_OK

        serializer = UserAlertDeviceSerializer(self.object, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=success_status_code)
 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAlertRoomSetView(generics.GenericAPIView):
    """
    Set alert for user for specific room
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_site(self, pk):
        try:
            return BluuSite.objects.get(pk=pk)
        except BluuSite.DoesNotExist:
            raise Http404

    def get_object(self, data):
        try:
            return UserAlertRoom.objects.get(user=data.get('user'),
                                             room=data.get('room'),
                                             alert=data.get('alert'))
        except UserAlertRoom.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        """
        Create or delete UserAlertRoom depending on checkbox state
        """
        room = Room.objects.get(pk=request.DATA.get('room'))
        if not room.device_set.filter(device_type__name=DeviceType.MOTION).exists():
            return Response({'room': ['No devices in this room']}, status=status.HTTP_400_BAD_REQUEST)

        self.object = None
        try:
            self.object = self.get_object(request.DATA)
        except Http404:
            success_status_code = status.HTTP_201_CREATED
        else:
            if not request.DATA.get('checked', False):
                self.object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            success_status_code = status.HTTP_200_OK

        serializer = UserAlertRoomSerializer(self.object, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=success_status_code)
 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAlertScaleSetView(generics.GenericAPIView):
    """
    Set alert for user for scale device
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_site(self, pk):
        try:
            return BluuSite.objects.get(pk=pk)
        except BluuSite.DoesNotExist:
            raise Http404

    def get_object(self, data):
        try:
            return UserAlertScale.objects.get(user=data.get('user'),
                                               device=data.get('device'),
                                               alert=data.get('alert'))
        except UserAlertScale.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        """
        Create or delete UserAlertDevice depending on checkbox state
        """
        self.object = None
        try:
            self.object = self.get_object(request.DATA)
        except Http404:
            success_status_code = status.HTTP_201_CREATED
        else:
            if not request.DATA.get('checked', False):
                self.object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            success_status_code = status.HTTP_200_OK

        serializer = UserAlertScaleSerializer(self.object, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=success_status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
