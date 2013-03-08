from __future__ import unicode_literals

from rest_framework import generics
from devices.models import Status

class DeviceStatusCreateView(generics.CreateAPIView):
    model = Status
