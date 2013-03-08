from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import UpdateView, CreateView, DetailView,\
                                 DeleteView, ListView, TemplateView
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import resolve

from guardian.decorators import (permission_required, 
                                 permission_required_or_403)
from guardian.mixins import PermissionRequiredMixin as GPermissionRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView

from grontextual.shortcuts import get_objects_for_user
from accounts.forms import BluuUserForm
from accounts.models import BluuUser
from bluusites.models import BluuSite

from .forms import DeviceForm
from .models import (Device, DeviceType, Status)


class DeviceListView(TemplateView):
    template_name = "devices/device_list.html"

    def get_object(self, queryset=None):
        pk = self.kwargs.get('site_pk', None)
        return get_object_or_404(BluuSite, pk=pk)

    def get_context_data(self, **kwargs):
        bluusite = self.get_object()
        device_types = DeviceType.objects.filter(device__isnull=False).distinct()

        return {
            'params': kwargs,
            'bluusite': bluusite,
            'device_types': device_types,
        }

    @method_decorator(permission_required(
                        'bluusites.change_bluusite',
                        (BluuSite, 'pk', 'site_pk'),
                        accept_global_perms=True))
    @method_decorator(permission_required(
                        'bluusites.browse_devices',
                        (BluuSite, 'pk', 'site_pk'),
                        accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceListView, self).dispatch(*args, **kwargs)


class DeviceListView_classic(TemplateView):
    template_name = "devices/device_list_classic.html"

    def get_object(self, queryset=None):
        pk = self.kwargs.get('site_pk', None)
        return get_object_or_404(BluuSite, pk=pk)

    def get_context_data(self, **kwargs):
        bluusite = self.get_object()
        return {
            'params': kwargs,
            'bluusite': bluusite,
        }

    @method_decorator(permission_required(
                        'bluusites.change_bluusite',
                        (BluuSite, 'pk', 'site_pk'),
                        accept_global_perms=True))
    @method_decorator(permission_required(
                        'bluusites.browse_devices',
                        (BluuSite, 'pk', 'site_pk'),
                        accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceListView, self).dispatch(*args, **kwargs)


class DeviceCreateView(CreateView):
    model = Device
    template_name = "devices/device_create.html"
    form_class = DeviceForm
    pk_url_kwarg = 'site_pk'

    def get_site(self):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return get_object_or_404(BluuSite, pk=pk)

    def get_context_data(self, **kwargs):
        kwargs = super(DeviceCreateView, self).get_context_data(**kwargs)
        kwargs.update({'bluusite': self.get_site()})
        return kwargs

    def get_form_kwargs(self, **kwargs):
        kwargs = super(DeviceCreateView, self).get_form_kwargs(**kwargs)
        kwargs['user'] = self.request.user
        kwargs['bluusite'] = self.get_site()
        return kwargs

    def form_valid(self, form):
        response = super(DeviceCreateView, self).form_valid(form)
        messages.success(self.request, _('Device added'))
        return response

    @method_decorator(login_required)
    @method_decorator(permission_required('bluusites.add_device',
                                          (BluuSite, 'pk', 'site_pk'),
                                          accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceCreateView, self).dispatch(*args, **kwargs)


class DeviceUpdateView(UpdateView):
    model = Device
    template_name = "devices/device_update.html"
    form_class = DeviceForm
    pk_url_kwarg = 'pk'

    def get_site(self):
        pk = self.kwargs.get('site_pk', None)
        return get_object_or_404(BluuSite, pk=int(pk))

    def get_context_data(self, **kwargs):
        kwargs = super(DeviceUpdateView, self).get_context_data(**kwargs)
        kwargs.update({'bluusite': self.get_site()})
        return kwargs

    def get_form_kwargs(self, **kwargs):
        kwargs = super(DeviceUpdateView, self).get_form_kwargs(**kwargs)
        kwargs['bluusite'] = self.get_site()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super(DeviceUpdateView, self).form_valid(form)
        messages.success(self.request, _('Device changed'))
        return response

    @method_decorator(login_required)
    @method_decorator(permission_required('bluusites.change_device',
                                          (BluuSite, 'pk', 'site_pk'),
                                          accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceUpdateView, self).dispatch(*args, **kwargs)


@permission_required('bluusites.delete_device',
                     (BluuSite, 'pk', 'site_pk'))
def device_delete(request, site_pk, pk):
    obj = get_object_or_404(Device, pk=pk)
    obj.delete()
    messages.success(request, _('Device deleted'))
    site_pk = int(site_pk)
    namespace = resolve(request.path).namespace
    return redirect('{}:device_list'.format(namespace), site_pk=site_pk)


class DeviceHistoryListView(TemplateView):
    template_name = "devices/device_history_list.html"

    def get_context_data(self, **kwargs):
        site_pk = self.kwargs.get('site_pk', None)
        pk = self.kwargs.get('pk', None)
        bluusite = get_object_or_404(BluuSite, pk=site_pk)
        device = get_object_or_404(Device, pk=pk)

        return {
            'params': kwargs,
            'bluusite': bluusite,
            'device': device,
        }

    @method_decorator(permission_required(
                        'bluusites.change_bluusite',
                        (BluuSite, 'pk', 'site_pk'),
                        accept_global_perms=True))
    @method_decorator(permission_required(
                        'bluusites.browse_devices',
                        (BluuSite, 'pk', 'site_pk'),
                        accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(DeviceHistoryListView, self).dispatch(*args, **kwargs)


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
    order_columns = ['', 'timestamp']

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
                        "last_seen": status.device.last_seen.strftime("%Y-%m-%d %H:%M:%S"),
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


