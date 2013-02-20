from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import UpdateView, CreateView, DetailView,\
                                 DeleteView, ListView, TemplateView
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from guardian.decorators import permission_required_or_403
from guardian.mixins import PermissionRequiredMixin as GPermissionRequiredMixin

from grontextual.shortcuts import get_objects_for_user
from accounts.forms import BluuUserForm
from accounts.models import BluuUser
from .forms import SiteInvitationForm
from .models import BluuSite
from .forms import SiteForm


class SensorListView(TemplateView):
    template_name = "bluusites/site_list.html"

    @method_decorator(login_required)
    @method_decorator(permission_required('bluusites.browse_bluusites'))
    def dispatch(self, *args, **kwargs):
        return super(SensorListView, self).dispatch(*args, **kwargs)


class SensorCreateView(CreateView):
    model = BluuSite
    template_name = "bluusites/site_create.html"
    form_class = SiteForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(SensorCreateView, self).get_form_kwargs(**kwargs)
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super(SensorCreateView, self).form_valid(form)
        #_create_groups_for_bluusite(self.object)
        messages.success(self.request, _('Sensor added'))
        return response

    @method_decorator(login_required)
    @method_decorator(permission_required('bluusites.add_bluusite'))
    def dispatch(self, *args, **kwargs):
        return super(SensorCreateView, self).dispatch(*args, **kwargs)


class SensorUpdateView(UpdateView):
    model = BluuSite
    template_name = "bluusites/site_update.html"
    form_class = SiteForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(SensorUpdateView, self).get_form_kwargs(**kwargs)
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super(SensorUpdateView, self).form_valid(form)
        messages.success(self.request, _('Sensor changed'))
        return response

    @method_decorator(login_required)
    @method_decorator(permission_required('bluusites.change_bluusite'))
    def dispatch(self, *args, **kwargs):
        return super(SensorUpdateView, self).dispatch(*args, **kwargs)

