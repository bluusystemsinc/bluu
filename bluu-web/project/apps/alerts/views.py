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
from .forms import SiteInvitationForm, RoomForm
from .models import BluuSite, Room
from .forms import SiteForm


class AlertsConfigurationView(TemplateView):
    template_name = "alerts/alerts.html"

    @method_decorator(login_required)
    @method_decorator(permission_required('bluusites.browse_bluusites', 
                                          accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        sites = self.request.user.can_see_sites(perm='bluusites.change_bluusite')
        site = sites.get('bluusite', None)
        if site is not None:
            return redirect('site_edit', pk=site.pk)

        return super(AlertsConfigurationView, self).dispatch(*args, **kwargs)

