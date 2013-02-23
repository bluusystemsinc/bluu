from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import UpdateView, CreateView, DetailView,\
                                 DeleteView, ListView, TemplateView
#from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from guardian.decorators import permission_required
from guardian.mixins import PermissionRequiredMixin as GPermissionRequiredMixin

from grontextual.shortcuts import get_objects_for_user
from accounts.forms import BluuUserForm
from accounts.models import BluuUser
from bluusites.models import BluuSite

from .forms import DeviceForm


class DeviceListView(TemplateView):
    template_name = "devices/device_list.html"

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

