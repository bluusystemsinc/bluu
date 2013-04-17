# -*- coding: utf-8 -*-
from django.http import Http404

from rest_framework.response import Response
from rest_framework import (serializers, status, permissions, generics)

from bluusites.models import BluuSite
from .models import (UserAlertDevice, UserAlertConfig)


class UserAlertConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAlertConfig
        fields = ('user', 'device_type', 'alert', 'duration', 'unit', 
                  'email_notification', 'text_notification')


class UserAlertDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAlertDevice
        fields = ('user', 'device', 'alert', 'duration', 'unit', 
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
        Create a new UserAlertDevice
        """
        self.object = None
        try:
            self.object = self.get_object(request.DATA)
        except Http404:
            success_status_code = status.HTTP_201_CREATED
        else:
            success_status_code = status.HTTP_200_OK

        serializer = UserAlertDeviceSerializer(self.object, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=success_status_code)
 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

