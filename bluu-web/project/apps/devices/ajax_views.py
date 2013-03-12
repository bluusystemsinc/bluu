from __future__ import unicode_literals

from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import Group
from django.template import Context
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import (login_required, permission_required)
from django.template.loader import get_template
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

import django_filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import generics
from rest_framework.parsers import JSONParser
from django_datatables_view.base_datatable_view import BaseDatatableView
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_groups_with_perms, get_objects_for_user


from grontextual.models import UserObjectGroup
from accounts.models import BluuUser
from companies.models import Company
from companies.serializers import CompanyAccessSerializer,\
        CompanyAccessGroupsSerializer

from bluusites.models import BluuSite
from .models import Device, Status


class DeviceListJson(BaseDatatableView):
    """
    Returns list of devices assigned to a site.
    It's intended to work with Jquery datatable.
    """

    # Defines column names that will be used in sorting.
    # Order is important and should be the same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['', 'serial']

    def get_site(self, pk):
        return get_object_or_404(BluuSite, pk=pk)

    def filter_queryset(self, qs):
        q = self.request.GET.get('sSearch', None)
        if q is not None:
            return qs.filter(Q(serial__istartswith=q))
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        self.bluusite = self.get_site(kwargs.get('site_pk'))

        qs = Device.objects.filter(bluusite=self.bluusite)
        # number of records before filtering
        total_records = qs.count()
        qs = self.filter_queryset(qs)
        # number of records after filtering
        total_display_records = qs.count()
        qs = self.ordering(qs)
        qs = self.paging(qs)

        # prepare output data
        aaData = self.prepare_results(qs)

        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }

        return ret

    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []

        try:
            no = int(self.request.GET.get('iDisplayStart', 0)) + 1
        except (ValueError, TypeError):
            no = 0

        for device in qs:
            actions = '<a href="{0}">{1}</a> <a href="{2}" onclick="return confirm(\'{3}\')">{4}</a>'.format(
                    reverse('devices:device_edit', args=(device.bluusite_id, device.pk,)), _('Manage'),
                    reverse('devices:device_delete', args=(device.bluusite_id, device.pk,)), 
                    _('Are you sure you want delete this device?'),
                    _('Delete'))

            #actions = '<a href="{0}">{1}</a>'.format(
            #        reverse('devices:device_edit',
            #                args=(device.bluusite_id, device.pk,)),
            #        _('Manage'))

            json_data.append(
                {
                    "device":{
                        "no": no,
                        "name": device.name,
                        "serial": device.serial,
                        "device_type": device.device_type.name,
                        "room": device.room.name,
                        "actions": actions
                    }
                }
            )
            no += 1
        return json_data

    @method_decorator(permission_required_or_403(
        'bluusites.change_bluusite',
        (BluuSite, 'pk', 'site_pk'),
        accept_global_perms=True))
    @method_decorator(permission_required_or_403(
        'bluusites.browse_devices',
        (BluuSite, 'pk', 'site_pk'),
        accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceListJson, self).dispatch(*args, **kwargs)


class DeviceHistoryListJson(BaseDatatableView):
    """
    Returns list of device statuses.
    It's intended to work with Jquery datatable.
    """

    # Defines column names that will be used in sorting.
    # Order is important and should be the same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['', '-timestamp']

    def get_site(self, pk):
        return get_object_or_404(BluuSite, pk=pk)

    def get_device(self, pk):
        return get_object_or_404(Device, pk=pk)

    def filter_queryset(self, qs):
        q = self.request.GET.get('sSearch', None)
        if q is not None:
            return qs.filter(Q(action__istartswith=q))
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        self.bluusite = self.get_site(kwargs.get('site_pk'))
        self.device = self.get_device(kwargs.get('pk'))

        qs = Status.objects.filter(device=self.device)
        # number of records before filtering
        total_records = qs.count()
        qs = self.filter_queryset(qs)
        # number of records after filtering
        total_display_records = qs.count()
        qs = self.ordering(qs)
        qs = self.paging(qs)

        # prepare output data
        aaData = self.prepare_results(qs)

        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }

        return ret

    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []

        try:
            no = int(self.request.GET.get('iDisplayStart', 0)) + 1
        except (ValueError, TypeError):
            no = 0

        for status in qs:
            #actions = '<a href="{0}">{1}</a> <a href="{2}" onclick="return confirm(\'{3}\')">{4}</a>'.format(
            #        reverse('devices:device_edit', args=(device.bluusite_id, device.pk,)), _('Manage'),
            #        reverse('devices:device_delete', args=(device.bluusite_id, device.pk,)), 
            #        _('Are you sure you want delete this device?'),
            #        _('Delete'))

            #actions = '<a href="{0}">{1}</a>'.format(
            #        reverse('devices:device_edit',
            #                args=(device.bluusite_id, device.pk,)),
            #        _('Manage'))

            json_data.append(
                {
                    "device":{
                        "no": no,
                        "last_seen": status.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "action": status.action,
                        "battery_low": status.battery,
                        "tamper": status.tamper,
                    }
                }
            )
            no += 1
        return json_data

    @method_decorator(permission_required_or_403(
        'bluusites.change_bluusite',
        (BluuSite, 'pk', 'site_pk'),
        accept_global_perms=True))
    @method_decorator(permission_required_or_403(
        'bluusites.browse_devices',
        (BluuSite, 'pk', 'site_pk'),
        accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceHistoryListJson, self).dispatch(*args, **kwargs)


class DeviceStatusCreateView(generics.CreateAPIView):
    model = Status
