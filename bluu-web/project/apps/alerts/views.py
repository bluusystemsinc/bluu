from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import (UpdateView, CreateView, ListView,
                                  TemplateView)
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

from guardian.decorators import permission_required

from accounts.forms import BluuUserForm
from accounts.models import BluuUser
from bluusites.forms import SiteInvitationForm, RoomForm
from bluusites.models import BluuSite, Room
from bluusites.forms import SiteForm

from devices.models import DeviceType


class AlertsConfigurationView(TemplateView):
    template_name = "alerts/alerts.html"
    pk_url_kwarg = 'site_pk'

    def get_object(self, queryset=None):
        site_pk = self.kwargs.get(self.pk_url_kwarg, None)
        return get_object_or_404(BluuSite, pk=site_pk)

    def get_context_data(self, **kwargs):
        bluusite = self.get_object()
        device_types = DeviceType.objects.filter(
                                    device__isnull=False,
                                    device__bluusite=bluusite).distinct()

        return {
            'params': kwargs,
            'bluusite': bluusite,
            'device_types': device_types,
        }

    @method_decorator(login_required)
    @method_decorator(permission_required('bluusites.browse_bluusites', 
                                          accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(AlertsConfigurationView, self).dispatch(*args, **kwargs)

