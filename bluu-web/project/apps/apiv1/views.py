from __future__ import unicode_literals

from django.shortcuts import get_object_or_404

from rest_framework import generics, serializers

from devices.models import Device, Status
from bluusites.models import BluuSite

class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device


class DeviceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        exclude = (id,)
        depth = 1

class DeviceStatusCreateView(generics.CreateAPIView):
    #model = Status
    serializer_class = DeviceStatusSerializer

    def create(self, request, *args, **kwargs):
        """
        Checks whether device belongs to the site specified in url
        """
        site_slug = self.kwargs.get('site_slug', None)
        bluusite = get_object_or_404(BluuSite, slug=site_slug)

        device_pk = self.kwargs.get('device_pk', None)
        device = get_object_or_404(Device, pk=device_pk, bluusite=bluusite)

        #if pk is not None:
        #    queryset = queryset.filter(pk=pk)
        ## Next, try looking up by slug.
        #elif slug is not None:
        #    slug_field = self.get_slug_field()
        #    queryset = queryset.filter(**{slug_field: slug})
        ## If none of those are defined, it's an error.
        #else:
        #    raise AttributeError("Generic detail view %s must be called with "
        #                         "either an object pk or a slug."
        #                          % self.__class__.__name__) 


        return super(DeviceStatusCreateView, self).create(request, *args,
                                                          **kwargs)
