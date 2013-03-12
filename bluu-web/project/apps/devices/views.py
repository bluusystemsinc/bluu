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
        device_types = DeviceType.objects.filter(device__isnull=False, device__bluusite=bluusite).distinct()

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

